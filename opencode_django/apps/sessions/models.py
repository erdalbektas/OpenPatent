import uuid
from django.db import models
from django.conf import settings
from apps.core.models import TimestampMixin


class Session(TimestampMixin):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    title = models.CharField(max_length=500, default='New Session')
    is_shared = models.BooleanField(default=False)
    share_secret = models.CharField(max_length=255, null=True, blank=True)
    version = models.CharField(max_length=50, default='0.0.1')
    time_created = models.BigIntegerField(default=0)
    time_updated = models.BigIntegerField(default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'sessions_session'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'deleted_at']),
            models.Index(fields=['is_shared']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.id})"
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)


class Message(TimestampMixin):
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    message_id = models.CharField(max_length=255)
    role = models.CharField(max_length=20)  # user, assistant, system
    content = models.JSONField(default=list)
    parts = models.JSONField(default=list)
    tokens_input = models.IntegerField(default=0)
    tokens_output = models.IntegerField(default=0)
    tokens_reasoning = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    provider_id = models.CharField(max_length=255, null=True, blank=True)
    model_id = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = 'sessions_message'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'message_id']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.message_id[:8]}..."
    
    class Meta:
        unique_together = ['session', 'message_id']


class Part(TimestampMixin):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='part_items'
    )
    part_id = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    content = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'sessions_part'
        unique_together = ['message', 'part_id']
    
    def __str__(self):
        return f"{self.part_id}: {self.type}"
