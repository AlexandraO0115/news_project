# news/api_views.py
"""
API views for the news app.

This module defines the viewsets for the API, handling the retrieval of articles
and other resources.
"""
from rest_framework import viewsets, permissions
from django.db.models import Q
from .models import Article
from .serializers import ArticleSerializer


class SubscribedArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for retrieving subscribed articles.

    Allows a third-party client (authenticated user) to retrieve approved
    articles based on their specific publisher and journalist subscriptions.
    """

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get the queryset of articles for the current user.

        Filters articles based on the authenticated user's subscriptions
        (publishers and journalists). Only returns approved articles.
        If the user is not a Reader, returns an empty queryset.

        :return: A queryset of Article objects.
        :rtype: django.db.models.query.QuerySet
        """
        user = self.request.user

        # Only Reader roles have subscriptions in our model structure.
        if user.role != user.Role.READER:
            return Article.objects.none()

        # Fetch the user's specific subscriptions.
        subscribed_publishers = user.subscribed_publishers.all()
        subscribed_journalists = user.subscribed_journalists.all()

        # Filter for approved articles where the publisher is in the user's
        # publisher subscriptions OR the author is in their journalist subscriptions.
        queryset = (
            Article.objects.filter(
                Q(publisher__in=subscribed_publishers)
                | Q(author__in=subscribed_journalists),
                is_approved=True,
            )
            .order_by("-created_at")
            .distinct()
        )

        return queryset
