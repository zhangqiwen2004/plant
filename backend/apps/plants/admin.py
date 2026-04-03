from django.contrib import admin

from .models import PlantCategory, Plant, PlantTag, PlantTagRelation


@admin.register(PlantCategory)
class PlantCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name']


class PlantTagRelationInline(admin.TabularInline):
    model = PlantTagRelation
    extra = 1


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'difficulty', 'view_count', 'is_active']
    list_filter = ['category', 'difficulty', 'is_active']
    search_fields = ['name', 'scientific_name', 'alias']
    inlines = [PlantTagRelationInline]


@admin.register(PlantTag)
class PlantTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']
