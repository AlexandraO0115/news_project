# news/models.py
"""
Database models for the news app.

This module defines the database schema for the application, including custom users,
publishers, articles, and newsletters.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class Publisher(models.Model):
    """
    Model representing a publication/publisher.

    Publishers can have multiple editors and journalists assigned to them.

    :ivar name: The name of the publisher.
    :vartype name: str
    :ivar description: A description of the publisher.
    :vartype description: str
    :ivar created_at: The timestamp when the publisher was created.
    :vartype created_at: datetime
    """

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return the string representation of the publisher (its name).

        :return: The publisher's name.
        :rtype: str
        """
        return self.name


class CustomUser(AbstractUser):
    """
    Custom user model handling Readers, Editors, and Journalists.

    This model extends the default Django AbstractUser to include roles and subscriptions.

    :ivar email: The unique email address of the user.
    :vartype email: str
    :ivar role: The role of the user (Reader, Editor, or Journalist).
    :vartype role: str
    :ivar subscribed_publishers: Publishers the user is subscribed to (if Reader).
    :vartype subscribed_publishers: django.db.models.query.QuerySet
    :ivar subscribed_journalists: Journalists the user is subscribed to (if Reader).
    :vartype subscribed_journalists: django.db.models.query.QuerySet
    :ivar publisher_affiliation: The publisher the user works for (if Editor or Journalist).
    :vartype publisher_affiliation: Publisher
    """

    class Role(models.TextChoices):
        """
        Enumeration for user roles.

        Defines the three main user roles: Reader, Editor, and Journalist.
        """
        READER = "reader", "Reader"
        EDITOR = "editor", "Editor"
        JOURNALIST = "journalist", "Journalist"

    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "A user with that email address already exists.",
        },
    )
    role = models.CharField(
        max_length=15, choices=Role.choices, default=Role.READER
    )

    # Subscriptions (Applicable to Readers).
    subscribed_publishers = models.ManyToManyField(
        Publisher, related_name="reader_subscribers", blank=True
    )
    subscribed_journalists = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="reader_subscribers",
        blank=True,
    )

    # Affiliation (For Editors and Journalists working for a publisher).
    publisher_affiliation = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff",
    )

    def __str__(self):
        """
        Return the string representation of the user.

        :return: The username and role.
        :rtype: str
        """
        return f"{self.username} - {self.get_role_display()}"

    def save(self, *args, **kwargs):
        """
        Override the save method to enforce role-based field restrictions.

        Ensures that Journalists/Editors cannot have Reader subscriptions,
        and Readers cannot have Publisher affiliations.

        :param args: Variable length argument list.
        :param kwargs: Arbitrary keyword arguments.
        """
        super().save(*args, **kwargs)

        # If the user is NOT a Reader, they cannot have subscriptions.
        if self.role != self.Role.READER:
            # Clear ManyToMany fields (which acts as setting them to 'None'/empty).
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()

        # If the user IS a Reader, they cannot have a publisher affiliation.
        if self.role == self.Role.READER:
            if self.publisher_affiliation is not None:
                self.publisher_affiliation = None
                # Save again to apply the nullified affiliation without triggering M2M clears.
                super().save(update_fields=["publisher_affiliation"])

    # Custom properties to enforce the 'None' rule based on roles.
    @property
    def reader_publisher_subscriptions(self):
        """
        Get the publisher subscriptions for a Reader.

        :return: A queryset of subscribed publishers or None if not a Reader.
        :rtype: django.db.models.query.QuerySet or None
        """
        if self.role == self.Role.READER:
            return self.subscribed_publishers.all()
        return None

    @property
    def reader_journalist_subscriptions(self):
        """
        Get the journalist subscriptions for a Reader.

        :return: A queryset of subscribed journalists or None if not a Reader.
        :rtype: django.db.models.query.QuerySet or None
        """
        if self.role == self.Role.READER:
            return self.subscribed_journalists.all()
        return None

    @property
    def independent_published_articles(self):
        """
        Get articles published independently by a Journalist.

        :return: A queryset of articles with no publisher or None if not a Journalist.
        :rtype: django.db.models.query.QuerySet or None
        """
        if self.role == self.Role.JOURNALIST:
            # Articles authored by this user with no publisher affiliation.
            return self.authored_articles.filter(publisher__isnull=True)
        return None

    @property
    def independent_published_newsletters(self):
        """
        Get newsletters published independently by a Journalist.

        :return: A queryset of newsletters with no publisher or None if not a Journalist.
        :rtype: django.db.models.query.QuerySet or None
        """
        if self.role == self.Role.JOURNALIST:
            return self.authored_newsletters.filter(publisher__isnull=True)
        return None


class Article(models.Model):
    """
    Model representing a news article.

    :ivar title: The title of the article.
    :vartype title: str
    :ivar content: The main content of the article.
    :vartype content: str
    :ivar author: The user who wrote the article.
    :vartype author: CustomUser
    :ivar publisher: The publisher associated with the article (optional).
    :vartype publisher: Publisher
    :ivar is_approved: Whether the article has been approved by an editor.
    :vartype is_approved: bool
    :ivar created_at: The timestamp when the article was created.
    :vartype created_at: datetime
    :ivar updated_at: The timestamp when the article was last updated.
    :vartype updated_at: datetime
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="authored_articles"
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="published_articles",
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Return the string representation of the article (its title).

        :return: The article title.
        :rtype: str
        """
        return self.title


class Newsletter(models.Model):
    """
    Model representing a newsletter.

    :ivar title: The title/subject of the newsletter.
    :vartype title: str
    :ivar content: The content of the newsletter.
    :vartype content: str
    :ivar author: The user who wrote the newsletter.
    :vartype author: CustomUser
    :ivar publisher: The publisher associated with the newsletter (optional).
    :vartype publisher: Publisher
    :ivar is_approved: Whether the newsletter has been approved by an editor.
    :vartype is_approved: bool
    :ivar created_at: The timestamp when the newsletter was created.
    :vartype created_at: datetime
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="authored_newsletters",
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="published_newsletters",
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return the string representation of the newsletter.

        :return: A string indicating it is a newsletter and its title.
        :rtype: str
        """
        return f"Newsletter: {self.title}"
