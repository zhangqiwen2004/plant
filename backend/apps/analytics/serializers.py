from rest_framework import serializers

from apps.users.models import User

from .models import DailyStatistics, UserActivity


class ActivityUserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'role', 'role_display']


class DailyStatisticsSerializer(serializers.ModelSerializer):
    match_success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyStatistics
        fields = '__all__'
    
    def get_match_success_rate(self, obj):
        if obj.match_count > 0:
            return round(obj.match_success_count / obj.match_count * 100, 2)
        return 0


class UserActivitySerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_info = ActivityUserSerializer(source='user', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'username', 'user_info', 'action', 'action_display',
                  'target_type', 'target_id', 'extra_data', 'created_at']


class OverviewSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_experts = serializers.IntegerField()
    total_posts = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    total_answers = serializers.IntegerField()
    pending_posts = serializers.IntegerField()
    pending_applications = serializers.IntegerField()
    today_active_users = serializers.IntegerField()
    today_new_users = serializers.IntegerField()
    match_success_rate = serializers.FloatField()


class TrendDataSerializer(serializers.Serializer):
    dates = serializers.ListField(child=serializers.DateField())
    new_users = serializers.ListField(child=serializers.IntegerField())
    active_users = serializers.ListField(child=serializers.IntegerField())
    posts = serializers.ListField(child=serializers.IntegerField())
    interactions = serializers.ListField(child=serializers.IntegerField())
