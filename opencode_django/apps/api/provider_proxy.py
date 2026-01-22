import json
import logging
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
import httpx
from datetime import datetime
from apps.api.middleware import RateLimiter

logger = logging.getLogger(__name__)

MINIMAX_API_BASE = "https://api.minimax.chat/v1"


class MiniMaxProxyView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, endpoint):
        user = request.user
        
        rate_limit_error = self.check_rate_limit(request)
        if rate_limit_error:
            return rate_limit_error
        
        minimax_url = f"{MINIMAX_API_BASE}/{endpoint}"
        api_key = self._get_minimax_api_key(user)
        
        if not api_key:
            return Response({
                'error': 'MiniMax API key not configured',
                'message': 'Please configure your MiniMax API key in settings'
            }, status=400)
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'OpenPatent/1.0',
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    minimax_url,
                    json=request.data,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    return Response({
                        'error': f'MiniMax API error: {response.status_code}',
                        'detail': error_data.get('detail', response.text)
                    }, status=response.status_code)
                
                return StreamingHttpResponse(
                    response.iter_bytes(),
                    content_type='text/event-stream'
                )
                
        except httpx.TimeoutException:
            return Response({
                'error': 'MiniMax API timeout',
                'message': 'The request to MiniMax timed out'
            }, status=504)
        except Exception as e:
            logger.error(f"MiniMax proxy error: {e}")
            return Response({
                'error': 'Proxy error',
                'message': str(e)
            }, status=500)
    
    def check_rate_limit(self, request, tokens: int = 0):
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
    
    def _get_minimax_api_key(self, user):
        from apps.accounts.models import Profile
        try:
            profile = Profile.objects.get(user=user)
            return getattr(profile, 'minimax_api_key', None)
        except Profile.DoesNotExist:
            return None


class MiniMaxModelsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        return Response({
            'object': 'list',
            'data': [
                {'id': 'abab6.5s-chat', 'object': 'model', 'owned_by': 'MiniMax'},
                {'id': 'abab6.5-chat', 'object': 'model', 'owned_by': 'MiniMax'},
                {'id': 'abab2.5-chat', 'object': 'model', 'owned_by': 'MiniMax'},
            ]
        })


class ProviderCredentialView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        from apps.accounts.models import Profile
        try:
            profile = Profile.objects.get(user=request.user)
            credentials = getattr(profile, 'api_credentials', {}) or {}
            return Response({'providers': list(credentials.keys())})
        except Profile.DoesNotExist:
            return Response({'providers': []})
    
    def post(self, request):
        from apps.accounts.models import Profile
        from django.conf import settings
        
        provider = request.data.get('provider')
        api_key = request.data.get('api_key')
        
        if not provider or not api_key:
            return Response({'error': 'provider and api_key are required'}, status=400)
        
        allowed_providers = ['openai', 'anthropic', 'google', 'qwen', 'minimax']
        if provider not in allowed_providers:
            return Response({'error': f'Unsupported provider. Allowed: {allowed_providers}'}, status=400)
        
        try:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            
            if not hasattr(profile, 'api_credentials') or profile.api_credentials is None:
                profile.api_credentials = {}
            
            profile.api_credentials[provider] = {
                'api_key': api_key,
                'created_at': datetime.utcnow().isoformat(),
            }
            profile.save()
            
            return Response({'message': f'{provider} API key stored successfully'})
            
        except Exception as e:
            logger.error(f"Error storing credential: {e}")
            return Response({'error': 'Failed to store credential'}, status=500)
    
    def delete(self, request):
        from apps.accounts.models import Profile
        
        provider = request.query_params.get('provider')
        if not provider:
            return Response({'error': 'provider query parameter is required'}, status=400)
        
        try:
            profile = Profile.objects.get(user=request.user)
            if hasattr(profile, 'api_credentials') and profile.api_credentials:
                if provider in profile.api_credentials:
                    del profile.api_credentials[provider]
                    profile.save()
                    return Response({'message': f'{provider} API key removed'})
            return Response({'error': 'Provider not found'}, status=404)
            
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)


class LocalProviderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        from apps.accounts.models import Profile
        
        try:
            profile = Profile.objects.get(user=request.user)
            local_providers = getattr(profile, 'local_providers', []) or []
            
            sanitized = []
            for p in local_providers:
                p_copy = p.copy()
                if 'api_key' in p_copy:
                    del p_copy['api_key']
                sanitized.append(p_copy)
            
            return Response({'local_providers': sanitized})
        except Profile.DoesNotExist:
            return Response({'local_providers': []})
    
    def post(self, request):
        from apps.accounts.models import Profile
        
        provider_type = request.data.get('type')
        name = request.data.get('name')
        base_url = request.data.get('base_url')
        api_key = request.data.get('api_key', '')
        
        if not provider_type or not name or not base_url:
            return Response({'error': 'type, name, and base_url are required'}, status=400)
        
        allowed_types = ['lm-studio', 'ollama', 'openai-compatible']
        if provider_type not in allowed_types:
            return Response({'error': f'Unsupported type. Allowed: {allowed_types}'}, status=400)
        
        try:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            
            if not hasattr(profile, 'local_providers') or profile.local_providers is None:
                profile.local_providers = []
            
            new_provider = {
                'type': provider_type,
                'name': name,
                'base_url': base_url,
                'api_key': api_key,
                'models': [],
                'created_at': datetime.utcnow().isoformat(),
            }
            
            existing_idx = None
            for i, p in enumerate(profile.local_providers):
                if p.get('name') == name:
                    existing_idx = i
                    break
            
            if existing_idx is not None:
                profile.local_providers[existing_idx] = new_provider
            else:
                profile.local_providers.append(new_provider)
            
            profile.save()
            
            models = self._fetch_models_from_provider(base_url, api_key, provider_type)
            if models:
                for i, p in enumerate(profile.local_providers):
                    if p.get('name') == name:
                        profile.local_providers[i]['models'] = models
                        profile.save()
                        break
            
            return Response({'message': f'Local provider "{name}" added', 'provider': new_provider})
            
        except Exception as e:
            logger.error(f"Error adding local provider: {e}")
            return Response({'error': 'Failed to add local provider'}, status=500)
    
    def _fetch_models_from_provider(self, base_url, api_key, provider_type):
        try:
            with httpx.Client(timeout=10.0) as client:
                headers = {}
                if api_key:
                    headers['Authorization'] = f'Bearer {api_key}'
                
                if provider_type in ['lm-studio', 'openai-compatible']:
                    url = f"{base_url}/v1/models"
                else:
                    url = f"{base_url}/api/tags"
                
                response = client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if provider_type in ['lm-studio', 'openai-compatible']:
                        return [
                            {'id': m['id'], 'object': 'model', 'owned_by': provider_type}
                            for m in data.get('data', [])
                        ]
                    else:
                        return [
                            {'id': m.get('name', m.get('id')), 'object': 'model'}
                            for m in data.get('models', [])
                        ]
                return []
        except Exception as e:
            logger.warning(f"Could not fetch models from {base_url}: {e}")
            return []
    
    def delete(self, request):
        from apps.accounts.models import Profile
        
        name = request.query_params.get('name')
        if not name:
            return Response({'error': 'name query parameter is required'}, status=400)
        
        try:
            profile = Profile.objects.get(user=request.user)
            if hasattr(profile, 'local_providers') and profile.local_providers:
                profile.local_providers = [p for p in profile.local_providers if p.get('name') != name]
                profile.save()
                return Response({'message': f'Local provider "{name}" removed'})
            return Response({'error': 'Provider not found'}, status=404)
            
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)
