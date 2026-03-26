# news/apps.py
"""
App configuration for the news app.

This module configures the 'news' application, including default auto field settings
and signal registration on startup.
"""
from django.apps import AppConfig


class NewsConfig(AppConfig):
    """
    Configuration class for the 'news' application.

    This class sets up the default auto field type and registers signals
    when the application is ready.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "news"

    def ready(self):
        """
        Perform application initialization tasks.

        This method is called when the app is fully loaded. It imports the
        `news.signals` module to ensure that signal handlers (receivers)
        are registered and active.
        """
        import news.signals
