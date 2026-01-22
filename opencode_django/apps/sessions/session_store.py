import secrets
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)


class SessionStore:
    
    @staticmethod
    def create(user_id: str, title: str = "New Session") -> Dict[str, Any]:
        """Create a new session."""
        import uuid
        session_id = str(uuid.uuid4())
        current_time = int(datetime.utcnow().timestamp() * 1000)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sessions_session 
                (id, user_id, title, is_shared, version, time_created, time_updated, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, [session_id, user_id, title, False, '0.0.1', current_time, current_time])
        
        return SessionStore.get(session_id)
    
    @staticmethod
    def get(session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, title, is_shared, share_secret, version, 
                       time_created, time_updated, created_at, updated_at
                FROM sessions_session 
                WHERE id = %s AND deleted_at IS NULL
            """, [session_id])
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'user_id': row[1],
            'title': row[2],
            'is_shared': row[3],
            'share_secret': row[4],
            'version': row[5],
            'time': {
                'created': row[6],
                'updated': row[7],
            },
            'created_at': row[8].isoformat() if row[8] else None,
            'updated_at': row[9].isoformat() if row[9] else None,
        }
    
    @staticmethod
    def list(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List sessions for a user."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, user_id, title, is_shared, share_secret, version,
                       time_created, time_updated, created_at, updated_at
                FROM sessions_session 
                WHERE user_id = %s AND deleted_at IS NULL
                ORDER BY updated_at DESC
                LIMIT %s OFFSET %s
            """, [user_id, limit, offset])
            
            rows = cursor.fetchall()
        
        return [{
            'id': row[0],
            'user_id': row[1],
            'title': row[2],
            'is_shared': row[3],
            'share_secret': row[4],
            'version': row[5],
            'time': {
                'created': row[6],
                'updated': row[7],
            },
        } for row in rows]
    
    @staticmethod
    def update(session_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a session."""
        if not kwargs:
            return SessionStore.get(session_id)
        
        allowed_fields = {'title', 'version', 'time_created', 'time_updated'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        updates['updated_at'] = timezone.now()
        
        if 'time_updated' not in updates:
            updates['updated_at'] = int(datetime.utcnow().timestamp() * 1000)
        
        set_clauses = [f"{k} = %s" for k in updates.keys()]
        values = list(updates.values()) + [session_id]
        
        with connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE sessions_session 
                SET {', '.join(set_clauses)}, updated_at = NOW()
                WHERE id = %s AND deleted_at IS NULL
            """, values)
        
        return SessionStore.get(session_id)
    
    @staticmethod
    def delete(session_id: str) -> bool:
        """Soft delete a session."""
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE sessions_session 
                SET deleted_at = NOW()
                WHERE id = %s
            """, [session_id])
            return cursor.rowcount > 0
    
    @staticmethod
    def share(session_id: str) -> Dict[str, str]:
        """Create or get share secret for a session."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT share_secret FROM sessions_session 
                WHERE id = %s AND deleted_at IS NULL
            """, [session_id])
            row = cursor.fetchone()
        
        if not row:
            raise ValueError("Session not found")
        
        secret = row[0] or secrets.token_urlsafe(32)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE sessions_session 
                SET is_shared = TRUE, share_secret = %s, updated_at = NOW()
                WHERE id = %s
            """, [secret, session_id])
        
        return {'secret': secret, 'url': f'/share/{session_id}?secret={secret}'}
    
    @staticmethod
    def unshare(session_id: str) -> bool:
        """Remove share secret from a session."""
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE sessions_session 
                SET is_shared = FALSE, share_secret = NULL, updated_at = NOW()
                WHERE id = %s
            """, [session_id])
            return cursor.rowcount > 0
    
    @staticmethod
    def validate_share(session_id: str, secret: str) -> bool:
        """Validate a share secret."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM sessions_session 
                WHERE id = %s AND share_secret = %s AND is_shared = TRUE
            """, [session_id, secret])
            return cursor.fetchone() is not None
    
    @staticmethod
    def add_message(session_id: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a message to a session."""
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sessions_message 
                (session_id, message_id, role, content, parts, tokens_input, 
                 tokens_output, tokens_reasoning, cost, provider_id, model_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (session_id, message_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    parts = EXCLUDED.parts,
                    tokens_input = EXCLUDED.tokens_input,
                    tokens_output = EXCLUDED.tokens_output,
                    tokens_reasoning = EXCLUDED.tokens_reasoning,
                    cost = EXCLUDED.cost,
                    updated_at = NOW()
                RETURNING created_at, updated_at
            """, [
                session_id,
                message_data.get('id'),
                message_data.get('role'),
                message_data.get('content', []),
                message_data.get('parts', []),
                message_data.get('tokens', {}).get('input', 0),
                message_data.get('tokens', {}).get('output', 0),
                message_data.get('tokens', {}).get('reasoning', 0),
                message_data.get('cost', 0),
                message_data.get('provider_id'),
                message_data.get('model_id'),
            ])
            
            timestamps = cursor.fetchone()
            
            cursor.execute("""
                UPDATE sessions_session 
                SET time_updated = %s, updated_at = NOW()
                WHERE id = %s
            """, [message_data.get('time', {}).get('completed', 0) or int(datetime.utcnow().timestamp() * 1000), session_id])
        
        return {
            **message_data,
            'created_at': timestamps[0].isoformat() if timestamps[0] else None,
            'updated_at': timestamps[1].isoformat() if timestamps[1] else None,
        }
    
    @staticmethod
    def get_messages(session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT message_id, role, content, parts, tokens_input, 
                       tokens_output, tokens_reasoning, cost, provider_id, model_id,
                       created_at, updated_at
                FROM sessions_message 
                WHERE session_id = %s
                ORDER BY created_at ASC
            """, [session_id])
            
            rows = cursor.fetchall()
        
        return [{
            'id': row[0],
            'role': row[1],
            'content': row[2],
            'parts': row[3],
            'tokens': {
                'input': row[4],
                'output': row[5],
                'reasoning': row[6],
            },
            'cost': float(row[7]) if row[7] else 0,
            'provider_id': row[8],
            'model_id': row[9],
        } for row in rows]
    
    @staticmethod
    def get_message(session_id: str, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific message."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT message_id, role, content, parts, tokens_input, 
                       tokens_output, tokens_reasoning, cost, provider_id, model_id,
                       created_at, updated_at
                FROM sessions_message 
                WHERE session_id = %s AND message_id = %s
            """, [session_id, message_id])
            
            row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'role': row[1],
            'content': row[2],
            'parts': row[3],
            'tokens': {
                'input': row[4],
                'output': row[5],
                'reasoning': row[6],
            },
            'cost': float(row[7]) if row[7] else 0,
            'provider_id': row[8],
            'model_id': row[9],
        }
