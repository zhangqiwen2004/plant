from django.db import models
from apps.users.models import User


class DailyStatistics(models.Model):
    date = models.DateField('日期', unique=True)
    
    new_users = models.IntegerField('新增用户数', default=0)
    active_users = models.IntegerField('活跃用户数', default=0)
    total_users = models.IntegerField('总用户数', default=0)
    
    new_posts = models.IntegerField('新增帖子数', default=0)
    new_questions = models.IntegerField('新增问题数', default=0)
    new_answers = models.IntegerField('新增回答数', default=0)
    new_comments = models.IntegerField('新增评论数', default=0)
    
    total_interactions = models.IntegerField('总互动数', default=0)
    match_count = models.IntegerField('匹配次数', default=0)
    match_success_count = models.IntegerField('匹配成功次数', default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '每日统计'
        verbose_name_plural = verbose_name
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.date} 统计数据"


class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('login', '登录'),
        ('post', '发帖'),
        ('comment', '评论'),
        ('question', '提问'),
        ('answer', '回答'),
        ('like', '点赞'),
        ('match', '匹配'),
        ('view', '浏览'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField('行为类型', max_length=20, choices=ACTION_CHOICES)
    target_type = models.CharField('目标类型', max_length=50, blank=True)
    target_id = models.IntegerField('目标ID', null=True, blank=True)
    extra_data = models.JSONField('额外数据', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '用户活动'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"
