from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsultationSessionViewSet, MatchingViewSet, MatchRecordViewSet, MatchRequestViewSet, TagWeightViewSet
from .function_views import basic_match_results

router = DefaultRouter()
router.register('find', MatchingViewSet, basename='matching')
router.register('records', MatchRecordViewSet, basename='match-record')
router.register('requests', MatchRequestViewSet, basename='match-request')
router.register('consultations', ConsultationSessionViewSet, basename='consultation')
router.register('tag-weights', TagWeightViewSet, basename='tag-weight')

urlpatterns = [
    path('basic-results/', basic_match_results),
    path('', include(router.urls)),
]
