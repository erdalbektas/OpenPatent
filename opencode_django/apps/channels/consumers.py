import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class SharePollConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for share polling."""
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.secret = self.scope['query_string'].decode().get('secret', '')
        
        try:
            valid = await self.validate_share()
            if not valid:
                logger.warning(f"Invalid share attempt for session {self.session_id}")
                await self.close(code=4004)
                return
            
            self.group_name = f'share_{self.session_id}'
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
            
            session_data = await self.get_session_data()
            if session_data:
                await self.send_json({
                    'key': 'session/info',
                    'content': session_data,
                })
            
            messages = await self.get_messages()
            for msg in messages:
                await self.send_json({
                    'key': f'session/message/{self.session_id}/{msg["id"]}',
                    'content': msg,
                })
            
            logger.info(f"WebSocket connected for share {self.session_id}")
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            await self.close(code=4000)
    
    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"WebSocket disconnected for share {self.session_id}")
        except Exception as e:
            logger.error(f"WebSocket disconnect error: {e}")
    
    async def receive_json(self, content):
        try:
            msg_type = content.get('type')
            
            if msg_type == 'ping':
                await self.send_json({'type': 'pong'})
            elif msg_type == 'subscribe':
                await self.send_json({
                    'type': 'subscribed',
                    'session_id': self.session_id,
                })
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")
    
    async def session_info(self, event):
        """Handle session info updates."""
        await self.send_json({
            'key': 'session/info',
            'content': event['content'],
        })
    
    async def session_message(self, event):
        """Handle message updates."""
        await self.send_json({
            'key': f'session/message/{event["session_id"]}/{event["message_id"]}',
            'content': event['content'],
        })
    
    async def session_part(self, event):
        """Handle part updates."""
        await self.send_json({
            'key': f'session/part/{event["session_id"]}/{event["message_id"]}/{event["part_id"]}',
            'content': event['content'],
        })
    
    @database_sync_to_async
    def validate_share(self) -> bool:
        """Validate the share secret."""
        from apps.sessions.session_store import SessionStore
        return SessionStore.validate_share(self.session_id, self.secret)
    
    @database_sync_to_async
    def get_session_data(self) -> dict:
        """Get session data."""
        from apps.sessions.session_store import SessionStore
        return SessionStore.get(self.session_id)
    
    @database_sync_to_async
    def get_messages(self) -> list:
        """Get all messages for the session."""
        from apps.sessions.session_store import SessionStore
        return SessionStore.get_messages(self.session_id)


class ShareSyncConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for share synchronization (internal use)."""
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f'sync_{self.session_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': content.get('type', 'session_message'),
                'key': content.get('key'),
                'content': content.get('content'),
                'session_id': self.session_id,
            }
        )
    
    async def session_info(self, event):
        await self.send_json({
            'key': event.get('key'),
            'content': event.get('content'),
        })
    
    async def session_message(self, event):
        await self.send_json({
            'key': event.get('key'),
            'content': event.get('content'),
        })
    
    async def session_part(self, event):
        await self.send_json({
            'key': event.get('key'),
            'content': event.get('content'),
        })
