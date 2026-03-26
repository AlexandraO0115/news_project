# news_project/urls.py
"""
Main URL configuration for the news_project.

This module defines the top-level URL routing for the Django project.
It delegates specific paths to the 'news' app and includes the Django admin
and authentication URLs.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin Panel
    path("admin/", admin.site.urls),
    # Third-Party REST API Endpoints
    path("api/", include("news.api_urls")),
    # Django's Built-in Auth URLs
    # (handles login, logout, password reset views automatically)
    path("accounts/", include("django.contrib.auth.urls")),
    # Main News App Frontend URLs
    path("", include("news.urls")),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
