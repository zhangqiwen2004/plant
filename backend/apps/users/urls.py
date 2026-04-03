from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserTagViewSet, ExpertApplicationViewSet, NotificationViewSet, submit_tags

router = DefaultRouter()
router.register('tags', UserTagViewSet, basename='user-tag')
router.register('expert-applications', ExpertApplicationViewSet, basename='expert-application')
router.register('notifications', NotificationViewSet, basename='notification')
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('tags/submit/', submit_tags),
    path('', include(router.urls)),
]
