from rest_framework import serializers
from .models import (
    Topic, TopicFollow, Post, PostImage, PostLike, Comment, CommentLike,
    Question, QuestionImage, Answer, AnswerLike
)
from .moderation import validate_clean_content
from apps.users.serializers import UserSerializer

MAX_IMAGE_COUNT = 6
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def validate_image_list(images):
    if len(images) > MAX_IMAGE_COUNT:
        raise serializers.ValidationError(f'最多上传 {MAX_IMAGE_COUNT} 张图片')
    for image in images:
        if image.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError('单张图片大小不能超过 5MB')
    return images


def get_uploaded_images(serializer, validated_data):
    uploaded_images = validated_data.pop('uploaded_images', [])
    request = serializer.context.get('request')
    request_images = request.FILES.getlist('uploaded_images') if request and hasattr(request, 'FILES') else []
    if request_images:
        return request_images

    if uploaded_images and not isinstance(uploaded_images, list):
        return [uploaded_images]
    return uploaded_images


class TopicSerializer(serializers.ModelSerializer):
    is_followed = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'icon', 'is_active', 
                  'post_count', 'follower_count', 'is_followed', 'created_at']
        read_only_fields = ['id', 'post_count', 'follower_count', 'created_at']
    
    def get_is_followed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TopicFollow.objects.filter(user=request.user, topic=obj).exists()
        return False


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'order']


class PostListSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    images = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'author_info', 'topic', 'topic_name', 'title', 
                  'content', 'images', 'status', 'status_display', 'view_count', 'like_count', 
                  'comment_count', 'is_top', 'is_essence', 'is_liked', 'created_at']
    
    def get_author_info(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar.url if obj.author.avatar else None,
            'role': obj.author.role,
            'is_expert': obj.author.is_expert_verified
        }
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(user=request.user, post=obj).exists()
        return False
    
    def get_images(self, obj):
        return [img.image.url for img in obj.post_images.all()]


class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['review_comment', 'reviewed_at', 'updated_at']


class PostCreateSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Post
        fields = ['topic', 'title', 'content', 'uploaded_images']

    def validate_uploaded_images(self, images):
        return validate_image_list(images)

    def validate(self, attrs):
        request = self.context.get('request')
        request_images = request.FILES.getlist('uploaded_images') if request and hasattr(request, 'FILES') else []
        if request_images:
            validate_image_list(request_images)
        validate_clean_content(attrs.get('title', ''), attrs.get('content', ''))
        return attrs

    def create(self, validated_data):
        uploaded_images = get_uploaded_images(self, validated_data)
        post = Post.objects.create(**validated_data)
        image_urls = []
        for index, image in enumerate(uploaded_images):
            post_image = PostImage.objects.create(post=post, image=image, order=index)
            image_urls.append(post_image.image.url)
        if image_urls:
            post.images = image_urls
            post.save(update_fields=['images'])
        return post

    def update(self, instance, validated_data):
        request = self.context.get('request')
        request_images = request.FILES.getlist('uploaded_images') if request and hasattr(request, 'FILES') else []
        uploaded_images = request_images if request_images else validated_data.pop('uploaded_images', None)
        if uploaded_images and not isinstance(uploaded_images, list):
            uploaded_images = [uploaded_images]
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if uploaded_images is not None:
            instance.post_images.all().delete()
            image_urls = []
            for index, image in enumerate(uploaded_images):
                post_image = PostImage.objects.create(post=instance, image=image, order=index)
                image_urls.append(post_image.image.url)
            instance.images = image_urls
            instance.save(update_fields=['images'])

        return instance


class CommentSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    post_title = serializers.CharField(source='post.title', read_only=True)
    reply_to_name = serializers.CharField(source='reply_to.username', read_only=True)
    replies = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'post_title', 'author', 'author_info', 'parent', 'reply_to',
                  'reply_to_name', 'content', 'like_count', 'replies', 'is_liked', 'created_at']
        read_only_fields = ['id', 'author', 'like_count', 'created_at']
    
    def get_author_info(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar.url if obj.author.avatar else None,
            'is_expert': obj.author.is_expert_verified
        }
    
    def get_replies(self, obj):
        if obj.parent is None:
            replies = obj.replies.all()[:5]
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(user=request.user, comment=obj).exists()
        return False

    def validate(self, attrs):
        validate_clean_content(attrs.get('content', ''))
        return attrs


class QuestionListSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'author', 'author_info', 'title', 'content', 'plant_type',
                  'status', 'status_display', 'view_count', 'answer_count', 
                  'is_urgent', 'bounty', 'created_at']
    
    def get_author_info(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar.url if obj.author.avatar else None,
        }


class QuestionDetailSerializer(QuestionListSerializer):
    images = serializers.SerializerMethodField()
    
    class Meta(QuestionListSerializer.Meta):
        fields = QuestionListSerializer.Meta.fields + ['images', 'updated_at']
    
    def get_images(self, obj):
        return [img.image.url for img in obj.question_images.all()]


class QuestionCreateSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Question
        fields = ['title', 'content', 'plant_type', 'is_urgent', 'bounty', 'uploaded_images']

    def validate_uploaded_images(self, images):
        return validate_image_list(images)

    def validate(self, attrs):
        request = self.context.get('request')
        request_images = request.FILES.getlist('uploaded_images') if request and hasattr(request, 'FILES') else []
        if request_images:
            validate_image_list(request_images)
        validate_clean_content(attrs.get('title', ''), attrs.get('content', ''), attrs.get('plant_type', ''))
        return attrs

    def create(self, validated_data):
        uploaded_images = get_uploaded_images(self, validated_data)
        question = Question.objects.create(**validated_data)
        image_urls = []
        for index, image in enumerate(uploaded_images):
            question_image = QuestionImage.objects.create(question=question, image=image, order=index)
            image_urls.append(question_image.image.url)
        if image_urls:
            question.images = image_urls
            question.save(update_fields=['images'])
        return question

    def update(self, instance, validated_data):
        request = self.context.get('request')
        request_images = request.FILES.getlist('uploaded_images') if request and hasattr(request, 'FILES') else []
        uploaded_images = request_images if request_images else validated_data.pop('uploaded_images', None)
        if uploaded_images and not isinstance(uploaded_images, list):
            uploaded_images = [uploaded_images]
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if uploaded_images is not None:
            instance.question_images.all().delete()
            image_urls = []
            for index, image in enumerate(uploaded_images):
                question_image = QuestionImage.objects.create(question=instance, image=image, order=index)
                image_urls.append(question_image.image.url)
            instance.images = image_urls
            instance.save(update_fields=['images'])

        return instance


class AnswerSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    question_title = serializers.CharField(source='question.title', read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Answer
        fields = ['id', 'question', 'question_title', 'author', 'author_info', 'content', 'images',
                  'is_accepted', 'like_count', 'is_liked', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'is_accepted', 'like_count', 'created_at', 'updated_at']
    
    def get_author_info(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar.url if obj.author.avatar else None,
            'role': obj.author.role,
            'is_expert': obj.author.is_expert_verified,
            'specialty': obj.author.expert_specialty if obj.author.is_expert_verified else ''
        }
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return AnswerLike.objects.filter(user=request.user, answer=obj).exists()
        return False

    def validate(self, attrs):
        validate_clean_content(attrs.get('content', ''))
        return attrs
