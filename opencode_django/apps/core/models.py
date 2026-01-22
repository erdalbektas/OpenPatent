from django.db import models
from django.conf import settings


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RateLimitMixin(models.Model):
    requests_per_hour = models.IntegerField(default=100)
    tokens_per_hour = models.IntegerField(default=100000)

    class Meta:
        abstract = True


def get_default_rate_limit():
    return {'requests': 100, 'tokens': 100000}
