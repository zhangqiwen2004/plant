from django.contrib import admin
from .models import DailyStatistics, UserActivity


@admin.register(DailyStatistics)
class DailyStatisticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'new_users', 'active_users', 'total_users', 
                    'new_posts', 'new_questions', 'match_count']
    list_filter = ['date']
    ordering = ['-date']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'target_type', 'target_id', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username']
