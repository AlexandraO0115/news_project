# news/permissions.py
"""
Custom permissions for the news app.

This module defines custom permission classes to control access to API views based on
user roles (Reader, Editor, Journalist) and object ownership.
"""
from rest_framework import permissions
from .models import CustomUser


class IsReader(permissions.BasePermission):
    """
    Allows access only to users with the Reader role.
    """

    def has_permission(self, request, view):
        """
        Check if the user has the 'Reader' role.

        :param request: The incoming request object.
        :type request: rest_framework.request.Request
        :param view: The view being accessed.
        :type view: rest_framework.views.APIView
        :return: True if the user is authenticated and is a Reader, False otherwise.
        :rtype: bool
        """
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == CustomUser.Role.READER
        )


class IsEditor(permissions.BasePermission):
    """
    Allows access only to users with the Editor role.
    """

    def has_permission(self, request, view):
        """
        Check if the user has the 'Editor' role.

        :param request: The incoming request object.
        :type request: rest_framework.request.Request
        :param view: The view being accessed.
        :type view: rest_framework.views.APIView
        :return: True if the user is authenticated and is an Editor, False otherwise.
        :rtype: bool
        """
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == CustomUser.Role.EDITOR
        )


class IsJournalist(permissions.BasePermission):
    """
    Allows access only to users with the Journalist role.
    """

    def has_permission(self, request, view):
        """
        Check if the user has the 'Journalist' role.

        :param request: The incoming request object.
        :type request: rest_framework.request.Request
        :param view: The view being accessed.
        :type view: rest_framework.views.APIView
        :return: True if the user is authenticated and is a Journalist, False otherwise.
        :rtype: bool
        """
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == CustomUser.Role.JOURNALIST
        )


class IsAuthorOrEditor(permissions.BasePermission):
    """
    Custom object-level permission to only allow the original author of an
    article/newsletter to edit it, UNLESS the user is an Editor (who has
    global override rights).
    """

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions.

        Allows read-only access for safe methods.
        Allows write access if the user is an Editor or the author of the object.

        :param request: The incoming request object.
        :type request: rest_framework.request.Request
        :param view: The view being accessed.
        :type view: rest_framework.views.APIView
        :param obj: The object being accessed.
        :type obj: news.models.Article or news.models.Newsletter
        :return: True if permission is granted, False otherwise.
        :rtype: bool
        """
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are granted to Editors automatically
        if request.user.role == CustomUser.Role.EDITOR:
            return True

        # Otherwise, the user must be the author of the object
        return obj.author == request.user
