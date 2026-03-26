# news/tests.py
"""
Tests for the news app.

This module contains tests for the API endpoints and other functionalities
of the news application, ensuring correct behavior for subscriptions and access controls.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, Publisher, Article


class SubscribedArticleAPITests(APITestCase):
    """
    Test suite for the third-party RESTful API endpoint that retrieves
    articles based on a user's subscriptions.

    This test case verifies:
    - Unauthenticated access is forbidden.
    - Non-reader roles receive empty lists (as they don't have subscriptions).
    - Readers receive only approved articles from their subscriptions.
    """

    def setUp(self):
        """
        Set up the database state with Publishers, Users, and Articles
        before each test runs.

        Creates:
        - Two publishers (Tech, Sports)
        - Users with roles: Journalist, Editor, Reader
        - Subscriptions for the Reader (Tech Publisher, Alice Journalist)
        - Four articles with varying approval status and authorship to test filtering logic.
        """
        # 1. Create Publishers
        self.publisher_tech = Publisher.objects.create(name="Tech Weekly")
        self.publisher_sports = Publisher.objects.create(name="Daily Sports")

        # 2. Create Users (Roles: Journalist, Editor, Reader)
        self.journalist_bob = CustomUser.objects.create_user(
            username="bob_writes",
            password="password123",
            role=CustomUser.Role.JOURNALIST,
        )
        self.journalist_alice = CustomUser.objects.create_user(
            username="alice_indie",
            password="password123",
            role=CustomUser.Role.JOURNALIST,
        )
        self.reader_john = CustomUser.objects.create_user(
            username="john_reader",
            password="password123",
            role=CustomUser.Role.READER,
        )
        self.editor_sue = CustomUser.objects.create_user(
            username="sue_edits",
            password="password123",
            role=CustomUser.Role.EDITOR,
        )

        # 3. Set up Subscriptions for the Reader
        # John subscribes to "Tech Weekly" (Publisher) and "Alice" (Independent Journalist)
        self.reader_john.subscribed_publishers.add(self.publisher_tech)
        self.reader_john.subscribed_journalists.add(self.journalist_alice)

        # 4. Create Articles
        # Article 1: Published by Tech Weekly, Approved (John SHOULD see this)
        self.article_tech = Article.objects.create(
            title="New AI Model Released",
            content="Content about AI...",
            author=self.journalist_bob,
            publisher=self.publisher_tech,
            is_approved=True,
        )

        # Article 2: Independent by Alice, Approved (John SHOULD see this)
        self.article_alice = Article.objects.create(
            title="Life of an Indie Writer",
            content="Content about writing...",
            author=self.journalist_alice,
            is_approved=True,
        )

        # Article 3: Published by Daily Sports, Approved (John SHOULD NOT see this)
        self.article_sports = Article.objects.create(
            title="Football Championship",
            content="Content about sports...",
            author=self.journalist_bob,
            publisher=self.publisher_sports,
            is_approved=True,
        )

        # Article 4: Published by Tech Weekly, UNAPPROVED (John SHOULD NOT see this)
        self.article_unapproved = Article.objects.create(
            title="Draft Tech Article",
            content="Draft content...",
            author=self.journalist_bob,
            publisher=self.publisher_tech,
            is_approved=False,
        )

        # DRF Router automatically names the list endpoint basename-list
        self.url = reverse("subscribed-articles-list")

    def test_unauthenticated_access(self):
        """
        Ensure unauthenticated users cannot access the API.

        This test verifies that a request without authentication credentials
        returns a 403 Forbidden status code.
        """
        response = self.client.get(self.url)
        # Update this line to expect a 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_reader_access(self):
        """
        Ensure Editors or Journalists get an empty list.

        This test verifies that users with roles other than READER (e.g., EDITOR)
        receive an empty list from the endpoint, as the subscription logic
        is specific to Reader profiles.
        """
        self.client.force_authenticate(user=self.editor_sue)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_reader_subscription_results(self):
        """
        Ensure a Reader only receives appropriate articles.

        This test verifies that a Reader receives articles that are:
        1. From a Publisher they are subscribed to.
        2. From a Journalist they are subscribed to.
        3. Approved by an Editor.

        It also verifies that unapproved articles and articles from sources
        the user is not subscribed to are excluded.
        """
        self.client.force_authenticate(user=self.reader_john)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # John should only get 2 articles: Tech Weekly's and Alice's
        self.assertEqual(len(response.data), 2)

        # Extract the titles from the JSON response to verify the correct articles were returned
        returned_titles = [article["title"] for article in response.data]

        self.assertIn(self.article_tech.title, returned_titles)
        self.assertIn(self.article_alice.title, returned_titles)

        # Verify un-subscribed and unapproved articles are excluded
        self.assertNotIn(self.article_sports.title, returned_titles)
        self.assertNotIn(self.article_unapproved.title, returned_titles)
