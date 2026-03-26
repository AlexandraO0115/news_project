# news/api_urls.py
"""
API URL configuration for the news app.

This module defines the URL patterns for the API, using Django REST Framework's
routers to automatically generate URLs for viewsets.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Use DefaultRouter to automatically generate the standard RESTful URL patterns.
router = DefaultRouter()

# This endpoint will handle the retrieval of articles for the API client
# based on their specific publisher and journalist subscriptions.
router.register(
    r"subscribed-articles",
    api_views.SubscribedArticleViewSet,
    basename="subscribed-articles",
)

urlpatterns = [
    # The API URLs will be accessible under whatever path you define in the
    # root urls.py (e.g., /api/subscribed-articles/).
    path("", include(router.urls)),
]
