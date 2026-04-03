from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TopicViewSet, PostViewSet, CommentViewSet, QuestionViewSet, AnswerViewSet

router = DefaultRouter()
router.register('topics', TopicViewSet, basename='topic')
router.register('posts', PostViewSet, basename='post')
router.register('comments', CommentViewSet, basename='comment')
router.register('questions', QuestionViewSet, basename='question')
router.register('answers', AnswerViewSet, basename='answer')

urlpatterns = [
    path('', include(router.urls)),
]
