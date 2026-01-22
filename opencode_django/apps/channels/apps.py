from django.apps import AppConfig


class ChannelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.channels'
    label = 'openpatent_channels'
    verbose_name = 'OpenPatent Channels'
