from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserTag, ExpertApplication, Notification, NotificationPreference


class UserTagSerializer(serializers.ModelSerializer):
    tag_type_display = serializers.CharField(source='get_tag_type_display', read_only=True)
    
    class Meta:
        model = UserTag
        fields = ['id', 'tag_type', 'tag_type_display', 'tag_value', 'weight', 'is_auto', 'created_at']
        read_only_fields = ['id', 'is_auto', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    experience_display = serializers.CharField(source='get_experience_level_display', read_only=True)
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    tags = UserTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'role_display', 'avatar', 'bio',
                  'experience_level', 'experience_display', 'region', 'region_display',
                  'is_expert_verified', 'expert_apply_status', 'expert_specialty',
                  'tags', 'created_at']
        read_only_fields = ['id', 'role', 'is_expert_verified', 'expert_apply_status', 'created_at']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 
                  'experience_level', 'region']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '两次密码输入不一致'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar', 'bio', 'experience_level', 'region', 'expert_specialty']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value


class ExpertApplicationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ExpertApplication
        fields = ['id', 'user', 'specialty', 'experience_desc', 'certification',
                  'status', 'status_display', 'reviewer', 'reviewer_name', 
                  'review_comment', 'created_at', 'reviewed_at']
        read_only_fields = ['id', 'user', 'status', 'reviewer', 'review_comment', 
                           'created_at', 'reviewed_at']


class ExpertReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    review_comment = serializers.CharField(required=False, allow_blank=True)


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'in_app_enabled',
            'email_enabled',
            'receive_match',
            'receive_answer',
            'receive_system',
            'receive_interaction',
            'updated_at',
        ]
        read_only_fields = ['updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'type_display', 'title', 'content',
                  'is_read', 'related_url', 'created_at']
        read_only_fields = ['id', 'notification_type', 'title', 'content', 
                           'related_url', 'created_at']
