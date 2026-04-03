from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import F

from .models import PlantCategory, Plant, PlantTag, UserPlant, CareRecord
from .serializers import (
    PlantAdminSerializer, PlantCategorySerializer, PlantListSerializer, PlantDetailSerializer,
    PlantTagSerializer, UserPlantSerializer, CareRecordSerializer
)
from apps.users.permissions import IsAdmin


class PlantCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = PlantCategorySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'admin':
            return PlantCategory.objects.all()
        return PlantCategory.objects.filter(parent=None)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [AllowAny()]
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        categories = PlantCategory.objects.all()
        serializer = PlantCategorySerializer(categories, many=True)
        return Response(serializer.data)


class PlantViewSet(viewsets.ModelViewSet):
    filterset_fields = ['category', 'difficulty', 'light_requirement', 'water_requirement', 'is_active']
    search_fields = ['name', 'scientific_name', 'alias', 'description']
    ordering_fields = ['created_at', 'view_count', 'name']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'admin':
            return Plant.objects.all().select_related('category').prefetch_related('tag_relations__tag')
        return Plant.objects.filter(is_active=True).select_related('category').prefetch_related('tag_relations__tag')
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [AllowAny()]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PlantAdminSerializer
        if self.action == 'retrieve':
            return PlantDetailSerializer
        return PlantListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Plant.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def collect(self, request, pk=None):
        plant = self.get_object()
        user_plant, created = UserPlant.objects.get_or_create(
            user=request.user, plant=plant,
            defaults={
                'nickname': request.data.get('nickname', ''),
                'notes': request.data.get('notes', ''),
                'acquired_date': request.data.get('acquired_date')
            }
        )
        if created:
            return Response({'message': '收藏成功'}, status=status.HTTP_201_CREATED)
        return Response({'message': '已收藏过该植物'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def uncollect(self, request, pk=None):
        plant = self.get_object()
        deleted, _ = UserPlant.objects.filter(user=request.user, plant=plant).delete()
        if deleted:
            return Response({'message': '取消收藏成功'})
        return Response({'message': '未收藏该植物'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        plants = Plant.objects.filter(is_active=True).order_by('-view_count')[:10]
        serializer = PlantListSerializer(plants, many=True)
        return Response(serializer.data)


class PlantTagViewSet(viewsets.ModelViewSet):
    queryset = PlantTag.objects.all()
    serializer_class = PlantTagSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [AllowAny()]


class UserPlantViewSet(viewsets.ModelViewSet):
    serializer_class = UserPlantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserPlant.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CareRecordViewSet(viewsets.ModelViewSet):
    serializer_class = CareRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user_plant', 'care_type', 'care_date']
    ordering_fields = ['care_date', 'created_at']
    
    def get_queryset(self):
        return CareRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
