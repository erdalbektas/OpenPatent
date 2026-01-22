from django.urls import path
from apps.api.views import (
    HealthView,
    SessionListView,
    SessionDetailView,
    SessionShareView,
    SessionMessagesView,
    UsageView,
    PublicShareView,
)
from apps.api.provider_proxy import (
    MiniMaxProxyView,
    MiniMaxModelsView,
    ProviderCredentialView,
    LocalProviderView,
)

urlpatterns = [
    path('health/', HealthView.as_view(), name='api-health'),
    path('sessions/', SessionListView.as_view(), name='session-list'),
    path('sessions/<str:session_id>/', SessionDetailView.as_view(), name='session-detail'),
    path('sessions/<str:session_id>/share/', SessionShareView.as_view(), name='session-share'),
    path('sessions/<str:session_id>/messages/', SessionMessagesView.as_view(), name='session-messages'),
    path('usage/', UsageView.as_view(), name='usage'),
    path('share/<str:session_id>/', PublicShareView.as_view(), name='public-share'),
    path('providers/credentials/', ProviderCredentialView.as_view(), name='provider-credentials'),
    path('providers/local/', LocalProviderView.as_view(), name='local-providers'),
    path('minimax/models/', MiniMaxModelsView.as_view(), name='minimax-models'),
    path('minimax/chat/<str:endpoint>/', MiniMaxProxyView.as_view(), name='minimax-proxy'),
]
