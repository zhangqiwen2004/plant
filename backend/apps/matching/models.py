from django.db import models
from django.utils import timezone

from apps.users.models import User


class MatchRecord(models.Model):
    MATCH_TYPE_CHOICES = [
        ('expert', '需求用户-养护达人'),
        ('peer', '需求用户-同好用户'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_records', verbose_name='发起用户')
    matched_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matched_by_records', verbose_name='匹配用户')
    match_type = models.CharField('匹配类型', max_length=20, choices=MATCH_TYPE_CHOICES)
    similarity_score = models.FloatField('相似度分数', default=0.0)
    match_reason = models.TextField('匹配依据', blank=True)
    matched_tags = models.JSONField('匹配的标签', default=list)
    
    is_contacted = models.BooleanField('是否已联系', default=False)
    feedback = models.IntegerField('反馈评分', null=True, blank=True)
    feedback_comment = models.TextField('反馈评论', blank=True)
    
    created_at = models.DateTimeField('匹配时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '匹配记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} -> {self.matched_user.username} ({self.similarity_score:.2f})"


class MatchRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
        ('expired', '已过期'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_match_requests', verbose_name='发起用户')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_match_requests', verbose_name='目标用户')
    message = models.TextField('请求消息', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    responded_at = models.DateTimeField('响应时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '匹配请求'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"


class ConsultationSession(models.Model):
    STATUS_CHOICES = [
        ('active', '进行中'),
        ('completed', '已完成'),
    ]

    match_request = models.OneToOneField(
        MatchRequest,
        on_delete=models.CASCADE,
        related_name='consultation',
        verbose_name='来源请求'
    )
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_consultations', verbose_name='发起用户')
    consultant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultant_consultations', verbose_name='接受用户')
    match_type = models.CharField('匹配类型', max_length=20, choices=MatchRecord.MATCH_TYPE_CHOICES, default='peer')
    status = models.CharField('会话状态', max_length=20, choices=STATUS_CHOICES, default='active')
    last_message_preview = models.CharField('最新消息摘要', max_length=200, blank=True)
    last_message_at = models.DateTimeField('最新消息时间', default=timezone.now)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '咨询会话'
        verbose_name_plural = verbose_name
        ordering = ['-last_message_at', '-created_at']

    def __str__(self):
        return f"{self.requester.username} <-> {self.consultant.username} ({self.get_status_display()})"


class ConsultationMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('system', '系统消息'),
        ('user', '用户消息'),
    ]

    consultation = models.ForeignKey(ConsultationSession, on_delete=models.CASCADE, related_name='messages', verbose_name='所属会话')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='consultation_messages', verbose_name='发送者')
    message_type = models.CharField('消息类型', max_length=20, choices=MESSAGE_TYPE_CHOICES, default='user')
    content = models.TextField('消息内容')
    created_at = models.DateTimeField('发送时间', auto_now_add=True)

    class Meta:
        verbose_name = '咨询消息'
        verbose_name_plural = verbose_name
        ordering = ['created_at']

    def __str__(self):
        sender = self.sender.username if self.sender else 'system'
        return f"{sender}: {self.content[:30]}"


class TagWeight(models.Model):
    tag_type = models.CharField('标签类型', max_length=30, unique=True)
    weight = models.FloatField('权重', default=1.0)
    description = models.TextField('描述', blank=True)
    
    class Meta:
        verbose_name = '标签权重'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f"{self.tag_type}: {self.weight}"
