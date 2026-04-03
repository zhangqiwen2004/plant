from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.matching.models import MatchRecord, MatchRequest, TagWeight
from apps.matching.seed_data import MATCH_RECORD_SEEDS, MATCH_REQUEST_SEEDS, TAG_WEIGHT_SEEDS
from apps.users.models import User


class Command(BaseCommand):
    help = '初始化匹配推荐种子数据'

    def add_arguments(self, parser):
        parser.add_argument('--refresh', action='store_true')

    def handle(self, *args, **options):
        refresh = options['refresh']
        self.stdout.write('开始初始化匹配数据...')

        self.users = {u.username: u for u in User.objects.all()}

        missing = self.validate_users()
        if missing:
            raise CommandError(f'缺少用户: {", ".join(sorted(missing))}')

        with transaction.atomic():
            if refresh:
                MatchRecord.objects.all().delete()
                MatchRequest.objects.all().delete()
                TagWeight.objects.all().delete()

            weight_count = self.seed_tag_weights()
            record_count = self.seed_match_records()
            request_count = self.seed_match_requests()

        self.stdout.write(
            self.style.SUCCESS(
                f'匹配数据初始化完成！tag_weights={weight_count},'
                f' match_records={record_count}, match_requests={request_count}'
            )
        )

    def validate_users(self):
        needed = set()
        for item in MATCH_RECORD_SEEDS:
            needed.add(item['user'])
            needed.add(item['matched_user'])
        for item in MATCH_REQUEST_SEEDS:
            needed.add(item['from_user'])
            needed.add(item['to_user'])
        return needed - set(self.users.keys())

    def seed_tag_weights(self):
        created_count = 0
        for item in TAG_WEIGHT_SEEDS:
            _, created = TagWeight.objects.get_or_create(
                tag_type=item['tag_type'],
                defaults={
                    'weight': item['weight'],
                    'description': item['description'],
                },
            )
            if created:
                created_count += 1
        return created_count

    def seed_match_records(self):
        created_count = 0
        for item in MATCH_RECORD_SEEDS:
            user = self.users[item['user']]
            matched_user = self.users[item['matched_user']]
            _, created = MatchRecord.objects.get_or_create(
                user=user,
                matched_user=matched_user,
                defaults={
                    'match_type': item['match_type'],
                    'similarity_score': item['similarity_score'],
                    'match_reason': item['match_reason'],
                    'matched_tags': item['matched_tags'],
                    'is_contacted': item.get('is_contacted', False),
                    'feedback': item.get('feedback'),
                    'feedback_comment': item.get('feedback_comment', ''),
                },
            )
            if created:
                created_count += 1
        return created_count

    def seed_match_requests(self):
        created_count = 0
        for item in MATCH_REQUEST_SEEDS:
            from_user = self.users[item['from_user']]
            to_user = self.users[item['to_user']]
            _, created = MatchRequest.objects.get_or_create(
                from_user=from_user,
                to_user=to_user,
                defaults={
                    'message': item['message'],
                    'status': item['status'],
                    'responded_at': timezone.now() if item['status'] == 'accepted' else None,
                },
            )
            if created:
                created_count += 1
        return created_count
