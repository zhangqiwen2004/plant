from rest_framework import serializers

from .models import PlantCategory, Plant, PlantTag, PlantTagRelation, UserPlant, CareRecord


class PlantCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    plant_count = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = PlantCategory
        fields = ['id', 'name', 'description', 'icon', 'parent', 'parent_name', 'order', 'children', 'plant_count']
    
    def get_children(self, obj):
        children = obj.children.all()
        return PlantCategorySerializer(children, many=True).data
    
    def get_plant_count(self, obj):
        return obj.plants.count()


class PlantTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantTag
        fields = ['id', 'name', 'color']


class PlantListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    light_display = serializers.CharField(source='get_light_requirement_display', read_only=True)
    water_display = serializers.CharField(source='get_water_requirement_display', read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Plant
        fields = ['id', 'name', 'scientific_name', 'category', 'category_name', 
                  'image', 'difficulty', 'difficulty_display', 'light_requirement', 'light_display',
                  'water_requirement', 'water_display', 'tags', 'view_count', 'is_active']
    
    def get_tags(self, obj):
        tag_relations = obj.tag_relations.select_related('tag')
        return [{'id': tr.tag.id, 'name': tr.tag.name, 'color': tr.tag.color} 
                for tr in tag_relations]


class PlantDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    light_display = serializers.CharField(source='get_light_requirement_display', read_only=True)
    water_display = serializers.CharField(source='get_water_requirement_display', read_only=True)
    tags = serializers.SerializerMethodField()
    tag_ids = serializers.SerializerMethodField()
    is_collected = serializers.SerializerMethodField()
    
    class Meta:
        model = Plant
        fields = '__all__'
    
    def get_tags(self, obj):
        tag_relations = obj.tag_relations.select_related('tag')
        return [{'id': tr.tag.id, 'name': tr.tag.name, 'color': tr.tag.color} 
                for tr in tag_relations]

    def get_tag_ids(self, obj):
        return list(obj.tag_relations.values_list('tag_id', flat=True))
    
    def get_is_collected(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserPlant.objects.filter(user=request.user, plant=obj).exists()
        return False


class PlantAdminSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    tag_ids = serializers.SerializerMethodField()
    selected_tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
    )
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Plant
        fields = [
            'id', 'name', 'scientific_name', 'alias', 'category', 'category_name', 'image',
            'description', 'difficulty', 'light_requirement', 'water_requirement',
            'temperature_min', 'temperature_max', 'humidity', 'soil_requirement',
            'fertilizer_tips', 'pruning_tips', 'propagation', 'common_problems',
            'care_tips', 'is_active', 'view_count', 'created_at', 'updated_at',
            'tags', 'tag_ids', 'selected_tag_ids'
        ]
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at', 'tags', 'tag_ids']

    def get_tag_ids(self, obj):
        return list(obj.tag_relations.values_list('tag_id', flat=True))

    def get_tags(self, obj):
        tag_relations = obj.tag_relations.select_related('tag')
        return [{'id': tr.tag.id, 'name': tr.tag.name, 'color': tr.tag.color}
                for tr in tag_relations]

    def _sync_tags(self, plant, tag_ids):
        if tag_ids is None:
            return

        valid_tag_ids = list(PlantTag.objects.filter(id__in=tag_ids).values_list('id', flat=True))
        PlantTagRelation.objects.filter(plant=plant).exclude(tag_id__in=valid_tag_ids).delete()

        existing_tag_ids = set(PlantTagRelation.objects.filter(plant=plant).values_list('tag_id', flat=True))
        PlantTagRelation.objects.bulk_create([
            PlantTagRelation(plant=plant, tag_id=tag_id)
            for tag_id in valid_tag_ids
            if tag_id not in existing_tag_ids
        ])

    def create(self, validated_data):
        tag_ids = validated_data.pop('selected_tag_ids', [])
        plant = Plant.objects.create(**validated_data)
        self._sync_tags(plant, tag_ids)
        return plant

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('selected_tag_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._sync_tags(instance, tag_ids)
        return instance


class UserPlantSerializer(serializers.ModelSerializer):
    plant_detail = PlantListSerializer(source='plant', read_only=True)
    
    class Meta:
        model = UserPlant
        fields = ['id', 'plant', 'plant_detail', 'nickname', 'notes', 'acquired_date', 'created_at']
        read_only_fields = ['id', 'created_at']


class CareRecordSerializer(serializers.ModelSerializer):
    care_type_display = serializers.CharField(source='get_care_type_display', read_only=True)
    plant_name = serializers.CharField(source='user_plant.plant.name', read_only=True)
    
    class Meta:
        model = CareRecord
        fields = ['id', 'user_plant', 'plant_name', 'care_type', 'care_type_display',
                  'description', 'image', 'care_date', 'created_at']
        read_only_fields = ['id', 'created_at']
