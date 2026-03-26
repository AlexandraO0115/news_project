# news/decorators.py
"""
Decorators for the news app.

This module provides custom decorators to restrict access to views based on
user roles (Editor, Journalist).
"""
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from .models import CustomUser


def editor_required(
    function=None, redirect_field_name=None, login_url="login"
):
    """
    Decorator for views that checks that the user is logged in and is an editor.

    If the user is authenticated but not an editor, a PermissionDenied
    exception is raised. If not authenticated, redirects to login.

    :param function: The view function to decorate.
    :type function: function
    :param redirect_field_name: The name of the field storing the redirect URL.
    :type redirect_field_name: str
    :param login_url: The URL to redirect to if not authenticated.
    :type login_url: str
    :return: The decorated function.
    :rtype: function
    """
    def check_user(user):
        if user.is_authenticated and user.role == CustomUser.Role.EDITOR:
            return True
        raise PermissionDenied

    actual_decorator = user_passes_test(
        check_user,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def journalist_required(
    function=None, redirect_field_name=None, login_url="login"
):
    """
    Decorator for views that checks that the user is logged in and is a journalist.

    If the user is authenticated but not a journalist, a PermissionDenied
    exception is raised. If not authenticated, redirects to login.

    :param function: The view function to decorate.
    :type function: function
    :param redirect_field_name: The name of the field storing the redirect URL.
    :type redirect_field_name: str
    :param login_url: The URL to redirect to if not authenticated.
    :type login_url: str
    :return: The decorated function.
    :rtype: function
    """
    def check_user(user):
        if user.is_authenticated and user.role == CustomUser.Role.JOURNALIST:
            return True
        raise PermissionDenied

    actual_decorator = user_passes_test(
        check_user,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
