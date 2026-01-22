from django.apps import AppConfig


class PatentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.patent'
    label = 'patent'
    verbose_name = 'OpenPatent Agents'
