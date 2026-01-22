from django.contrib import admin
from .models import (
    PatentSession,
    PremiumAgentUsage,
    SubscriptionQuota,
    PriorArtReference,
    OfficeAction,
    ClaimDraft,
    AgentDefinition,
    AgentVersion,
)


@admin.register(AgentDefinition)
class AgentDefinitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'agent_type', 'category', 'is_active', 'is_published', 'current_version']
    list_filter = ['agent_type', 'category', 'is_active', 'is_published']
    search_fields = ['id', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AgentVersion)
class AgentVersionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'version', 'changelog', 'is_active_version', 'created_at']
    list_filter = ['agent', 'is_active_version']
    search_fields = ['changelog']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PatentSession)
class PatentSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'status', 'is_premium', 'created_at']
    list_filter = ['status', 'is_premium', 'created_at']
    search_fields = ['title', 'id', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PremiumAgentUsage)
class PremiumAgentUsageAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'agent_type', 'status', 'tokens_used', 'created_at']
    list_filter = ['agent_type', 'status', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SubscriptionQuota)
class SubscriptionQuotaAdmin(admin.ModelAdmin):
    list_display = ['user', 'tier', 'mock_examiner_used', 'office_action_used', 'claim_strategy_used', 'specification_perfection_used']
    list_filter = ['tier']
    search_fields = ['user__email']


@admin.register(PriorArtReference)
class PriorArtReferenceAdmin(admin.ModelAdmin):
    list_display = ['session', 'title', 'source', 'relevance_score']
    list_filter = ['source', 'created_at']
    search_fields = ['title']


@admin.register(OfficeAction)
class OfficeActionAdmin(admin.ModelAdmin):
    list_display = ['session', 'action_type', 'status', 'created_at']
    list_filter = ['action_type', 'status', 'created_at']


@admin.register(ClaimDraft)
class ClaimDraftAdmin(admin.ModelAdmin):
    list_display = ['session', 'claim_number', 'claim_type', 'status']
    list_filter = ['claim_type', 'status']
