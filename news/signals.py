"""
Signals for the news app.

Handles automatic assignment of users to Groups and ensures
those Groups have the exact permissions specified in the project outline.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import CustomUser, Article, Newsletter


def setup_group_permissions(group_name):
    """
    Helper function to assign specific model permissions to a group.

    Creates the group if it doesn't exist and assigns default permissions
    based on the group name (Reader, Editor, Journalist).

    :param group_name: The name of the group (e.g., 'Reader', 'Editor').
    :type group_name: str
    :return: The created or retrieved Group object.
    :rtype: django.contrib.auth.models.Group
    """
    group, created = Group.objects.get_or_create(name=group_name)

    # Only assign permissions if the group was just created to save database hits.
    if created:
        article_ct = ContentType.objects.get_for_model(Article)
        newsletter_ct = ContentType.objects.get_for_model(Newsletter)

        if group_name == "Reader":
            # Reader: Can only view articles and newsletters
            perms = Permission.objects.filter(
                content_type__in=[article_ct, newsletter_ct],
                codename__in=["view_article", "view_newsletter"],
            )
            group.permissions.add(*perms)

        elif group_name == "Editor":
            # Editor: Can view, update, and delete
            perms = Permission.objects.filter(
                content_type__in=[article_ct, newsletter_ct],
                codename__in=[
                    "view_article",
                    "change_article",
                    "delete_article",
                    "view_newsletter",
                    "change_newsletter",
                    "delete_newsletter",
                ],
            )
            group.permissions.add(*perms)

        elif group_name == "Journalist":
            # Journalist: Can create, view, update, and delete
            perms = Permission.objects.filter(
                content_type__in=[article_ct, newsletter_ct],
                codename__in=[
                    "add_article",
                    "view_article",
                    "change_article",
                    "delete_article",
                    "add_newsletter",
                    "view_newsletter",
                    "change_newsletter",
                    "delete_newsletter",
                ],
            )
            group.permissions.add(*perms)

    return group


@receiver(post_save, sender=CustomUser)
def assign_user_to_group(sender, instance, created, **kwargs):
    """
    Assigns a user to a Django Group based on their role after saving.

    This signal receiver listens for the post_save signal of CustomUser.
    It clears existing groups and adds the user to the group corresponding
    to their role.

    :param sender: The model class.
    :type sender: type
    :param instance: The actual instance being saved.
    :type instance: CustomUser
    :param created: A boolean; True if a new record was created.
    :type created: bool
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    """
    # Remove user from all groups first to prevent overlapping roles.
    instance.groups.clear()

    if instance.role == CustomUser.Role.READER:
        group = setup_group_permissions("Reader")
        instance.groups.add(group)

    elif instance.role == CustomUser.Role.EDITOR:
        group = setup_group_permissions("Editor")
        instance.groups.add(group)

    elif instance.role == CustomUser.Role.JOURNALIST:
        group = setup_group_permissions("Journalist")
        instance.groups.add(group)
