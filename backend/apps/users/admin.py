from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserTag, ExpertApplication


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'experience_level', 'region', 'is_expert_verified']
    list_filter = ['role', 'experience_level', 'region', 'is_expert_verified']
    search_fields = ['username', 'email']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('role', 'avatar', 'bio', 'experience_level', 'region',
                              'is_expert_verified', 'expert_apply_status', 'expert_specialty')}),
    )


@admin.register(UserTag)
class UserTagAdmin(admin.ModelAdmin):
    list_display = ['user', 'tag_type', 'tag_value', 'weight', 'is_auto']
    list_filter = ['tag_type', 'is_auto']
    search_fields = ['user__username', 'tag_value']


@admin.register(ExpertApplication)
class ExpertApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'reviewer', 'created_at', 'reviewed_at']
    list_filter = ['status']
    search_fields = ['user__username']
