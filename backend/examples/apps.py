from django.apps import AppConfig


class ExamplesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "examples"

    def ready(self):
        # Import signals to register them
        from . import signals  # noqa