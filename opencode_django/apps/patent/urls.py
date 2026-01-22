from django.urls import path
from apps.patent.views import (
    PremiumAgentView,
    PatentSessionView,
    PatentSessionDetailView,
    QuotaStatusView,
    PremiumAgentsListView,
    FreeAgentsConfigView,
    UnifiedAgentsListView,
    AgentDetailView,
    AgentCreateView,
    AgentUpdateView,
    OrchestratorPlanView,
    OrchestratorExecuteView,
    OrchestratorThinkingView,
    OrchestratorTemplatesView,
)

urlpatterns = [
    path('agents/premium/', PremiumAgentView.as_view(), name='premium-agent'),
    path('agents/premium/list/', PremiumAgentsListView.as_view(), name='premium-agents-list'),
    path('agents/free/config/', FreeAgentsConfigView.as_view(), name='free-agents-config'),
    path('agents/', UnifiedAgentsListView.as_view(), name='unified-agents'),
    path('agents/<str:agent_id>/', AgentDetailView.as_view(), name='agent-detail'),
    path('agents/create/', AgentCreateView.as_view(), name='agent-create'),
    path('agents/<str:agent_id>/update/', AgentUpdateView.as_view(), name='agent-update'),
    path('orchestrator/plan/', OrchestratorPlanView.as_view(), name='orchestrator-plan'),
    path('orchestrator/execute/', OrchestratorExecuteView.as_view(), name='orchestrator-execute'),
    path('orchestrator/thinking/<str:session_id>/', OrchestratorThinkingView.as_view(), name='orchestrator-thinking'),
    path('orchestrator/templates/', OrchestratorTemplatesView.as_view(), name='orchestrator-templates'),
    path('sessions/', PatentSessionView.as_view(), name='patent-sessions'),
    path('sessions/<str:session_id>/', PatentSessionDetailView.as_view(), name='patent-session-detail'),
    path('quota/', QuotaStatusView.as_view(), name='quota-status'),
]
