from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('expert', '养护达人'),
        ('user', '普通用户'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('beginner', '新手'),
        ('intermediate', '有一定经验'),
        ('advanced', '资深玩家'),
        ('expert', '专业级'),
    ]
    
    REGION_CHOICES = [
        ('north', '华北'),
        ('northeast', '东北'),
        ('east', '华东'),
        ('central', '华中'),
        ('south', '华南'),
        ('southwest', '西南'),
        ('northwest', '西北'),
    ]
    
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    bio = models.TextField('个人简介', max_length=500, blank=True)
    experience_level = models.CharField('养护经验等级', max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')
    region = models.CharField('所在地区', max_length=20, choices=REGION_CHOICES, blank=True)
    
    is_expert_verified = models.BooleanField('达人认证状态', default=False)
    expert_apply_status = models.CharField('达人申请状态', max_length=20, 
        choices=[('none', '未申请'), ('pending', '审核中'), ('approved', '已通过'), ('rejected', '已拒绝')],
        default='none')
    expert_specialty = models.TextField('擅长领域', blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class UserTag(models.Model):
    TAG_TYPE_CHOICES = [
        ('plant_type', '植物类型'),
        ('care_environment', '养护环境'),
        ('interest', '兴趣方向'),
        ('problem', '常见问题'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags', verbose_name='用户')
    tag_type = models.CharField('标签类型', max_length=30, choices=TAG_TYPE_CHOICES)
    tag_value = models.CharField('标签值', max_length=100)
    weight = models.FloatField('权重', default=1.0)
    is_auto = models.BooleanField('是否自动生成', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '用户标签'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'tag_type', 'tag_value']
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.tag_value}"


class ExpertApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', '审核中'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expert_applications', verbose_name='申请用户')
    specialty = models.TextField('擅长领域')
    experience_desc = models.TextField('养护经验描述')
    certification = models.ImageField('资质证明', upload_to='certifications/', null=True, blank=True)
    status = models.CharField('审核状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='reviewed_applications', verbose_name='审核人')
    review_comment = models.TextField('审核意见', blank=True)
    created_at = models.DateTimeField('申请时间', auto_now_add=True)
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '达人认证申请'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('match', '匹配提醒'),
        ('answer', '答疑回复'),
        ('system', '系统通知'),
        ('interaction', '互动通知'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收用户')
    notification_type = models.CharField('通知类型', max_length=20, choices=TYPE_CHOICES)
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    is_read = models.BooleanField('是否已读', default=False)
    related_url = models.CharField('相关链接', max_length=500, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference', verbose_name='用户')
    in_app_enabled = models.BooleanField('站内通知开关', default=True)
    email_enabled = models.BooleanField('邮件通知开关', default=False)
    receive_match = models.BooleanField('接收匹配提醒', default=True)
    receive_answer = models.BooleanField('接收答疑回复', default=True)
    receive_system = models.BooleanField('接收系统通知', default=True)
    receive_interaction = models.BooleanField('接收互动通知', default=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '通知偏好'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} - 通知偏好"
