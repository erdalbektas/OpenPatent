from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
import logging
from apps.api.middleware import RateLimiter
from apps.sessions.session_store import SessionStore

logger = logging.getLogger(__name__)


class RateLimitMixin:
    """Mixin to add rate limiting to views."""
    
    def check_rate_limit(self, request, tokens: int = 0):
        """Check rate limit and return error response if exceeded."""
        user = request.user
        
        if not user or not user.is_authenticated:
            return None
        
        allowed, info = RateLimiter.check_rate_limit(
            user_id=user.id,
            tokens=tokens,
            max_requests=user.requests_per_hour,
            max_tokens=user.tokens_per_hour
        )
        
        if not allowed:
            response = Response(info, status=429)
            response['Retry-After'] = info.get('retry_after', 3600)
            return response
        
        return None


class HealthView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'openpatent-api',
            'version': '0.0.3',
        })


@method_decorator(csrf_exempt, name='dispatch')
class SessionListView(RateLimitMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        sessions = SessionStore.list(
            user_id=str(request.user.id),
            limit=limit,
            offset=offset
        )
        
        rate_limit_error = self.check_rate_limit(request)
        if rate_limit_error:
            return rate_limit_error
        
        return Response({
            'sessions': sessions,
            'limit': limit,
            'offset': offset,
        })
    
    def post(self, request):
        title = request.data.get('title', 'New Session')
        
        rate_limit_error = self.check_rate_limit(request)
        if rate_limit_error:
            return rate_limit_error
        
        session = SessionStore.create(
            user_id=str(request.user.id),
            title=title
        )
        
        return Response(session, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class SessionDetailView(RateLimitMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, session_id):
        session = SessionStore.get(session_id)
        
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        
        if session.get('user_id') != str(request.user.id):
            return Response({'error': 'Not authorized'}, status=403)
        
        rate_limit_error = self.check_rate_limit(request)
        if rate_limit_error:
            return rate_limit_error
        
        return Response(session)
    
    def delete(self, request, session_id):
        session = SessionStore.get(session_id)
        
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        
        if session.get('user_id') != str(request.user.id):
            return Response({'error': 'Not authorized'}, status=403)
        
        SessionStore.delete(session_id)
        
        return Response({'deleted': True})


@method_decorator(csrf_exempt, name='dispatch')
class SessionShareView(RateLimitMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, session_id):
        session = SessionStore.get(session_id)
        
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        
        if session.get('user_id') != str(request.user.id):
            return Response({'error': 'Not authorized'}, status=403)
        
        share_info = SessionStore.share(session_id)
        
        return Response(share_info)
    
    def delete(self, request, session_id):
        session = SessionStore.get(session_id)
        
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        
        if session.get('user_id') != str(request.user.id):
            return Response({'error': 'Not authorized'}, status=403)
        
        SessionStore.unshare(session_id)
        
        return Response({'unshared': True})


@method_decorator(csrf_exempt, name='dispatch')
class SessionMessagesView(RateLimitMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, session_id):
        session = SessionStore.get(session_id)
        
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        
        if session.get('user_id') != str(request.user.id):
            return Response({'error': 'Not authorized'}, status=403)
        
        messages = SessionStore.get_messages(session_id)
        
        return Response({'messages': messages})
    
    def post(self, request, session_id):
        session = SessionStore.get(session_id)
        
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        
        if session.get('user_id') != str(request.user.id):
            return Response({'error': 'Not authorized'}, status=403)
        
        message_data = request.data
        
        tokens = message_data.get('tokens', {}).get('input', 0) + message_data.get('tokens', {}).get('output', 0)
        
        rate_limit_error = self.check_rate_limit(request, tokens=tokens)
        if rate_limit_error:
            return rate_limit_error
        
        message = SessionStore.add_message(session_id, message_data)
        
        return Response(message, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class UsageView(RateLimitMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        usage = RateLimiter.get_usage(
            user_id=request.user.id,
            max_requests=request.user.requests_per_hour,
            max_tokens=request.user.tokens_per_hour
        )
        
        return Response({
            'usage': usage,
            'limits': {
                'requests_per_hour': request.user.requests_per_hour,
                'tokens_per_hour': request.user.tokens_per_hour,
            },
            'tier': request.user.subscription_tier,
        })


@method_decorator(csrf_exempt, name='dispatch')
class PublicShareView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, session_id):
        secret = request.query_params.get('secret')
        
        if not secret:
            return Response({'error': 'Secret required'}, status=400)
        
        if not SessionStore.validate_share(session_id, secret):
            return Response({'error': 'Invalid or expired share link'}, status=403)
        
        session = SessionStore.get(session_id)
        
        if not session:
            return Response({'error': 'Session not found'}, status=404)
        
        messages = SessionStore.get_messages(session_id)
        
        return Response({
            'info': session,
            'messages': messages,
        })
