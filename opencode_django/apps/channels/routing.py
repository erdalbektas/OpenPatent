from django.urls import re_path
from apps.channels.consumers import SharePollConsumer, ShareSyncConsumer

websocket_urlpatterns = [
    re_path(r'^ws/share/(?P<session_id>[0-9a-f-]+)/$', SharePollConsumer.as_asgi()),
    re_path(r'^ws/sync/(?P<session_id>[0-9a-f-]+)/$', ShareSyncConsumer.as_asgi()),
]
