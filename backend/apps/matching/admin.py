from django.contrib import admin

from .models import MatchRecord, TagWeight


@admin.register(MatchRecord)
class MatchRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'matched_user', 'match_type', 'similarity_score', 'is_contacted', 'feedback']
    list_filter = ['match_type', 'is_contacted']
    search_fields = ['user__username', 'matched_user__username']


@admin.register(TagWeight)
class TagWeightAdmin(admin.ModelAdmin):
    list_display = ['tag_type', 'weight', 'description']
