# news/urls.py
"""
URL configuration for the news app.

This module defines the URL patterns for the news application, mapping URLs
to their corresponding views. It includes paths for:

*   Public article listing and details.
*   Journalist actions (creating articles).
*   Editor actions (dashboard, approving articles).
*   User authentication (registration, login, logout).
*   Subscription management.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public Views: Accessible by anyone.
    path("", views.article_list, name="article_list"),
    path("article/<int:pk>/", views.article_detail, name="article_detail"),
    path("newsletters/", views.newsletter_list, name="newsletter_list"),
    path(
        "newsletter/<int:pk>/",
        views.newsletter_detail,
        name="newsletter_detail",
    ),
    path("publishers/", views.publisher_list, name="publisher_list"),
    # Journalist Views: Dashboard and content creation.
    path(
        "journalist/dashboard/",
        views.journalist_dashboard,
        name="journalist_dashboard",
    ),
    # Article CRUD: Create, Update, Delete for Articles.
    path("article/create/", views.create_article, name="create_article"),
    path(
        "article/<int:pk>/update/", views.update_article, name="update_article"
    ),
    path(
        "article/<int:pk>/delete/", views.delete_article, name="delete_article"
    ),
    # Newsletter CRUD: Create, Update, Delete for Newsletters.
    path(
        "newsletter/create/", views.create_newsletter, name="create_newsletter"
    ),
    path(
        "newsletter/<int:pk>/update/",
        views.update_newsletter,
        name="update_newsletter",
    ),
    path(
        "newsletter/<int:pk>/delete/",
        views.delete_newsletter,
        name="delete_newsletter",
    ),
    # Editor Views: Dashboard and approval workflow.
    path(
        "editor/dashboard/",
        views.unapproved_articles,
        name="unapproved_articles",
    ),
    path(
        "editor/publisher/create/",
        views.create_publisher,
        name="create_publisher",
    ),
    path(
        "editor/approve/<int:pk>/",
        views.approve_article,
        name="approve_article",
    ),
    path(
        "editor/approve-newsletter/<int:pk>/",
        views.approve_newsletter,
        name="approve_newsletter",
    ),
    # Authentication: User management.
    # We map the custom register view here.
    path("register/", views.register, name="register"),
    # You can safely use Django's built-in login/logout views and point them
    # to your existing templates.
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="article_list"),
        name="logout",
    ),
    # Subscription Views: Managing subscriptions.
    path(
        "subscribe/<str:target_type>/<int:target_id>/",
        views.toggle_subscription,
        name="toggle_subscription",
    ),
]
