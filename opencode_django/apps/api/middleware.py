import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from django.db import connection
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class RateLimiter:
    """PostgreSQL-based sliding window rate limiter."""
    
    WINDOW_SIZE = 3600  # 1 hour in seconds
    
    @staticmethod
    def get_window_start() -> datetime:
        """Get the start of the current rate limit window."""
        now = timezone.now()
        return now.replace(minute=0, second=0, microsecond=0)
    
    @staticmethod
    def check_rate_limit(
        user_id: int, 
        tokens: int = 0, 
        max_requests: int = 100,
        max_tokens: int = 100000
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check and update rate limits for a user.
        
        Uses PostgreSQL advisory locks for atomic operations.
        
        Returns:
            Tuple of (allowed, usage_info)
        """
        window_start = RateLimiter.get_window_start()
        window_key = int(window_start.timestamp())
        lock_id = user_id * 1000000000 + window_key
        
        with connection.cursor() as cursor:
            acquired = cursor.execute("SELECT pg_try_advisory_lock(%s)", [lock_id])
            
            if not acquired:
                logger.warning(f"Could not acquire lock for user {user_id}")
                return True, {'lock_wait': True}
            
            try:
                cursor.execute("""
                    SELECT requests_count, tokens_used 
                    FROM billing_ratelimitlog
                    WHERE user_id = %s AND window_start = %s
                """, [user_id, window_start])
                
                row = cursor.fetchone()
                
                if row:
                    requests_count, tokens_used = row
                else:
                    requests_count, tokens_used = 0, 0
                
                requests_remaining = max_requests - requests_count
                tokens_remaining = max_tokens - tokens_used
                
                if requests_count >= max_requests:
                    retry_after = 3600 - int((timezone.now() - window_start).total_seconds())
                    return False, {
                        'error': 'Rate limit exceeded',
                        'code': 'rate_limit_requests',
                        'retry_after': retry_after,
                        'limit': max_requests,
                        'reset_at': window_start.isoformat(),
                    }
                
                if tokens_used + tokens > max_tokens:
                    retry_after = 3600 - int((timezone.now() - window_start).total_seconds())
                    return False, {
                        'error': 'Token limit exceeded',
                        'code': 'rate_limit_tokens',
                        'retry_after': retry_after,
                        'limit': max_tokens,
                        'used': tokens_used,
                        'reset_at': window_start.isoformat(),
                    }
                
                cursor.execute("""
                    INSERT INTO billing_ratelimitlog 
                    (user_id, endpoint, requests_count, tokens_used, window_start, created_at, updated_at)
                    VALUES (%s, 'api', %s, %s, %s, NOW(), NOW())
                    ON CONFLICT (user_id, window_start) 
                    DO UPDATE SET 
                        requests_count = billing_ratelimitlog.requests_count + 1,
                        tokens_used = billing_ratelimitlog.tokens_used + %s,
                        updated_at = NOW()
                """, [user_id, requests_count + 1, tokens_used + tokens, window_start, tokens])
                
                return True, {
                    'requests_remaining': max_requests - requests_count - 1,
                    'tokens_remaining': max_tokens - tokens_used - tokens,
                    'reset_at': window_start.isoformat(),
                }
                
            finally:
                if acquired:
                    cursor.execute("SELECT pg_advisory_unlock(%s)", [lock_id])
    
    @staticmethod
    def get_usage(user_id: int, max_requests: int = 100, max_tokens: int = 100000) -> Dict[str, Any]:
        """Get current rate limit usage without incrementing."""
        window_start = RateLimiter.get_window_start()
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT requests_count, tokens_used, updated_at
                FROM billing_ratelimitlog
                WHERE user_id = %s AND window_start = %s
            """, [user_id, window_start])
            
            row = cursor.fetchone()
            
            if row:
                requests_count, tokens_used, updated_at = row
                return {
                    'requests_used': requests_count,
                    'requests_remaining': max_requests - requests_count,
                    'tokens_used': tokens_used,
                    'tokens_remaining': max_tokens - tokens_used,
                    'reset_at': window_start.isoformat(),
                    'window_start': window_start.isoformat(),
                }
            
            return {
                'requests_used': 0,
                'requests_remaining': max_requests,
                'tokens_used': 0,
                'tokens_remaining': max_tokens,
                'reset_at': window_start.isoformat(),
                'window_start': window_start.isoformat(),
            }


class JWTAuthBackend:
    """Custom JWT authentication for API views."""
    
    @staticmethod
    def authenticate(request) -> Tuple[Optional[Any], Optional[str]]:
        """
        Authenticate the request and return a user and token.
        """
        jwt_auth = JWTAuthentication()
        
        try:
            validated_token = jwt_auth.get_validated_token(
                jwt_auth.get_raw_token(jwt_auth.get_header(request)).decode()
            )
            user = jwt_auth.get_user(validated_token)
            return user, None
        except AuthenticationFailed:
            return None, "Invalid token"
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None, "Authentication failed"
    
    @staticmethod
    def get_user(user_id: int):
        """Get user by ID from validated token."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
