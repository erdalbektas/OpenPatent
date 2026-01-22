from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    
    subscription_tier = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('pro', 'Pro'),
            ('enterprise', 'Enterprise'),
        ],
        default='free',
        db_index=True
    )
    
    requests_per_hour = models.IntegerField(default=100)
    tokens_per_hour = models.IntegerField(default=100000)
    
    last_request_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'accounts_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['stripe_customer_id']),
            models.Index(fields=['subscription_tier']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def is_pro(self):
        return self.subscription_tier in ['pro', 'enterprise']
    
    @property
    def is_enterprise(self):
        return self.subscription_tier == 'enterprise'


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(max_length=200, blank=True)
    github_username = models.CharField(max_length=100, blank=True)
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_profile'
    
    def __str__(self):
        return f"Profile for {self.user.email}"
