from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import F
from django.utils import timezone

from .models import (
    Topic, TopicFollow, Post, PostImage, PostLike, Comment, CommentLike,
    Question, QuestionImage, Answer, AnswerLike
)
from .serializers import (
    TopicSerializer, PostListSerializer, PostDetailSerializer, PostCreateSerializer,
    CommentSerializer, QuestionListSerializer, QuestionDetailSerializer,
    QuestionCreateSerializer, AnswerSerializer
)
from .pagination import CommunityPagination
from apps.analytics.activity_service import log_user_activity
from apps.users.notification_service import send_user_notification
from apps.users.permissions import IsAdmin, IsOwnerOrAdmin, IsOwnerOrReadOnly


class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    pagination_class = CommunityPagination
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'admin':
            return Topic.objects.all()
        return Topic.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [AllowAny()]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        topic = self.get_object()
        _, created = TopicFollow.objects.get_or_create(user=request.user, topic=topic)
        if created:
            Topic.objects.filter(pk=topic.pk).update(follower_count=F('follower_count') + 1)
            return Response({'message': '关注成功'})
        return Response({'message': '已关注'})
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        topic = self.get_object()
        deleted, _ = TopicFollow.objects.filter(user=request.user, topic=topic).delete()
        if deleted:
            Topic.objects.filter(pk=topic.pk).update(follower_count=F('follower_count') - 1)
            return Response({'message': '取消关注成功'})
        return Response({'message': '未关注'})


class PostViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = CommunityPagination
    filterset_fields = ['topic', 'author', 'status', 'is_top', 'is_essence']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count', 'like_count']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'admin':
            return Post.objects.all()
        if user.is_authenticated:
            return (Post.objects.filter(status='approved') | Post.objects.filter(author=user)).distinct()
        return Post.objects.filter(status='approved')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        if serializer.instance.topic:
            Topic.objects.filter(pk=serializer.instance.topic.pk).update(
                post_count=F('post_count') + 1
            )
        log_user_activity(
            self.request.user,
            'post',
            serializer.instance,
            {'status': serializer.instance.status, 'topic_id': serializer.instance.topic_id}
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Post.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        log_user_activity(request.user, 'view', instance, {'resource': 'post'})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        if instance.topic_id:
            topic = instance.topic
            topic.post_count = max(topic.post_count - 1, 0)
            topic.save(update_fields=['post_count'])
        instance.delete()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        _, created = PostLike.objects.get_or_create(user=request.user, post=post)
        if created:
            Post.objects.filter(pk=post.pk).update(like_count=F('like_count') + 1)
            if post.author != request.user:
                send_user_notification(
                    user=post.author,
                    notification_type='interaction',
                    title='收到新点赞',
                    content=f'{request.user.username} 赞了你的帖子《{post.title}》',
                    related_url=f'/posts/{post.id}'
                )
            log_user_activity(request.user, 'like', post, {'target': 'post'})
            return Response({'message': '点赞成功'})
        return Response({'message': '已点赞'})
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        deleted, _ = PostLike.objects.filter(user=request.user, post=post).delete()
        if deleted:
            Post.objects.filter(pk=post.pk).update(like_count=F('like_count') - 1)
            return Response({'message': '取消点赞成功'})
        return Response({'message': '未点赞'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def review(self, request, pk=None):
        post = self.get_object()
        action_type = request.data.get('action')
        comment = request.data.get('comment', '')
        
        if action_type == 'approve':
            post.status = 'approved'
        elif action_type == 'reject':
            post.status = 'rejected'
        else:
            return Response({'error': '无效操作'}, status=status.HTTP_400_BAD_REQUEST)
        
        post.reviewer = request.user
        post.review_comment = comment
        post.reviewed_at = timezone.now()
        post.save()
        
        send_user_notification(
            user=post.author,
            notification_type='system',
            title='帖子审核结果',
            content=f'您的帖子《{post.title}》已{"通过" if post.status == "approved" else "被拒绝"}审核。{comment}',
            related_url=f'/posts/{post.id}'
        )
        
        return Response({'message': '审核完成'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def set_top(self, request, pk=None):
        post = self.get_object()
        post.is_top = not post.is_top
        post.save()
        return Response({'message': f'{"设置" if post.is_top else "取消"}置顶成功', 'is_top': post.is_top})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def set_essence(self, request, pk=None):
        post = self.get_object()
        post.is_essence = not post.is_essence
        post.save()
        return Response({'message': f'{"设置" if post.is_essence else "取消"}精华成功', 'is_essence': post.is_essence})

    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    def stats(self, request):
        total = Post.objects.count()
        approved = Post.objects.filter(status='approved').count()
        pending = Post.objects.filter(status='pending').count()
        rejected = Post.objects.filter(status='rejected').count()
        top = Post.objects.filter(is_top=True).count()
        essence = Post.objects.filter(is_essence=True).count()
        return Response({
            'total': total,
            'approved': approved,
            'pending': pending,
            'rejected': rejected,
            'top': top,
            'essence': essence,
        })


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = CommunityPagination
    filterset_fields = ['post', 'author']
    search_fields = ['content', 'author__username', 'post__title']
    ordering_fields = ['created_at', 'like_count']
    
    def get_queryset(self):
        queryset = Comment.objects.select_related('post', 'author', 'reply_to')
        user = self.request.user
        if user.is_authenticated and user.role == 'admin' and self.request.query_params.get('flat') == '1':
            return queryset.order_by('-created_at')
        return queryset.filter(parent=None).order_by('-created_at')
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [AllowAny()]
    
    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        post = comment.post
        Post.objects.filter(pk=post.pk).update(comment_count=F('comment_count') + 1)
        log_user_activity(self.request.user, 'comment', comment, {'post_id': post.id})
        
        if post.author != self.request.user:
            send_user_notification(
                user=post.author,
                notification_type='interaction',
                title='收到新评论',
                content=f'{self.request.user.username} 评论了你的帖子《{post.title}》',
                related_url=f'/posts/{post.id}'
            )
        
        if comment.reply_to and comment.reply_to != self.request.user:
            send_user_notification(
                user=comment.reply_to,
                notification_type='interaction',
                title='收到新回复',
                content=f'{self.request.user.username} 回复了你的评论',
                related_url=f'/posts/{post.id}'
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        _, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        if created:
            Comment.objects.filter(pk=comment.pk).update(like_count=F('like_count') + 1)
            if comment.author != request.user:
                send_user_notification(
                    user=comment.author,
                    notification_type='interaction',
                    title='收到评论点赞',
                    content=f'{request.user.username} 赞了你在《{comment.post.title}》下的评论',
                    related_url=f'/posts/{comment.post.id}'
                )
            log_user_activity(request.user, 'like', comment, {'target': 'comment'})
            return Response({'message': '点赞成功'})
        return Response({'message': '已点赞'})

    def _count_comment_tree(self, comment):
        total = 1
        for reply in comment.replies.all():
            total += self._count_comment_tree(reply)
        return total

    def perform_destroy(self, instance):
        post = instance.post
        deleted_count = self._count_comment_tree(instance)
        instance.delete()
        post.comment_count = max(post.comment_count - deleted_count, 0)
        post.save(update_fields=['comment_count'])


class QuestionViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = CommunityPagination
    queryset = Question.objects.all()
    filterset_fields = ['author', 'status', 'plant_type', 'is_urgent']
    search_fields = ['title', 'content', 'plant_type']
    ordering_fields = ['created_at', 'view_count', 'answer_count']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return QuestionCreateSerializer
        if self.action == 'retrieve':
            return QuestionDetailSerializer
        return QuestionListSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'my_questions']:
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        log_user_activity(
            self.request.user,
            'question',
            serializer.instance,
            {'plant_type': serializer.instance.plant_type, 'is_urgent': serializer.instance.is_urgent}
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Question.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        log_user_activity(request.user, 'view', instance, {'resource': 'question'})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_questions(self, request):
        questions = Question.objects.filter(author=request.user)
        serializer = QuestionListSerializer(questions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def set_status(self, request, pk=None):
        question = self.get_object()
        next_status = request.data.get('status')
        valid_statuses = {choice[0] for choice in Question.STATUS_CHOICES}
        if next_status not in valid_statuses:
            return Response({'error': '问题状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        question.status = next_status
        question.save(update_fields=['status', 'updated_at'])
        return Response({'message': '问题状态已更新', 'status': question.status})


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    pagination_class = CommunityPagination
    filterset_fields = ['question', 'author', 'is_accepted']
    search_fields = ['content', 'author__username', 'question__title']
    ordering_fields = ['created_at', 'like_count']
    
    def get_queryset(self):
        return Answer.objects.select_related('question', 'author').all()
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [AllowAny()]
    
    def perform_create(self, serializer):
        answer = serializer.save(author=self.request.user)
        question = answer.question
        Question.objects.filter(pk=question.pk).update(answer_count=F('answer_count') + 1)
        log_user_activity(self.request.user, 'answer', answer, {'question_id': question.id})
        
        if question.author != self.request.user:
            send_user_notification(
                user=question.author,
                notification_type='answer',
                title='收到新回答',
                content=f'{self.request.user.username} 回答了你的问题《{question.title}》',
                related_url=f'/questions/{question.id}'
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        answer = self.get_object()
        question = answer.question
        
        if question.author != request.user:
            return Response({'error': '只有提问者可以采纳回答'}, status=status.HTTP_403_FORBIDDEN)
        
        Answer.objects.filter(question=question).update(is_accepted=False)
        answer.is_accepted = True
        answer.save()
        
        question.status = 'answered'
        question.save()
        
        if answer.author != request.user:
            send_user_notification(
                user=answer.author,
                notification_type='system',
                title='回答被采纳',
                content=f'你对问题《{question.title}》的回答已被采纳为最佳答案！',
                related_url=f'/questions/{question.id}'
            )
        
        return Response({'message': '采纳成功'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        answer = self.get_object()
        _, created = AnswerLike.objects.get_or_create(user=request.user, answer=answer)
        if created:
            Answer.objects.filter(pk=answer.pk).update(like_count=F('like_count') + 1)
            if answer.author != request.user:
                send_user_notification(
                    user=answer.author,
                    notification_type='interaction',
                    title='收到回答赞同',
                    content=f'{request.user.username} 赞同了你在《{answer.question.title}》下的回答',
                    related_url=f'/questions/{answer.question.id}'
                )
            log_user_activity(request.user, 'like', answer, {'target': 'answer'})
            return Response({'message': '点赞成功'})
        return Response({'message': '已点赞'})

    def perform_destroy(self, instance):
        question = instance.question
        was_accepted = instance.is_accepted
        instance.delete()
        question.answer_count = max(question.answer_count - 1, 0)
        update_fields = ['answer_count']
        if was_accepted and question.status == 'answered' and not question.answers.filter(is_accepted=True).exists():
            question.status = 'open'
            update_fields.append('status')
        question.save(update_fields=update_fields)
