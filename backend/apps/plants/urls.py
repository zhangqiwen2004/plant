from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlantCategoryViewSet, PlantViewSet, PlantTagViewSet,
    UserPlantViewSet, CareRecordViewSet
)

router = DefaultRouter()
router.register('categories', PlantCategoryViewSet, basename='plant-category')
router.register('tags', PlantTagViewSet, basename='plant-tag')
router.register('user-plants', UserPlantViewSet, basename='user-plant')
router.register('care-records', CareRecordViewSet, basename='care-record')
router.register('', PlantViewSet, basename='plant')

urlpatterns = [
    path('', include(router.urls)),
]
