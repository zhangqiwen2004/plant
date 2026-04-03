from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnalyticsOverviewView, AnalyticsTrendView,
    DailyStatisticsViewSet, UserActivityViewSet
)

router = DefaultRouter()
router.register('daily-stats', DailyStatisticsViewSet, basename='daily-stats')
router.register('activities', UserActivityViewSet, basename='activity')

urlpatterns = [
    path('overview/', AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('trend/', AnalyticsTrendView.as_view(), name='analytics-trend'),
    path('', include(router.urls)),
]
