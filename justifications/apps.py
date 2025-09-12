from django.apps import AppConfig

class JustificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'justifications'
    def ready(self):
        from . import signals  # noqa
