from django.contrib import admin
from .models import (
    Topic, TopicFollow, Post, PostImage, PostLike, Comment, CommentLike,
    Question, QuestionImage, Answer, AnswerLike
)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count', 'follower_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'topic', 'status', 'view_count', 'like_count', 'is_top', 'is_essence']
    list_filter = ['status', 'topic', 'is_top', 'is_essence']
    search_fields = ['title', 'content', 'author__username']
    actions = ['approve_posts', 'reject_posts']
    
    @admin.action(description='批准选中的帖子')
    def approve_posts(self, request, queryset):
        queryset.update(status='approved', reviewer=request.user)
    
    @admin.action(description='拒绝选中的帖子')
    def reject_posts(self, request, queryset):
        queryset.update(status='rejected', reviewer=request.user)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'content', 'like_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'plant_type', 'answer_count', 'is_urgent']
    list_filter = ['status', 'is_urgent', 'plant_type']
    search_fields = ['title', 'content', 'author__username']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'author', 'is_accepted', 'like_count', 'created_at']
    list_filter = ['is_accepted']
    search_fields = ['content', 'author__username']
