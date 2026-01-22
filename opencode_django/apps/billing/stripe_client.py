import stripe
import logging
from django.conf import settings
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeClient:
    
    @staticmethod
    def create_customer(user) -> str:
        """Create a Stripe customer for a user."""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name() or user.username,
                metadata={
                    'user_id': user.id,
                    'username': user.username,
                }
            )
            logger.info(f"Created Stripe customer {customer.id} for user {user.id}")
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise
    
    @staticmethod
    def get_or_create_customer(user) -> str:
        """Get existing or create new Stripe customer."""
        if user.stripe_customer_id:
            return user.stripe_customer_id
        
        customer_id = StripeClient.create_customer(user)
        return customer_id
    
    @staticmethod
    def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        user_id: int = None
    ) -> dict:
        """Create a Stripe checkout session for subscription."""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                allow_promotion_codes=True,
                metadata={
                    'user_id': user_id,
                } if user_id else {}
            )
            logger.info(f"Created checkout session {session.id}")
            return {
                'session_id': session.id,
                'url': session.url,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise
    
    @staticmethod
    def create_portal_session(customer_id: str, return_url: str) -> dict:
        """Create a Stripe billing portal session."""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            logger.info(f"Created portal session for customer {customer_id}")
            return {
                'url': session.url,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create portal session: {e}")
            raise
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> dict:
        """Cancel a subscription."""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            logger.info(f"Canceled subscription {subscription_id}")
            return {
                'id': subscription.id,
                'status': subscription.status,
                'cancel_at_period_end': subscription.cancel_at_period_end,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise
    
    @staticmethod
    def get_subscription(subscription_id: str) -> dict:
        """Get subscription details."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'canceled_at': subscription.canceled_at,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscription: {e}")
            raise
    
    @staticmethod
    def construct_webhook_event(payload: bytes, signature: str) -> stripe.Event:
        """Construct a webhook event from payload and signature."""
        try:
            return stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            raise
        except Exception as e:
            logger.error(f"Webhook construction error: {e}")
            raise
    
    @staticmethod
    def get_customer_portal_url(customer_id: str, return_url: str) -> str:
        """Get URL for Stripe customer portal."""
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session.url
    
    @staticmethod
    def get_plan_limits(price_id: str) -> dict:
        """Get rate limit configuration for a price ID."""
        price_plans = {
            settings.STRIPE_PRICE_ID_PRO: {
                'requests_per_hour': 500,
                'tokens_per_hour': 1000000,
                'tier': 'pro',
            },
            settings.STRIPE_PRICE_ID_ENTERPRISE: {
                'requests_per_hour': 2000,
                'tokens_per_hour': 5000000,
                'tier': 'enterprise',
            },
        }
        return price_plans.get(price_id, {
            'requests_per_hour': 100,
            'tokens_per_hour': 100000,
            'tier': 'free',
        })
