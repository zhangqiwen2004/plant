from django.urls import path

from .views import MetadataView


urlpatterns = [
    path('', MetadataView.as_view(), name='metadata'),
]
