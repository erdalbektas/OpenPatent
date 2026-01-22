import logging
from django.conf import settings
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.billing.stripe_client import StripeClient
from apps.billing.models import Subscription

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        price_id = request.data.get('price_id')
        
        if not price_id:
            return Response({'error': 'price_id is required'}, status=400)
        
        try:
            customer_id = StripeClient.get_or_create_customer(request.user)
            
            success_url = f"{settings.openpatent_API_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{settings.openpatent_API_URL}/billing/cancel"
            
            result = StripeClient.create_checkout_session(
                customer_id=customer_id,
                price_id=price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                user_id=request.user.id,
            )
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Checkout error: {e}")
            return Response({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PortalView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        try:
            subscription = Subscription.objects.get(user=request.user)
            
            if not subscription.stripe_customer_id:
                return Response({'error': 'No Stripe customer found'}, status=400)
            
            return_url = f"{settings.openpatent_API_URL}/billing/portal"
            
            result = StripeClient.create_portal_session(
                customer_id=subscription.stripe_customer_id,
                return_url=return_url,
            )
            
            return Response(result)
            
        except Subscription.DoesNotExist:
            return Response({'error': 'No subscription found'}, status=404)
        except Exception as e:
            logger.error(f"Portal error: {e}")
            return Response({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    def post(self, request):
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        if not signature:
            return HttpResponse('Missing signature', status=400)
        
        try:
            event = StripeClient.construct_webhook_event(payload, signature)
            
            if event.type == 'checkout.session.completed':
                self.handle_checkout_completed(event.data.object)
            elif event.type == 'customer.subscription.created':
                self.handle_subscription_created(event.data.object)
            elif event.type == 'customer.subscription.updated':
                self.handle_subscription_updated(event.data.object)
            elif event.type == 'customer.subscription.deleted':
                self.handle_subscription_deleted(event.data.object)
            elif event.type == 'invoice.paid':
                self.handle_invoice_paid(event.data.object)
            elif event.type == 'invoice.payment_failed':
                self.handle_invoice_failed(event.data.object)
            
            return HttpResponse(status=200)
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return HttpResponse(str(e), status=400)
    
    def handle_checkout_completed(self, session):
        """Handle successful checkout."""
        user_id = session.metadata.get('user_id')
        if not user_id:
            return
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            
            with transaction.atomic():
                subscription = Subscription.objects.get_or_create(
                    user=user,
                    defaults={
                        'stripe_customer_id': session.customer,
                    }
                )[0]
                
                user.stripe_customer_id = session.customer
                user.save()
                
        except User.DoesNotExist:
            logger.error(f"User not found: {user_id}")
    
    def handle_subscription_created(self, subscription):
        """Handle new subscription."""
        self._update_subscription(subscription)
    
    def handle_subscription_updated(self, subscription):
        """Handle subscription update."""
        self._update_subscription(subscription)
    
    def handle_subscription_deleted(self, subscription):
        """Handle subscription cancellation."""
        self._update_subscription(subscription, canceled=True)
    
    def handle_invoice_paid(self, invoice):
        """Handle successful payment."""
        pass
    
    def handle_invoice_failed(self, invoice):
        """Handle failed payment."""
        logger.warning(f"Payment failed for invoice {invoice.id}")
    
    def _update_subscription(self, stripe_subscription, canceled=False):
        """Update local subscription from Stripe data."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(stripe_customer_id=stripe_subscription.customer)
        except User.DoesNotExist:
            logger.error(f"User not found for customer: {stripe_subscription.customer}")
            return
        
        with transaction.atomic():
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                defaults={
                    'stripe_customer_id': stripe_subscription.customer,
                    'stripe_subscription_id': stripe_subscription.id,
                    'stripe_price_id': stripe_subscription.items.data[0].price.id if stripe_subscription.items.data else None,
                    'status': stripe_subscription.status,
                    'plan': self._get_plan_name(stripe_subscription.items.data[0].price.id) if stripe_subscription.items.data else None,
                    'current_period_start': timezone.datetime.fromtimestamp(stripe_subscription.current_period_start),
                    'current_period_end': timezone.datetime.fromtimestamp(stripe_subscription.current_period_end),
                    'cancel_at_period_end': stripe_subscription.cancel_at_period_end,
                }
            )
            
            if not created:
                subscription.stripe_subscription_id = stripe_subscription.id
                subscription.stripe_price_id = stripe_subscription.items.data[0].price.id if stripe_subscription.items.data else None
                subscription.status = stripe_subscription.status
                subscription.current_period_start = timezone.datetime.fromtimestamp(stripe_subscription.current_period_start)
                subscription.current_period_end = timezone.datetime.fromtimestamp(stripe_subscription.current_period_end)
                subscription.cancel_at_period_end = stripe_subscription.cancel_at_period_end
                subscription.save()
            
            limits = StripeClient.get_plan_limits(subscription.stripe_price_id)
            
            user.subscription_tier = limits['tier']
            user.requests_per_hour = limits['requests_per_hour']
            user.tokens_per_hour = limits['tokens_per_hour']
            user.save()
    
    def _get_plan_name(self, price_id: str) -> str:
        """Map price ID to plan name."""
        if price_id == settings.STRIPE_PRICE_ID_PRO:
            return 'pro_monthly'
        elif price_id == settings.STRIPE_PRICE_ID_ENTERPRISE:
            return 'enterprise_monthly'
        return 'free'


@method_decorator(csrf_exempt, name='dispatch')
class SubscriptionStatusView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        try:
            subscription = Subscription.objects.get(user=request.user)
            return Response({
                'status': subscription.status,
                'plan': subscription.plan,
                'current_period_end': subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                'cancel_at_period_end': subscription.cancel_at_period_end,
            })
        except Subscription.DoesNotExist:
            return Response({
                'status': 'none',
                'plan': 'free',
            })


@method_decorator(csrf_exempt, name='dispatch')
class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        try:
            subscription = Subscription.objects.get(user=request.user)
            
            if not subscription.stripe_subscription_id:
                return Response({'error': 'No active subscription'}, status=400)
            
            result = StripeClient.cancel_subscription(subscription.stripe_subscription_id)
            
            subscription.cancel_at_period_end = True
            subscription.save()
            
            return Response(result)
            
        except Subscription.DoesNotExist:
            return Response({'error': 'No subscription found'}, status=404)
        except Exception as e:
            logger.error(f"Cancel subscription error: {e}")
            return Response({'error': str(e)}, status=500)


class PricingView(View):
    def get(self, request):
        return JsonResponse({
            'plans': [
                {
                    'id': 'free',
                    'name': 'Free',
                    'price': 0,
                    'requests_per_hour': 100,
                    'tokens_per_hour': 100000,
                },
                {
                    'id': 'pro_monthly',
                    'name': 'Pro',
                    'price_id': settings.STRIPE_PRICE_ID_PRO,
                    'price': 2900,
                    'requests_per_hour': 500,
                    'tokens_per_hour': 1000000,
                },
                {
                    'id': 'enterprise_monthly',
                    'name': 'Enterprise',
                    'price_id': settings.STRIPE_PRICE_ID_ENTERPRISE,
                    'price': 9900,
                    'requests_per_hour': 2000,
                    'tokens_per_hour': 5000000,
                },
            ]
        })
