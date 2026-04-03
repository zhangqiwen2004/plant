from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from django.utils import timezone

from .models import User, UserTag, ExpertApplication, Notification, NotificationPreference
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, UserTagSerializer, ExpertApplicationSerializer,
    ExpertReviewSerializer, NotificationPreferenceSerializer, NotificationSerializer
)
from .notification_service import send_user_notification
from .permissions import IsAdmin, IsSelfOnly
from .constants import TAG_OPTIONS_BY_TYPE


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_tags(request):
    user = request.user
    tags_data = request.data.get('tags', [])
    if not isinstance(tags_data, list):
        return Response({'error': 'tags 必须为数组'}, status=status.HTTP_400_BAD_REQUEST)

    allowed_tag_types = {choice[0] for choice in UserTag.TAG_TYPE_CHOICES}
    existing_tag_values = {}
    for tag in user.tags.all():
        existing_tag_values.setdefault(tag.tag_type, set()).add(tag.tag_value)
    normalized_tags = []
    seen = set()
    for item in tags_data:
        if not isinstance(item, dict):
            return Response({'error': '标签格式不正确'}, status=status.HTTP_400_BAD_REQUEST)

        tag_type = item.get('tag_type')
        tag_value = str(item.get('tag_value', '')).strip()
        allowed_values = TAG_OPTIONS_BY_TYPE.get(tag_type, set())
        current_values = existing_tag_values.get(tag_type, set())
        if tag_type not in allowed_tag_types or not tag_value:
            return Response({'error': '标签格式不正确'}, status=status.HTTP_400_BAD_REQUEST)
        if allowed_values and tag_value not in allowed_values and tag_value not in current_values:
            return Response({'error': '标签格式不正确'}, status=status.HTTP_400_BAD_REQUEST)

        key = (tag_type, tag_value)
        if key in seen:
            continue

        seen.add(key)
        normalized_tags.append({
            'tag_type': tag_type,
            'tag_value': tag_value,
            'weight': item.get('weight', 1.0),
        })

    update_fields = []
    experience_level = request.data.get('experience_level')
    if experience_level in dict(User.EXPERIENCE_CHOICES):
        user.experience_level = experience_level
        update_fields.append('experience_level')

    region = request.data.get('region')
    if region == '' or region in dict(User.REGION_CHOICES):
        user.region = region
        update_fields.append('region')

    with transaction.atomic():
        if update_fields:
            user.save(update_fields=update_fields)
        UserTag.objects.filter(user=user).delete()
        UserTag.objects.bulk_create([
            UserTag(
                user=user,
                tag_type=item['tag_type'],
                tag_value=item['tag_value'],
                weight=item['weight'],
            )
            for item in normalized_tags
        ])

    refreshed_user = User.objects.prefetch_related('tags').get(pk=user.pk)
    return Response({
        'message': '标签已保存',
        'user': UserSerializer(refreshed_user).data,
        'tags': UserTagSerializer(refreshed_user.tags.all(), many=True).data,
    })


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        if user.role == 'admin' and self.action in ['list', 'retrieve']:
            return User.objects.all()
        return User.objects.filter(pk=user.pk)

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSelfOnly()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """返回用户统计数据（供管理员使用）"""
        if request.user.role != 'admin':
            return Response({'detail': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        total = User.objects.count()
        by_role = {}
        for role_code, _ in User.ROLE_CHOICES:
            by_role[role_code] = User.objects.filter(role=role_code).count()
        verified = User.objects.filter(is_expert_verified=True).count()
        return Response({
            'total': total,
            'by_role': by_role,
            'verified_experts': verified,
        })

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': '密码修改成功'})

    @action(detail=False, methods=['get'])
    def experts(self, request):
        experts = User.objects.filter(role='expert', is_expert_verified=True)
        serializer = UserSerializer(experts, many=True)
        return Response(serializer.data)


class UserTagViewSet(viewsets.ModelViewSet):
    serializer_class = UserTagSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserTag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        tags_data = request.data.get('tags', [])
        created_tags = []
        for tag_data in tags_data:
            tag, created = UserTag.objects.get_or_create(
                user=request.user,
                tag_type=tag_data.get('tag_type'),
                tag_value=tag_data.get('tag_value'),
                defaults={'weight': tag_data.get('weight', 1.0)}
            )
            if created:
                created_tags.append(tag)
        serializer = UserTagSerializer(created_tags, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExpertApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ExpertApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return ExpertApplication.objects.all()
        return ExpertApplication.objects.filter(user=user)

    def get_permissions(self):
        if self.action in ['review']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'user':
            raise serializers.ValidationError({'detail': '仅普通用户可以申请达人认证'})
        if user.expert_apply_status in ['pending', 'approved']:
            raise serializers.ValidationError({'detail': '您已有进行中或已通过的申请'})
        serializer.save(user=user)
        user.expert_apply_status = 'pending'
        user.save()

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        application = self.get_object()
        serializer = ExpertReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application.status = serializer.validated_data['status']
        application.review_comment = serializer.validated_data.get('review_comment', '')
        application.reviewer = request.user
        application.reviewed_at = timezone.now()
        application.save()

        user = application.user
        if application.status == 'approved':
            user.role = 'expert'
            user.is_expert_verified = True
            user.expert_apply_status = 'approved'
            user.expert_specialty = application.specialty
        else:
            user.expert_apply_status = 'rejected'
        user.save()

        send_user_notification(
            user=user,
            notification_type='system',
            title='达人认证审核结果',
            content=f'您的达人认证申请已{"通过" if application.status == "approved" else "被拒绝"}。{application.review_comment}',
        )

        return Response({'message': '审核完成'})

    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    def stats(self, request):
        total = ExpertApplication.objects.count()
        pending = ExpertApplication.objects.filter(status='pending').count()
        approved = ExpertApplication.objects.filter(status='approved').count()
        rejected = ExpertApplication.objects.filter(status='rejected').count()
        return Response({
            'total': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
        })


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['notification_type', 'is_read']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'patch'])
    def preferences(self, request):
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            serializer = NotificationPreferenceSerializer(preference)
            return Response(serializer.data)

        serializer = NotificationPreferenceSerializer(preference, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'count': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': '已全部标记为已读'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': '已标记为已读'})
