from django.db import models
from django.conf import settings
from apps.core.models import TimestampMixin


class PatentSession(TimestampMixin):
    """A patent drafting session containing invention details and drafts."""
    
    id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patent_sessions'
    )
    title = models.CharField(max_length=500)
    invention_title = models.CharField(max_length=500, blank=True)
    technical_field = models.CharField(max_length=500, blank=True)
    
    status = models.CharField(
        max_length=50,
        choices=[
            ('drafting', 'Drafting'),
            ('review', 'Under Review'),
            ('perfecting', 'Perfecting'),
            ('filed', 'Filed'),
            ('examining', 'Under Examination'),
            ('granted', 'Granted'),
            ('abandoned', 'Abandoned'),
        ],
        default='drafting'
    )
    
    invention_disclosure = models.JSONField(default=dict, blank=True)
    claims = models.JSONField(default=list, blank=True)
    specification = models.JSONField(default=dict, blank=True)
    drawings_description = models.TextField(blank=True)
    
    prior_art_references = models.JSONField(default=list, blank=True)
    office_actions = models.JSONField(default=list, blank=True)
    
    is_premium = models.BooleanField(default=False)
    premium_session_ref = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'patent_session'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} ({self.status})"


class PremiumAgentUsage(TimestampMixin):
    """Tracks usage of premium agents for quota management."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='premium_agent_usage'
    )
    
    session = models.ForeignKey(
        PatentSession,
        on_delete=models.CASCADE,
        related_name='agent_usage',
        null=True,
        blank=True
    )
    
    agent_type = models.CharField(
        max_length=50,
        choices=[
            ('mock_examiner', 'Mock Examiner'),
            ('office_action_response', 'Office Action Response'),
            ('claim_strategy', 'Claim Strategy'),
            ('specification_perfection', 'Specification Perfection'),
            ('patent_searcher', 'Patent Searcher'),
            ('patent_drafter', 'Patent Drafter'),
            ('patent_interrogator', 'Patent Interrogator'),
            ('patent_illustrator', 'Patent Illustrator'),
        ]
    )
    
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'patent_premium_agent_usage'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.agent_type} ({self.status})"


class SubscriptionQuota(TimestampMixin):
    """Manages subscription quotas for premium agents."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patent_quota'
    )
    
    tier = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('pro', 'Pro'),
            ('enterprise', 'Enterprise'),
        ],
        default='free'
    )
    
    mock_examiner_used = models.IntegerField(default=0)
    mock_examiner_limit = models.IntegerField(default=3)
    
    office_action_used = models.IntegerField(default=0)
    office_action_limit = models.IntegerField(default=0)
    
    claim_strategy_used = models.IntegerField(default=0)
    claim_strategy_limit = models.IntegerField(default=0)
    
    specification_perfection_used = models.IntegerField(default=0)
    specification_perfection_limit = models.IntegerField(default=0)
    
    patent_searcher_used = models.IntegerField(default=0)
    patent_searcher_limit = models.IntegerField(default=3)
    
    patent_drafter_used = models.IntegerField(default=0)
    patent_drafter_limit = models.IntegerField(default=3)
    
    patent_interrogator_used = models.IntegerField(default=0)
    patent_interrogator_limit = models.IntegerField(default=3)
    
    patent_illustrator_used = models.IntegerField(default=0)
    patent_illustrator_limit = models.IntegerField(default=3)
    
    reset_date = models.DateTimeField()
    
    class Meta:
        db_table = 'patent_subscription_quota'
    
    def __str__(self):
        return f"{self.user.email} - {self.tier}"
    
    def can_use_agent(self, agent_type: str) -> tuple[bool, int, int]:
        """Check if user can use a premium agent. Returns (allowed, used, limit)."""
        limits = {
            'mock_examiner': (self.mock_examiner_used, self.mock_examiner_limit),
            'office_action_response': (self.office_action_used, self.office_action_limit),
            'claim_strategy': (self.claim_strategy_used, self.claim_strategy_limit),
            'specification_perfection': (self.specification_perfection_used, self.specification_perfection_limit),
            'patent_searcher': (self.patent_searcher_used, self.patent_searcher_limit),
            'patent_drafter': (self.patent_drafter_used, self.patent_drafter_limit),
            'patent_interrogator': (self.patent_interrogator_used, self.patent_interrogator_limit),
            'patent_illustrator': (self.patent_illustrator_used, self.patent_illustrator_limit),
        }
        
        if agent_type not in limits:
            return False, 0, 0
        
        used, limit = limits[agent_type]
        return used < limit, used, limit
    
    def increment_usage(self, agent_type: str):
        """Increment usage for an agent type."""
        field_map = {
            'mock_examiner': 'mock_examiner_used',
            'office_action_response': 'office_action_used',
            'claim_strategy': 'claim_strategy_used',
            'specification_perfection': 'specification_perfection_used',
            'patent_searcher': 'patent_searcher_used',
            'patent_drafter': 'patent_drafter_used',
            'patent_interrogator': 'patent_interrogator_used',
            'patent_illustrator': 'patent_illustrator_used',
        }
        
        if agent_type in field_map:
            setattr(self, field_map[agent_type], getattr(self, field_map[agent_type]) + 1)
            self.save()


