from django.urls import path
from .views import get_config

urlpatterns = [
    path('config/', get_config, name='api_config'),
]