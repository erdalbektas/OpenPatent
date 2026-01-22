from django.urls import path
from apps.billing.views import (
    CheckoutView,
    PortalView,
    WebhookView,
    SubscriptionStatusView,
    CancelSubscriptionView,
    PricingView,
)

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('portal/', PortalView.as_view(), name='portal'),
    path('webhook/', WebhookView.as_view(), name='webhook'),
    path('subscription/', SubscriptionStatusView.as_view(), name='subscription-status'),
    path('cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('pricing/', PricingView.as_view(), name='pricing'),
]
