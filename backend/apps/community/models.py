from django.db import models
from apps.users.models import User


class Topic(models.Model):
    name = models.CharField('话题名称', max_length=100, unique=True)
    description = models.TextField('话题描述', blank=True)
    icon = models.ImageField('话题图标', upload_to='topics/', null=True, blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    post_count = models.IntegerField('帖子数', default=0)
    follower_count = models.IntegerField('关注数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '话题圈'
        verbose_name_plural = verbose_name
        ordering = ['-follower_count']
        
    def __str__(self):
        return self.name


class TopicFollow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_topics')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField('关注时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '话题关注'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'topic']


class Post(models.Model):
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='作者')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='posts', verbose_name='话题')
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    images = models.JSONField('图片列表', default=list, blank=True)
    
    status = models.CharField('审核状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='reviewed_posts', verbose_name='审核人')
    review_comment = models.TextField('审核意见', blank=True)
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)
    
    view_count = models.IntegerField('浏览数', default=0)
    like_count = models.IntegerField('点赞数', default=0)
    comment_count = models.IntegerField('评论数', default=0)
    is_top = models.BooleanField('是否置顶', default=False)
    is_essence = models.BooleanField('是否精华', default=False)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '帖子'
        verbose_name_plural = verbose_name
        ordering = ['-is_top', '-created_at']
        
    def __str__(self):
        return self.title


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_images')
    image = models.ImageField('图片', upload_to='posts/')
    order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '帖子图片'
        verbose_name_plural = verbose_name
        ordering = ['order']


class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField('点赞时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '帖子点赞'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'post']


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='帖子')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='作者')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='replies', verbose_name='父评论')
    reply_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='replied_comments', verbose_name='回复对象')
    content = models.TextField('内容')
    like_count = models.IntegerField('点赞数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"


class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField('点赞时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '评论点赞'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'comment']


class Question(models.Model):
    STATUS_CHOICES = [
        ('open', '待解答'),
        ('answered', '已解答'),
        ('closed', '已关闭'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name='提问者')
    title = models.CharField('问题标题', max_length=200)
    content = models.TextField('问题描述')
    images = models.JSONField('图片列表', default=list, blank=True)
    plant_type = models.CharField('植物类型', max_length=100, blank=True)
    
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='open')
    view_count = models.IntegerField('浏览数', default=0)
    answer_count = models.IntegerField('回答数', default=0)
    
    is_urgent = models.BooleanField('是否紧急', default=False)
    bounty = models.IntegerField('悬赏积分', default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '养护问题'
        verbose_name_plural = verbose_name
        ordering = ['-is_urgent', '-created_at']
        
    def __str__(self):
        return self.title


class QuestionImage(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_images')
    image = models.ImageField('图片', upload_to='questions/')
    order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '问题图片'
        verbose_name_plural = verbose_name
        ordering = ['order']


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='问题')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name='回答者')
    content = models.TextField('回答内容')
    images = models.JSONField('图片列表', default=list, blank=True)
    
    is_accepted = models.BooleanField('是否被采纳', default=False)
    like_count = models.IntegerField('点赞数', default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '问题回答'
        verbose_name_plural = verbose_name
        ordering = ['-is_accepted', '-like_count', '-created_at']
        
    def __str__(self):
        return f"{self.author.username} 回答 {self.question.title}"


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_likes')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField('点赞时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '回答点赞'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'answer']
