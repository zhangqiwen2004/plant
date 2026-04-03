from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.community.models import (
    Answer,
    AnswerLike,
    Comment,
    CommentLike,
    Post,
    PostLike,
    Question,
    Topic,
    TopicFollow,
)
from apps.community.seed_data import POST_SEEDS, QUESTION_SEEDS, TOPIC_FOLLOW_SEEDS
from apps.users.models import User


class Command(BaseCommand):
    help = '初始化社区种子数据'

    def add_arguments(self, parser):
        parser.add_argument('--refresh', action='store_true')

    def handle(self, *args, **options):
        refresh = options['refresh']
        self.stdout.write('开始初始化社区数据...')

        call_command('init_users')
        self.users = {user.username: user for user in User.objects.all()}
        self.topics = {topic.name: topic for topic in Topic.objects.all()}
        self.admin = self.users.get('admin')
        self.validate_reference_data()

        with transaction.atomic():
            if refresh:
                self.clear_community_data()

            follow_created = self.seed_topic_follows()
            post_stats = self.seed_posts(refresh=refresh)
            question_stats = self.seed_questions(refresh=refresh)
            self.sync_counters()

        self.stdout.write(
            self.style.SUCCESS(
                '社区数据初始化完成！'
                f' follows={follow_created},'
                f' posts_created={post_stats["created"]},'
                f' posts_updated={post_stats["updated"]},'
                f' comments_created={post_stats["comments"]},'
                f' post_likes_created={post_stats["post_likes"]},'
                f' comment_likes_created={post_stats["comment_likes"]},'
                f' questions_created={question_stats["created"]},'
                f' questions_updated={question_stats["updated"]},'
                f' answers_created={question_stats["answers"]},'
                f' answer_likes_created={question_stats["answer_likes"]}'
            )
        )

    def validate_reference_data(self):
        usernames = {'admin'}
        topics = set()

        for item in TOPIC_FOLLOW_SEEDS:
            topics.add(item['topic'])
            usernames.update(item['followers'])

        for item in POST_SEEDS:
            topics.add(item['topic'])
            usernames.add(item['author'])
            usernames.update(item.get('like_users', []))
            usernames.update(self.collect_comment_usernames(item.get('comments', [])))

        for item in QUESTION_SEEDS:
            usernames.add(item['author'])
            for answer in item.get('answers', []):
                usernames.add(answer['author'])
                usernames.update(answer.get('like_users', []))

        missing_users = sorted(username for username in usernames if username not in self.users)
        missing_topics = sorted(topic for topic in topics if topic not in self.topics)

        if missing_users or missing_topics:
            messages = []
            if missing_users:
                messages.append(f'缺少用户: {", ".join(missing_users)}')
            if missing_topics:
                messages.append(f'缺少话题: {", ".join(missing_topics)}')
            raise CommandError('；'.join(messages))

    def collect_comment_usernames(self, comments):
        usernames = set()
        for item in comments:
            usernames.add(item['author'])
            usernames.update(item.get('like_users', []))
            if item.get('reply_to'):
                usernames.add(item['reply_to'])
            usernames.update(self.collect_comment_usernames(item.get('replies', [])))
        return usernames

    def clear_community_data(self):
        TopicFollow.objects.all().delete()
        Post.objects.all().delete()
        Question.objects.all().delete()
        Topic.objects.update(post_count=0, follower_count=0)

    def seed_topic_follows(self):
        created_count = 0
        for item in TOPIC_FOLLOW_SEEDS:
            topic = self.topics[item['topic']]
            for username in item['followers']:
                _, created = TopicFollow.objects.get_or_create(
                    user=self.users[username],
                    topic=topic,
                )
                if created:
                    created_count += 1
        return created_count

    def seed_posts(self, refresh=False):
        stats = {
            'created': 0,
            'updated': 0,
            'comments': 0,
            'post_likes': 0,
            'comment_likes': 0,
        }

        for item in POST_SEEDS:
            author = self.users[item['author']]
            topic = self.topics[item['topic']]
            defaults = {
                'topic': topic,
                'content': item['content'],
                'images': [],
                'status': item['status'],
                'reviewer': self.admin if item['status'] == 'approved' else None,
                'review_comment': '种子内容初始化通过' if item['status'] == 'approved' else '',
                'reviewed_at': timezone.now() if item['status'] == 'approved' else None,
                'view_count': item['view_count'],
                'is_top': item['is_top'],
                'is_essence': item['is_essence'],
            }
            post, created = Post.objects.get_or_create(
                author=author,
                title=item['title'],
                defaults=defaults,
            )
            if created:
                stats['created'] += 1
            elif refresh and self.update_instance(post, defaults):
                stats['updated'] += 1

            stats['post_likes'] += self.seed_post_likes(post, item.get('like_users', []))
            comment_stats = self.seed_comment_tree_batch(post, item.get('comments', []))
            stats['comments'] += comment_stats['created']
            stats['comment_likes'] += comment_stats['likes']

        return stats

    def seed_post_likes(self, post, usernames):
        created_count = 0
        for username in usernames:
            _, created = PostLike.objects.get_or_create(user=self.users[username], post=post)
            if created:
                created_count += 1
        return created_count

    def seed_comment_tree_batch(self, post, comments):
        stats = {'created': 0, 'likes': 0}
        for item in comments:
            item_stats = self.seed_comment(post, item, parent=None)
            stats['created'] += item_stats['created']
            stats['likes'] += item_stats['likes']
        return stats

    def seed_comment(self, post, item, parent=None):
        author = self.users[item['author']]
        reply_to = self.users[item['reply_to']] if item.get('reply_to') else None
        comment, created = Comment.objects.get_or_create(
            post=post,
            author=author,
            parent=parent,
            reply_to=reply_to,
            content=item['content'],
        )

        stats = {
            'created': 1 if created else 0,
            'likes': self.seed_comment_likes(comment, item.get('like_users', [])),
        }

        for reply in item.get('replies', []):
            reply_stats = self.seed_comment(post, reply, parent=comment)
            stats['created'] += reply_stats['created']
            stats['likes'] += reply_stats['likes']

        return stats

    def seed_comment_likes(self, comment, usernames):
        created_count = 0
        for username in usernames:
            _, created = CommentLike.objects.get_or_create(
                user=self.users[username],
                comment=comment,
            )
            if created:
                created_count += 1
        return created_count

    def seed_questions(self, refresh=False):
        stats = {
            'created': 0,
            'updated': 0,
            'answers': 0,
            'answer_likes': 0,
        }

        for item in QUESTION_SEEDS:
            author = self.users[item['author']]
            defaults = {
                'content': item['content'],
                'images': [],
                'plant_type': item['plant_type'],
                'status': item['status'],
                'view_count': item['view_count'],
                'is_urgent': item['is_urgent'],
                'bounty': item['bounty'],
            }
            question, created = Question.objects.get_or_create(
                author=author,
                title=item['title'],
                defaults=defaults,
            )
            if created:
                stats['created'] += 1
            elif refresh and self.update_instance(question, defaults):
                stats['updated'] += 1

            answer_stats = self.seed_answers(question, item.get('answers', []), refresh=refresh)
            stats['answers'] += answer_stats['created']
            stats['answer_likes'] += answer_stats['likes']

        return stats

    def seed_answers(self, question, answers, refresh=False):
        stats = {'created': 0, 'likes': 0}
        for item in answers:
            author = self.users[item['author']]
            defaults = {
                'content': item['content'],
                'images': [],
                'is_accepted': item['is_accepted'],
            }
            answer, created = Answer.objects.get_or_create(
                question=question,
                author=author,
                defaults=defaults,
            )
            if created:
                stats['created'] += 1
            elif refresh:
                self.update_instance(answer, defaults)

            stats['likes'] += self.seed_answer_likes(answer, item.get('like_users', []))

        return stats

    def seed_answer_likes(self, answer, usernames):
        created_count = 0
        for username in usernames:
            _, created = AnswerLike.objects.get_or_create(
                user=self.users[username],
                answer=answer,
            )
            if created:
                created_count += 1
        return created_count

    def update_instance(self, instance, values):
        changed_fields = []
        for field_name, value in values.items():
            field = instance._meta.get_field(field_name)
            if field.is_relation and field.many_to_one:
                current_value = getattr(instance, f'{field_name}_id')
                target_value = value.pk if value is not None else None
            else:
                current_value = getattr(instance, field_name)
                target_value = value

            if current_value != target_value:
                setattr(instance, field_name, value)
                changed_fields.append(field_name)

        if changed_fields:
            instance.save(update_fields=changed_fields)
            return True
        return False

    def sync_counters(self):
        for topic in Topic.objects.all():
            post_count = topic.posts.count()
            follower_count = topic.followers.count()
            update_fields = []
            if topic.post_count != post_count:
                topic.post_count = post_count
                update_fields.append('post_count')
            if topic.follower_count != follower_count:
                topic.follower_count = follower_count
                update_fields.append('follower_count')
            if update_fields:
                topic.save(update_fields=update_fields)

        for post in Post.objects.all():
            like_count = post.likes.count()
            comment_count = post.comments.count()
            update_fields = []
            if post.like_count != like_count:
                post.like_count = like_count
                update_fields.append('like_count')
            if post.comment_count != comment_count:
                post.comment_count = comment_count
                update_fields.append('comment_count')
            if update_fields:
                post.save(update_fields=update_fields)

        for comment in Comment.objects.all():
            like_count = comment.likes.count()
            if comment.like_count != like_count:
                comment.like_count = like_count
                comment.save(update_fields=['like_count'])

        for question in Question.objects.all():
            answer_count = question.answers.count()
            update_fields = []
            if question.answer_count != answer_count:
                question.answer_count = answer_count
                update_fields.append('answer_count')
            if question.answers.filter(is_accepted=True).exists() and question.status != 'answered':
                question.status = 'answered'
                update_fields.append('status')
            if update_fields:
                question.save(update_fields=update_fields)

        for answer in Answer.objects.all():
            like_count = answer.likes.count()
            if answer.like_count != like_count:
                answer.like_count = like_count
                answer.save(update_fields=['like_count'])
