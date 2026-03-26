# news/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Publisher, Article, Newsletter


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Customizes the admin panel view for the CustomUser model.

    This admin class extends the default UserAdmin to include specific roles,
    affiliations, and subscriptions associated with the custom user model.
    """

    list_display = (
        "username",
        "email",
        "role",
        "publisher_affiliation",
        "is_staff",
    )
    list_filter = (
        "role",
        "publisher_affiliation",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    search_fields = ("username", "email")

    # Adds our custom fields to the user editing screen in the admin panel
    fieldsets = UserAdmin.fieldsets + (
        (
            "Role & Affiliations",
            {
                "fields": ("role", "publisher_affiliation"),
            },
        ),
        (
            "Subscriptions (Readers)",
            {
                "fields": ("subscribed_publishers", "subscribed_journalists"),
                "description": "Only applicable if the user has the Reader role.",
            },
        ),
    )

    # Adds our custom fields to the user creation screen in the admin panel
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Role & Affiliations",
            {
                "fields": ("role", "publisher_affiliation"),
            },
        ),
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """
    Admin view for the Publisher model.

    Provides basic list display and search functionality for Publishers.
    """

    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin view for the Article model.

    Provides filtering by approval status, publisher, and creation date.
    Includes a custom action to batch approve articles.
    """

    list_display = (
        "title",
        "author",
        "publisher",
        "is_approved",
        "created_at",
    )
    list_filter = ("is_approved", "publisher", "created_at")
    search_fields = ("title", "content", "author__username")
    # Allows admin to approve multiple articles at once via the action dropdown
    actions = ["approve_articles"]

    @admin.action(description="Mark selected articles as approved")
    def approve_articles(self, request, queryset):
        """
        Action to approve selected articles.

        Updates the `is_approved` field to True for all selected articles in the queryset.

        :param request: The HTTP request object.
        :type request: django.http.HttpRequest
        :param queryset: The queryset of selected Article objects.
        :type queryset: django.db.models.query.QuerySet
        """
        queryset.update(is_approved=True)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Admin view for the Newsletter model.

    Provides filtering by approval status, publisher, and creation date.
    Includes a custom action to batch approve newsletters.
    """

    list_display = (
        "title",
        "author",
        "publisher",
        "is_approved",
        "created_at",
    )
    list_filter = ("is_approved", "publisher", "created_at")
    search_fields = ("title", "content", "author__username")
    actions = ["approve_newsletters"]

    @admin.action(description="Mark selected newsletters as approved")
    def approve_newsletters(self, request, queryset):
        """
        Action to approve selected newsletters.

        Updates the `is_approved` field to True for all selected newsletters in the queryset.

        :param request: The HTTP request object.
        :type request: django.http.HttpRequest
        :param queryset: The queryset of selected Newsletter objects.
        :type queryset: django.db.models.query.QuerySet
        """
        queryset.update(is_approved=True)
