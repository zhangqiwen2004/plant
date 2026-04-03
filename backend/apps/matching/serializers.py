from rest_framework import serializers

from apps.community.moderation import validate_clean_content
from apps.users.serializers import UserSerializer

from .models import ConsultationMessage, ConsultationSession, MatchRecord, MatchRequest, TagWeight


class MatchParticipantSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    region_display = serializers.CharField(source='get_region_display', read_only=True)

    class Meta:
        model = UserSerializer.Meta.model
        fields = [
            'id', 'username', 'avatar', 'role', 'role_display', 'bio',
            'region', 'region_display', 'is_expert_verified', 'expert_specialty'
        ]


class MatchAdminParticipantSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = UserSerializer.Meta.model
        fields = ['id', 'username', 'avatar', 'role', 'role_display', 'is_expert_verified']


class MatchRecordSerializer(serializers.ModelSerializer):
    matched_user_info = UserSerializer(source='matched_user', read_only=True)
    match_type_display = serializers.CharField(source='get_match_type_display', read_only=True)

    class Meta:
        model = MatchRecord
        fields = ['id', 'user', 'matched_user', 'matched_user_info', 'match_type',
                  'match_type_display', 'similarity_score', 'match_reason', 'matched_tags',
                  'is_contacted', 'feedback', 'feedback_comment', 'created_at']
        read_only_fields = ['id', 'user', 'matched_user', 'match_type', 'similarity_score',
                            'match_reason', 'matched_tags', 'created_at']


class MatchResultSerializer(serializers.Serializer):
    score = serializers.FloatField()
    tag_similarity = serializers.FloatField()
    region_score = serializers.FloatField()
    experience_score = serializers.FloatField()
    matched_tags = serializers.ListField()
    overlap_count = serializers.IntegerField(required=False)
    core_tag_count = serializers.IntegerField(required=False)
    priority_hits = serializers.DictField(required=False)
    match_reason = serializers.CharField(required=False)


class MatchRequestSerializer(serializers.ModelSerializer):
    from_user_info = UserSerializer(source='from_user', read_only=True)
    to_user_info = UserSerializer(source='to_user', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    consultation_id = serializers.IntegerField(source='consultation.id', read_only=True)
    consultation_status = serializers.CharField(source='consultation.status', read_only=True)

    class Meta:
        model = MatchRequest
        fields = ['id', 'from_user', 'from_user_info', 'to_user', 'to_user_info',
                  'message', 'status', 'status_display', 'consultation_id', 'consultation_status',
                  'created_at', 'responded_at']
        read_only_fields = ['id', 'from_user', 'status', 'created_at', 'responded_at']

    def validate_message(self, value):
        validate_clean_content(value)
        return value


class AdminMatchRequestSerializer(serializers.ModelSerializer):
    from_user_info = MatchAdminParticipantSerializer(source='from_user', read_only=True)
    to_user_info = MatchAdminParticipantSerializer(source='to_user', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    consultation_id = serializers.IntegerField(source='consultation.id', read_only=True)

    class Meta:
        model = MatchRequest
        fields = [
            'id', 'from_user', 'from_user_info', 'to_user', 'to_user_info',
            'status', 'status_display', 'consultation_id', 'created_at', 'responded_at'
        ]
        read_only_fields = fields


class MatchFeedbackSerializer(serializers.Serializer):
    feedback = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True)


class AdminMatchRecordSerializer(serializers.ModelSerializer):
    user_info = MatchAdminParticipantSerializer(source='user', read_only=True)
    matched_user_info = MatchAdminParticipantSerializer(source='matched_user', read_only=True)
    match_type_display = serializers.CharField(source='get_match_type_display', read_only=True)

    class Meta:
        model = MatchRecord
        fields = [
            'id', 'user', 'user_info', 'matched_user', 'matched_user_info',
            'match_type', 'match_type_display', 'similarity_score',
            'is_contacted', 'feedback', 'created_at'
        ]
        read_only_fields = fields


class ConsultationMessageSerializer(serializers.ModelSerializer):
    sender_info = MatchParticipantSerializer(source='sender', read_only=True)
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)

    class Meta:
        model = ConsultationMessage
        fields = ['id', 'sender', 'sender_info', 'message_type', 'message_type_display', 'content', 'created_at']
        read_only_fields = ['id', 'sender', 'message_type', 'created_at']


class ConsultationMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=1000)

    def validate_content(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError('消息内容不能为空')
        validate_clean_content(cleaned_value)
        return cleaned_value


class ConsultationSessionListSerializer(serializers.ModelSerializer):
    requester_info = MatchParticipantSerializer(source='requester', read_only=True)
    consultant_info = MatchParticipantSerializer(source='consultant', read_only=True)
    counterpart_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    match_type_display = serializers.CharField(source='get_match_type_display', read_only=True)
    request_message = serializers.CharField(source='match_request.message', read_only=True)

    class Meta:
        model = ConsultationSession
        fields = [
            'id', 'match_request', 'requester', 'requester_info', 'consultant', 'consultant_info',
            'counterpart_info', 'match_type', 'match_type_display', 'status', 'status_display',
            'request_message', 'last_message_preview', 'last_message_at',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = fields

    def get_counterpart_info(self, obj):
        request = self.context.get('request')
        current_user = getattr(request, 'user', None)
        counterpart = obj.consultant if current_user and current_user == obj.requester else obj.requester
        return MatchParticipantSerializer(counterpart, context=self.context).data


class ConsultationSessionDetailSerializer(ConsultationSessionListSerializer):
    messages = ConsultationMessageSerializer(many=True, read_only=True)
    current_record_id = serializers.SerializerMethodField()
    current_feedback = serializers.SerializerMethodField()
    current_feedback_comment = serializers.SerializerMethodField()
    can_complete = serializers.SerializerMethodField()
    can_send_message = serializers.SerializerMethodField()

    class Meta(ConsultationSessionListSerializer.Meta):
        fields = ConsultationSessionListSerializer.Meta.fields + [
            'messages', 'current_record_id', 'current_feedback', 'current_feedback_comment',
            'can_complete', 'can_send_message'
        ]
        read_only_fields = fields

    def _get_current_record(self, obj):
        request = self.context.get('request')
        current_user = getattr(request, 'user', None)
        if not current_user or not current_user.is_authenticated:
            return None

        counterpart = obj.consultant if current_user == obj.requester else obj.requester
        return MatchRecord.objects.filter(user=current_user, matched_user=counterpart).order_by('-created_at').first()

    def get_current_record_id(self, obj):
        record = self._get_current_record(obj)
        return record.id if record else None

    def get_current_feedback(self, obj):
        record = self._get_current_record(obj)
        return record.feedback if record else None

    def get_current_feedback_comment(self, obj):
        record = self._get_current_record(obj)
        return record.feedback_comment if record else ''

    def get_can_complete(self, obj):
        request = self.context.get('request')
        current_user = getattr(request, 'user', None)
        return bool(current_user and current_user.is_authenticated and obj.status == 'active')

    def get_can_send_message(self, obj):
        return obj.status == 'active'


class TagWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagWeight
        fields = ['id', 'tag_type', 'weight', 'description']
