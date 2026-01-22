from django.db import models
from django.conf import settings
from apps.core.models import TimestampMixin


class Subscription(TimestampMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    stripe_customer_id = models.CharField(max_length=255, db_index=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    stripe_price_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('active', 'Active'),
            ('past_due', 'Past Due'),
            ('canceled', 'Canceled'),
            ('unpaid', 'Unpaid'),
            ('trialing', 'Trialing'),
            ('incomplete', 'Incomplete'),
        ],
        default='active',
        db_index=True
    )
    plan = models.CharField(
        max_length=50,
        choices=[
            ('pro_monthly', 'Pro Monthly'),
            ('pro_yearly', 'Pro Yearly'),
            ('enterprise_monthly', 'Enterprise Monthly'),
            ('enterprise_yearly', 'Enterprise Yearly'),
        ],
        null=True,
        blank=True
    )
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'billing_subscription'
    
    def __str__(self):
        return f"Subscription({self.user.email}, {self.plan}, {self.status})"


class RateLimitLog(TimestampMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rate_limit_logs'
    )
    endpoint = models.CharField(max_length=255, default='api')
    requests_count = models.IntegerField(default=1)
    tokens_used = models.IntegerField(default=0)
    window_start = models.DateTimeField(db_index=True)
    
    class Meta:
        db_table = 'billing_ratelimitlog'
        unique_together = ['user', 'window_start']
    
    def __str__(self):
        return f"RateLimitLog({self.user.email}, {self.window_start})"


class UsageRecord(TimestampMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )
    stripe_usage_record_id = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    action = models.CharField(max_length=100)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'billing_usagerecord'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"UsageRecord({self.user.email}, {self.action}, {self.quantity})"


class Invoice(TimestampMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    stripe_invoice_id = models.CharField(max_length=255, unique=True)
    amount_due = models.IntegerField(default=0)
    amount_paid = models.IntegerField(default=0)
    status = models.CharField(max_length=50)
    invoice_url = models.URLField(max_length=500, null=True, blank=True)
    invoice_pdf = models.URLField(max_length=500, null=True, blank=True)
    period_start = models.DateTimeField(null=True, blank=True)
    period_end = models.DateTimeField(null=True, blank=True)
    hosted_invoice_url = models.URLField(max_length=500, null=True, blank=True)
    
    class Meta:
        db_table = 'billing_invoice'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice({self.user.email}, {self.amount_due/100:.2f}, {self.status})"
