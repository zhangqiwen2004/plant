from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.analytics.activity_service import log_user_activity
from apps.users.notification_service import send_user_notification
from apps.users.permissions import IsAdmin

from .basic_algorithm import matching_algorithm
from .constants import MATCH_MODE_API_VALUES
from .models import ConsultationMessage, ConsultationSession, MatchRecord, MatchRequest, TagWeight
from .serializers import (
    AdminMatchRecordSerializer,
    AdminMatchRequestSerializer,
    ConsultationMessageCreateSerializer,
    ConsultationMessageSerializer,
    ConsultationSessionDetailSerializer,
    ConsultationSessionListSerializer,
    MatchFeedbackSerializer,
    MatchRecordSerializer,
    MatchRequestSerializer,
    TagWeightSerializer,
)


CONSULTATION_STARTED_TEXT = '咨询会话已建立，请围绕植物养护问题继续交流。'
CONSULTATION_COMPLETED_TEXT = '本次咨询已结束，你们仍可以回看记录和提交反馈。'


def infer_match_type(from_user, to_user):
    direct_record = MatchRecord.objects.filter(user=from_user, matched_user=to_user).order_by('-created_at').first()
    if direct_record:
        return direct_record.match_type, direct_record
    return ('expert' if to_user.is_expert_verified else 'peer'), None


def ensure_match_records(from_user, to_user):
    match_type, direct_record = infer_match_type(from_user, to_user)
    if direct_record is None:
        result = matching_algorithm.calculate_match_score(from_user, to_user, match_type)
        direct_record = MatchRecord.objects.create(
            user=from_user,
            matched_user=to_user,
            match_type=match_type,
            similarity_score=result['score'],
            match_reason=matching_algorithm.generate_match_reason(
                result['matched_tags'],
                result['region_score'] >= 0.8,
                result['experience_score'] >= 0.8
            ),
            matched_tags=result['matched_tags'],
        )

    reciprocal_record, _ = MatchRecord.objects.get_or_create(
        user=to_user,
        matched_user=from_user,
        defaults={
            'match_type': direct_record.match_type,
            'similarity_score': direct_record.similarity_score,
            'match_reason': direct_record.match_reason,
            'matched_tags': direct_record.matched_tags,
        }
    )
    return direct_record, reciprocal_record


def create_system_message(consultation, content):
    message = ConsultationMessage.objects.create(
        consultation=consultation,
        sender=None,
        message_type='system',
        content=content,
    )
    consultation.last_message_preview = content[:200]
    consultation.last_message_at = message.created_at
    consultation.save(update_fields=['last_message_preview', 'last_message_at', 'updated_at'])
    return message


def ensure_consultation_for_request(match_request):
    direct_record, reciprocal_record = ensure_match_records(match_request.from_user, match_request.to_user)
    direct_record.is_contacted = True
    direct_record.save(update_fields=['is_contacted'])
    reciprocal_record.is_contacted = True
    reciprocal_record.save(update_fields=['is_contacted'])

    consultation, created = ConsultationSession.objects.get_or_create(
        match_request=match_request,
        defaults={
            'requester': match_request.from_user,
            'consultant': match_request.to_user,
            'match_type': direct_record.match_type,
            'last_message_preview': CONSULTATION_STARTED_TEXT[:200],
            'last_message_at': timezone.now(),
        }
    )

    if created:
        create_system_message(consultation, CONSULTATION_STARTED_TEXT)

    return consultation


def ensure_consultations_for_user(user):
    accepted_requests = MatchRequest.objects.filter(
        Q(from_user=user) | Q(to_user=user),
        status='accepted',
        consultation__isnull=True,
    ).select_related('from_user', 'to_user')
    for match_request in accepted_requests:
        ensure_consultation_for_request(match_request)


class MatchingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def find_experts(self, request):
        limit = int(request.query_params.get('limit', 10))
        matches = matching_algorithm.find_expert_matches(request.user, limit=limit)

        results = []
        for match in matches:
            user_data = {
                'id': match['user'].id,
                'username': match['user'].username,
                'avatar': match['user'].avatar.url if match['user'].avatar else None,
                'bio': match['user'].bio,
                'experience_level': match['user'].experience_level,
                'region': match['user'].region,
                'expert_specialty': match['user'].expert_specialty,
                'is_expert_verified': match['user'].is_expert_verified,
            }

            match_reason = matching_algorithm.generate_match_reason(
                match['matched_tags'],
                match['region_score'] >= 0.8,
                match['experience_score'] >= 0.8
            )

            results.append({
                'user': user_data,
                'score': match['score'],
                'tag_similarity': match['tag_similarity'],
                'region_score': match['region_score'],
                'experience_score': match['experience_score'],
                'matched_tags': match['matched_tags'],
                'match_reason': match_reason
            })

        return Response(results)

    @action(detail=False, methods=['get'])
    def find_peers(self, request):
        limit = int(request.query_params.get('limit', 10))
        matches = matching_algorithm.find_peer_matches(request.user, limit=limit)

        results = []
        for match in matches:
            user_data = {
                'id': match['user'].id,
                'username': match['user'].username,
                'avatar': match['user'].avatar.url if match['user'].avatar else None,
                'bio': match['user'].bio,
                'experience_level': match['user'].experience_level,
                'region': match['user'].region,
            }

            match_reason = matching_algorithm.generate_match_reason(
                match['matched_tags'],
                match['region_score'] >= 0.8,
                match['experience_score'] >= 0.8
            )

            results.append({
                'user': user_data,
                'score': match['score'],
                'tag_similarity': match['tag_similarity'],
                'region_score': match['region_score'],
                'experience_score': match['experience_score'],
                'matched_tags': match['matched_tags'],
                'match_reason': match_reason
            })

        return Response(results)

    @action(detail=False, methods=['post'])
    def save_match(self, request):
        matched_user_id = request.data.get('matched_user_id')
        match_type = request.data.get('match_type', 'peer')
        if match_type not in MATCH_MODE_API_VALUES:
            return Response({'error': '匹配类型不正确'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.users.models import User

        try:
            matched_user = User.objects.get(pk=matched_user_id)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        result = matching_algorithm.calculate_match_score(request.user, matched_user, match_type)
        match_reason = matching_algorithm.generate_match_reason(
            result['matched_tags'],
            result['region_score'] >= 0.8,
            result['experience_score'] >= 0.8
        )

        record, created = MatchRecord.objects.get_or_create(
            user=request.user,
            matched_user=matched_user,
            defaults={
                'match_type': match_type,
                'similarity_score': result['score'],
                'match_reason': match_reason,
                'matched_tags': result['matched_tags']
            }
        )

        if not created:
            record.similarity_score = result['score']
            record.match_reason = match_reason
            record.matched_tags = result['matched_tags']
            record.save()

        log_user_activity(request.user, 'match', record, {'match_type': match_type, 'matched_user_id': matched_user.id})
        serializer = MatchRecordSerializer(record)
        return Response(serializer.data)


class MatchRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MatchRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['match_type', 'is_contacted']
    ordering_fields = ['created_at', 'similarity_score', 'feedback']

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return MatchRecord.objects.select_related('user', 'matched_user').all()
        return MatchRecord.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.user.role == 'admin':
            return AdminMatchRecordSerializer
        return MatchRecordSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    def admin_summary(self, request):
        total_records = MatchRecord.objects.count()
        contacted_records = MatchRecord.objects.filter(is_contacted=True).count()
        expert_records = MatchRecord.objects.filter(match_type='expert').count()
        peer_records = MatchRecord.objects.filter(match_type='peer').count()
        avg_score = round(sum(MatchRecord.objects.values_list('similarity_score', flat=True)) / total_records, 4) if total_records else 0

        request_queryset = MatchRequest.objects.all()
        total_requests = request_queryset.count()
        pending_requests = request_queryset.filter(status='pending').count()
        accepted_requests = request_queryset.filter(status='accepted').count()
        rejected_requests = request_queryset.filter(status='rejected').count()

        return Response({
            'total_records': total_records,
            'contacted_records': contacted_records,
            'expert_records': expert_records,
            'peer_records': peer_records,
            'average_score': avg_score,
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'accepted_requests': accepted_requests,
            'rejected_requests': rejected_requests,
        })

    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        record = self.get_object()
        serializer = MatchFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record.feedback = serializer.validated_data['feedback']
        record.feedback_comment = serializer.validated_data.get('comment', '')
        record.save(update_fields=['feedback', 'feedback_comment'])

        return Response({'message': '反馈提交成功'})

    @action(detail=True, methods=['post'])
    def mark_contacted(self, request, pk=None):
        record = self.get_object()
        record.is_contacted = True
        record.save(update_fields=['is_contacted'])
        return Response({'message': '已标记为已联系'})


class MatchRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MatchRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'responded_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return MatchRequest.objects.select_related('from_user', 'to_user').all()
        return (MatchRequest.objects.filter(from_user=user) | MatchRequest.objects.filter(to_user=user)).distinct()

    def get_serializer_class(self):
        if self.request.user.role == 'admin' and self.action in ['list', 'retrieve']:
            return AdminMatchRequestSerializer
        return MatchRequestSerializer

    def perform_create(self, serializer):
        match_request = serializer.save(from_user=self.request.user)
        send_user_notification(
            user=match_request.to_user,
            notification_type='match',
            title='收到匹配请求',
            content=f'{self.request.user.username} 希望与您建立联系',
            related_url='/matching'
        )
        log_user_activity(self.request.user, 'match', match_request, {'target_user_id': match_request.to_user_id, 'request': 'sent'})

    @action(detail=False, methods=['get'])
    def received(self, request):
        requests = MatchRequest.objects.filter(to_user=request.user, status='pending')
        serializer = MatchRequestSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        ensure_consultations_for_user(request.user)
        requests = MatchRequest.objects.filter(from_user=request.user)
        serializer = MatchRequestSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        match_request = self.get_object()
        if match_request.to_user != request.user:
            return Response({'error': '无权操作'}, status=status.HTTP_403_FORBIDDEN)

        if match_request.status == 'accepted':
            consultation = ensure_consultation_for_request(match_request)
            return Response({'message': '该请求已接受', 'consultation_id': consultation.id})
        if match_request.status != 'pending':
            return Response({'error': '当前请求状态不可接受'}, status=status.HTTP_400_BAD_REQUEST)

        match_request.status = 'accepted'
        match_request.responded_at = timezone.now()
        match_request.save(update_fields=['status', 'responded_at'])
        consultation = ensure_consultation_for_request(match_request)

        send_user_notification(
            user=match_request.from_user,
            notification_type='match',
            title='匹配请求已接受',
            content=f'{request.user.username} 接受了您的匹配请求',
            related_url=f'/matching/consultations/{consultation.id}'
        )
        log_user_activity(request.user, 'match', match_request, {'target_user_id': match_request.from_user_id, 'request': 'accepted'})

        return Response({'message': '已接受请求', 'consultation_id': consultation.id})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        match_request = self.get_object()
        if match_request.to_user != request.user:
            return Response({'error': '无权操作'}, status=status.HTTP_403_FORBIDDEN)
        if match_request.status != 'pending':
            return Response({'error': '当前请求状态不可拒绝'}, status=status.HTTP_400_BAD_REQUEST)

        match_request.status = 'rejected'
        match_request.responded_at = timezone.now()
        match_request.save(update_fields=['status', 'responded_at'])
        log_user_activity(request.user, 'match', match_request, {'target_user_id': match_request.from_user_id, 'request': 'rejected'})

        return Response({'message': '已拒绝请求'})


class ConsultationSessionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ensure_consultations_for_user(self.request.user)
        queryset = ConsultationSession.objects.filter(
            Q(requester=self.request.user) | Q(consultant=self.request.user)
        ).select_related('requester', 'consultant', 'match_request')
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('messages__sender')
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConsultationSessionDetailSerializer
        return ConsultationSessionListSerializer

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        consultation = self.get_object()
        if consultation.status != 'active':
            return Response({'error': '咨询已结束，无法继续发送消息'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ConsultationMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = ConsultationMessage.objects.create(
            consultation=consultation,
            sender=request.user,
            message_type='user',
            content=serializer.validated_data['content'],
        )
        consultation.last_message_preview = message.content[:200]
        consultation.last_message_at = message.created_at
        consultation.save(update_fields=['last_message_preview', 'last_message_at', 'updated_at'])

        counterpart = consultation.consultant if request.user == consultation.requester else consultation.requester
        send_user_notification(
            user=counterpart,
            notification_type='match',
            title='收到新的咨询消息',
            content=f'{request.user.username} 发送了新的咨询消息',
            related_url=f'/matching/consultations/{consultation.id}'
        )
        log_user_activity(request.user, 'match', consultation, {'conversation_id': consultation.id, 'event': 'message'})

        message_serializer = ConsultationMessageSerializer(message, context={'request': request})
        return Response(message_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        consultation = self.get_object()
        if consultation.status == 'completed':
            serializer = ConsultationSessionDetailSerializer(consultation, context={'request': request})
            return Response(serializer.data)

        consultation.status = 'completed'
        consultation.completed_at = timezone.now()
        consultation.save(update_fields=['status', 'completed_at', 'updated_at'])
        create_system_message(consultation, CONSULTATION_COMPLETED_TEXT)

        counterpart = consultation.consultant if request.user == consultation.requester else consultation.requester
        send_user_notification(
            user=counterpart,
            notification_type='match',
            title='咨询已结束',
            content=f'{request.user.username} 已结束本次咨询会话',
            related_url=f'/matching/consultations/{consultation.id}'
        )
        log_user_activity(request.user, 'match', consultation, {'conversation_id': consultation.id, 'event': 'completed'})

        serializer = ConsultationSessionDetailSerializer(consultation, context={'request': request})
        return Response(serializer.data)


class TagWeightViewSet(viewsets.ModelViewSet):
    queryset = TagWeight.objects.all()
    serializer_class = TagWeightSerializer
    permission_classes = [IsAdmin]
