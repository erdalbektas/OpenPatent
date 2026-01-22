from django.apps import AppConfig


class SessionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sessions'
    label = 'openpatent_sessions'
    verbose_name = 'OpenPatent Sessions'
