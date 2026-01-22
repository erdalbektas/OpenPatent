"""
Integration tests for patent agents.

These tests verify the agent loading, execution, and quota management.
Run with: cd openpatent_django && python manage.py test apps.patent.tests.test_agents
"""

import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.patent.models import (
    PatentSession,
    SubscriptionQuota,
    PremiumAgentUsage,
    AgentDefinition,
    AgentVersion,
)
from apps.patent.services.premium_agents import (
    PremiumAgentFactory,
    MockExaminerAgent,
    OfficeActionResponseAgent,
    ClaimStrategyAgent,
    SpecificationPerfectionAgent,
    PatentSearcherAgent,
    PatentDrafterAgent,
    PatentInterrogatorAgent,
    PatentIllustratorAgent,
)


class PremiumAgentFactoryTests(TestCase):
    """Tests for the premium agent factory."""

    def test_factory_lists_all_agents(self):
        """Test that factory returns all registered agents."""
        agents = PremiumAgentFactory.list_agents()
        agent_ids = [a['id'] for a in agents]
        
        expected_agents = [
            'mock_examiner',
            'office_action_response',
            'claim_strategy',
            'specification_perfection',
            'patent_searcher',
            'patent_drafter',
            'patent_interrogator',
            'patent_illustrator',
        ]
        
        for expected in expected_agents:
            self.assertIn(expected, agent_ids, f"Missing agent: {expected}")

    def test_factory_creates_correct_agent_types(self):
        """Test that factory creates correct agent class instances."""
        context = {'invention_title': 'Test Invention'}
        
        test_cases = [
            ('mock_examiner', MockExaminerAgent),
            ('office_action_response', OfficeActionResponseAgent),
            ('claim_strategy', ClaimStrategyAgent),
            ('specification_perfection', SpecificationPerfectionAgent),
            ('patent_searcher', PatentSearcherAgent),
            ('patent_drafter', PatentDrafterAgent),
            ('patent_interrogator', PatentInterrogatorAgent),
            ('patent_illustrator', PatentIllustratorAgent),
        ]
        
        for agent_id, expected_class in test_cases:
            with self.subTest(agent_id=agent_id):
                agent = PremiumAgentFactory.get_agent(agent_id, context)
                self.assertIsInstance(agent, expected_class)

    def test_factory_raises_for_unknown_agent(self):
        """Test that factory raises ValueError for unknown agents."""
        with self.assertRaises(ValueError) as context:
            PremiumAgentFactory.get_agent('unknown_agent', {})
        
        self.assertIn('Unknown agent type', str(context.exception))


class AgentDefinitionTests(TestCase):
    """Tests for agent definition models."""

    def test_create_agent_definition(self):
        """Test creating an agent definition."""
        agent = AgentDefinition.objects.create(
            id='test_agent',
            name='Test Agent',
            description='A test agent',
            agent_type='premium',
            category='drafting',
        )
        
        AgentVersion.objects.create(
            agent=agent,
            version='v1',
            system_prompt='You are a test agent.',
            changelog='Initial version',
            is_active_version=True,
        )
        
        self.assertEqual(agent.name, 'Test Agent')
        self.assertEqual(agent.current_version, 'v1')
        
        version = agent.versions.filter(is_active_version=True).first()
        self.assertIsNotNone(version)
        self.assertEqual(version.system_prompt, 'You are a test agent.')

    def test_agent_version_increment(self):
        """Test version incrementing on update."""
        agent = AgentDefinition.objects.create(
            id='version_test',
            name='Version Test',
            description='Testing version increments',
            agent_type='local',
        )
        
        AgentVersion.objects.create(
            agent=agent,
            version='v1',
            system_prompt='Version 1',
            is_active_version=True,
        )
        
        agent.current_version = 'v2'
        agent.save()
        
        AgentVersion.objects.create(
            agent=agent,
            version='v2',
            system_prompt='Version 2',
            is_active_version=True,
        )
        
        self.assertEqual(agent.current_version, 'v2')
        
        versions = list(agent.versions.order_by('-created_at'))
        self.assertEqual(len(versions), 2)