class PriorArtReference(TimestampMixin):
    """Stores prior art references for patent sessions."""
    
    session = models.ForeignKey(
        PatentSession,
        on_delete=models.CASCADE,
        related_name='prior_art'
    )
    
    title = models.CharField(max_length=500)
    source = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    relevance_score = models.FloatField(default=0.0)
    summary = models.TextField(blank=True)
    claims_affected = models.JSONField(default=list)
    
    class Meta:
        db_table = 'patent_prior_art'
    
    def __str__(self):
        return f"{self.title[:50]}..."


class OfficeAction(TimestampMixin):
    """Tracks office actions and responses."""
    
    session = models.ForeignKey(
        PatentSession,
        on_delete=models.CASCADE,
        related_name='office_actions_history'
    )
    
    action_type = models.CharField(
        max_length=50,
        choices=[
            ('rejection_101', '101 Rejection'),
            ('rejection_102', '102 Rejection'),
            ('rejection_103', '103 Rejection'),
            ('objection', 'Objection'),
            ('requirement', 'Requirement'),
            ('allowance', 'Allowance'),
        ]
    )
    
    content = models.TextField()
    response = models.TextField(blank=True)
    response_draft = models.JSONField(default=dict, blank=True)
    
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('drafting', 'Drafting'),
            ('filed', 'Filed'),
            ('responded', 'Responded'),
        ],
        default='pending'
    )
    
    examiner_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'patent_office_action'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.status}"


class ClaimDraft(TimestampMixin):
    """Stores individual claim drafts."""
    
    session = models.ForeignKey(
        PatentSession,
        on_delete=models.CASCADE,
        related_name='claim_drafts'
    )
    
    claim_number = models.IntegerField()
    claim_type = models.CharField(
        max_length=20,
        choices=[
            ('independent', 'Independent'),
            ('dependent', 'Dependent'),
        ]
    )
    
    depends_on = models.IntegerField(null=True, blank=True)
    text = models.TextField()
    
    status = models.CharField(
        max_length=50,
        choices=[
            ('draft', 'Draft'),
            ('reviewed', 'Reviewed'),
            ('perfected', 'Perfected'),
            ('final', 'Final'),
        ],
        default='draft'
    )
    
    amendments = models.JSONField(default=list, blank=True)
    examiner_comments = models.TextField(blank=True)
    
    class Meta:
        db_table = 'patent_claim_draft'
        ordering = ['claim_number']
    
    def __str__(self):
        return f"Claim {self.claim_number}: {self.text[:50]}..."


class AgentDefinition(TimestampMixin):
    """Unified agent definition for both local and premium agents."""

    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    agent_type = models.CharField(
        max_length=20,
        choices=[
            ('local', 'Local'),
            ('premium', 'Premium'),
        ]
    )

    category = models.CharField(
        max_length=50,
        choices=[
            ('drafting', 'Drafting'),
            ('review', 'Review'),
            ('analysis', 'Analysis'),
            ('perfecting', 'Perfecting'),
            ('response', 'Response'),
            ('strategy', 'Strategy'),
            ('orchestrator', 'Orchestrator'),
            ('custom', 'Custom'),
        ],
        default='custom'
    )

    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_agents'
    )

    current_version = models.CharField(max_length=20, default='v1')

    allowed_modes = models.JSONField(
        default=list,
        blank=True,
        help_text="List of allowed modes: ['chat', 'edit', 'ask', 'agent']"
    )

    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Hex color for UI display"
    )

    icon = models.CharField(max_length=100, blank=True)

    tags = models.JSONField(default=list, blank=True)

    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Agent-specific configuration"
    )

    class Meta:
        db_table = 'patent_agent_definition'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.agent_type})"


class AgentVersion(TimestampMixin):
    """Version history for agent definitions."""

    agent = models.ForeignKey(
        AgentDefinition,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    version = models.CharField(max_length=20)

    system_prompt = models.TextField()

    changelog = models.TextField(blank=True)

    config_snapshot = models.JSONField(default=dict)

    is_active_version = models.BooleanField(default=True)

    class Meta:
        db_table = 'patent_agent_version'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.agent.name} - {self.version}"