class SubscriptionQuotaTests(TestCase):
    """Tests for subscription quota management."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.quota = SubscriptionQuota.objects.create(
            user=self.user,
            tier='free',
            mock_examiner_limit=3,
            patent_searcher_limit=3,
            patent_drafter_limit=3,
            patent_interrogator_limit=3,
            patent_illustrator_limit=3,
        )

    def test_can_use_agent_within_limit(self):
        """Test agent usage within quota limits."""
        allowed, used, limit = self.quota.can_use_agent('mock_examiner')
        self.assertTrue(allowed)
        self.assertEqual(used, 0)
        self.assertEqual(limit, 3)

    def test_cannot_use_agent_when_limit_exceeded(self):
        """Test agent usage when quota exceeded."""
        self.quota.mock_examiner_used = 3
        self.quota.save()
        
        allowed, used, limit = self.quota.can_use_agent('mock_examiner')
        self.assertFalse(allowed)
        self.assertEqual(used, 3)
        self.assertEqual(limit, 3)

    def test_new_agents_have_default_limits(self):
        """Test that new agent types have default limits."""
        allowed, used, limit = self.quota.can_use_agent('patent_drafter')
        self.assertFalse(allowed)
        self.assertEqual(used, 0)
        self.assertEqual(limit, 0)

    def test_increment_usage(self):
        """Test incrementing usage counter."""
        self.quota.increment_usage('mock_examiner')
        
        self.quota.refresh_from_db()
        self.assertEqual(self.quota.mock_examiner_used, 1)

    def test_increment_usage_unknown_agent(self):
        """Test incrementing for unknown agent does nothing."""
        initial = self.quota.mock_examiner_used
        self.quota.increment_usage('unknown_agent')
        
        self.quota.refresh_from_db()
        self.assertEqual(self.quota.mock_examiner_used, initial)


class AgentAPITests(TestCase):
    """Tests for agent API endpoints."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='api_test@example.com',
            password='testpass123',
        )
        self.quota = SubscriptionQuota.objects.create(
            user=self.user,
            tier='pro',
            mock_examiner_limit=50,
            patent_searcher_limit=100,
            patent_drafter_limit=200,
            patent_interrogator_limit=200,
            patent_illustrator_limit=150,
        )
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_premium_agents(self):
        """Test listing premium agents."""
        response = self.client.get('/api/patent/agents/premium/list/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('agents', data)
        self.assertIn('pricing', data)
        
        agent_ids = [a['id'] for a in data['agents']]
        self.assertIn('mock_examiner', agent_ids)
        self.assertIn('patent_searcher', agent_ids)

    def test_quota_status_includes_new_agents(self):
        """Test quota status includes new agent types."""
        response = self.client.get('/api/patent/quota/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        quotas = data.get('quotas', {})
        
        self.assertIn('patent_searcher', quotas)
        self.assertIn('patent_drafter', quotas)
        self.assertIn('patent_interrogator', quotas)
        self.assertIn('patent_illustrator', quotas)


class MockAgentExecutionTests(TestCase):
    """Tests for agent execution with mocked OpenAI."""

    @patch('apps.patent.services.premium_agents.openai.ChatCompletion.acreate')
    async def test_mock_examiner_execution(self, mock_create):
        """Test mock examiner agent execution."""
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"result": "success"}'))],
            usage=MagicMock(total_tokens=100),
        )
        
        agent = MockExaminerAgent({})
        result = await agent.execute('Review this patent', {'claims': ['claim 1']})
        
        self.assertTrue(result['success'])
        mock_create.assert_called_once()

    @patch('apps.patent.services.premium_agents.openai.ChatCompletion.acreate')
    async def test_patent_searcher_execution(self, mock_create):
        """Test patent searcher agent execution."""
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"search_queries": []}'))],
            usage=MagicMock(total_tokens=150),
        )
        
        agent = PatentSearcherAgent({})
        result = await agent.execute(
            'Search for prior art',
            {'invention_description': 'A new toaster'}
        )
        
        self.assertTrue(result['success'])
        mock_create.assert_called_once()


class AgentMarkdownLoadingTests(TestCase):
    """Tests for loading agents from Markdown files."""

    def test_agent_markdown_files_exist(self):
        """Verify agent Markdown files exist."""
        import os
        agent_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'agents'
        )
        
        expected_agents = [
            'patent_searcher.md',
            'patent_drafter.md',
            'patent_examiner.md',
            'patent_interrogator.md',
            'patent_illustrator.md',
        ]
        
        for agent_file in expected_agents:
            filepath = os.path.join(agent_dir, agent_file)
            self.assertTrue(
                os.path.exists(filepath),
                f"Agent file not found: {filepath}"
            )

    def test_agent_markdown_has_required_fields(self):
        """Verify Markdown files have required frontmatter fields."""
        import os
        import yaml
        
        agent_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'agents'
        )
        
        for filename in os.listdir(agent_dir):
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(agent_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            
            if content.startswith('---'):
                frontmatter_end = content.find('---', 3)
                if frontmatter_end != -1:
                    frontmatter = yaml.safe_load(content[3:frontmatter_end])
                    self.assertIn('name', frontmatter, f"{filename} missing 'name'")
                    self.assertIn('description', frontmatter, f"{filename} missing 'description'")
                    self.assertIn('color', frontmatter, f"{filename} missing 'color'")
