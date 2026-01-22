import json
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status

from apps.patent.models import (
    PatentSession,
    PremiumAgentUsage,
    SubscriptionQuota,
    OfficeAction,
    ClaimDraft,
    AgentDefinition,
    AgentVersion,
)
from apps.patent.services.premium_agents import PremiumAgentFactory
from apps.patent.services.orchestrator import OrchestratorAgent, OrchestratorTemplateLoader
from apps.api.middleware import RateLimiter

logger = logging.getLogger(__name__)


class PremiumAgentView(APIView):
    """
    Main endpoint for premium patent agent calls.
    
    POST /api/patent/agents/premium/
    
    Request body:
    {
        "agent_type": "mock_examiner|office_action_response|claim_strategy|specification_perfection",
        "session_id": "uuid",  // optional
        "task": "Review my patent draft for potential issues",
        "context": {
            "invention_title": "...",
            "technical_field": "...",
            "claims": [...],
            "specification": {...},
            ...
        }
    }
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        user = request.user
        agent_type = request.data.get('agent_type')
        session_id = request.data.get('session_id')
        task = request.data.get('task')
        context = request.data.get('context', {})
        
        if not agent_type or not task:
            return Response({
                'error': 'agent_type and task are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        allowed_agents = [
            'mock_examiner',
            'office_action_response',
            'claim_strategy',
            'specification_perfection',
        ]
        
        if agent_type not in allowed_agents:
            return Response({
                'error': f'Invalid agent_type. Allowed: {allowed_agents}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quota = SubscriptionQuota.objects.get(user=user)
        except SubscriptionQuota.DoesNotExist:
            quota = SubscriptionQuota.objects.create(
                user=user,
                tier='free',
                reset_date=self.get_next_reset_date()
            )
        
        allowed, used, limit = quota.can_use_agent(agent_type)
        
        if not allowed:
            return Response({
                'error': 'Quota exceeded',
                'code': 'QUOTA_EXCEEDED',
                'agent_type': agent_type,
                'used': used,
                'limit': limit,
                'upgrade_url': '/billing/checkout/',
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        session_context = self.get_session_context(session_id, context)
        session_context['conversation_history'] = self.get_conversation_history(session_id)
        
        usage = PremiumAgentUsage.objects.create(
            user=user,
            session_id=session_id,
            agent_type=agent_type,
            request_data={'task': task, 'context_keys': list(context.keys())},
            status='processing'
        )
        
        try:
            agent = PremiumAgentFactory.get_agent(agent_type, session_context)
            result = agent.execute(task, context)
            
            if result['success']:
                usage.status = 'completed'
                usage.response_data = result['result']
                usage.tokens_used = result['tokens_used']
                usage.cost = result['cost']
                usage.save()
                
                quota.increment_usage(agent_type)
                
                if session_id:
                    self.update_session_with_result(session_id, agent_type, result)
                
                return Response({
                    'success': True,
                    'result': result['result'],
                    'usage': {
                        'agent_type': agent_type,
                        'used': used + 1,
                        'limit': limit,
                        'remaining': limit - (used + 1),
                    }
                })
            else:
                usage.status = 'failed'
                usage.error_message = result['error']
                usage.save()
                
                return Response({
                    'success': False,
                    'error': result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Premium agent error: {e}")
            usage.status = 'failed'
            usage.error_message = str(e)
            usage.save()
            
            return Response({
                'success': False,
                'error': 'Internal server error',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_session_context(self, session_id: str, provided_context: dict) -> dict:
        """Get session context from database if session_id provided."""
        if not session_id:
            return provided_context
        
        try:
            session = PatentSession.objects.get(id=session_id)
            return {
                'invention_title': session.invention_title or provided_context.get('invention_title', ''),
                'technical_field': session.technical_field or provided_context.get('technical_field', ''),
                'claims': session.claims or provided_context.get('claims', []),
                'specification': session.specification or provided_context.get('specification', {}),
                'prior_art_references': session.prior_art_references or provided_context.get('prior_art_references', []),
                **provided_context
            }
        except PatentSession.DoesNotExist:
            return provided_context
    
    def get_conversation_history(self, session_id: str) -> list:
        """Get conversation history for session context."""
        if not session_id:
            return []
        
        try:
            session = PatentSession.objects.get(id=session_id)
            return session.messages if hasattr(session, 'messages') else []
        except PatentSession.DoesNotExist:
            return []
    
    def update_session_with_result(self, session_id: str, agent_type: str, result: dict):
        """Update session with premium agent results."""
        try:
            session = PatentSession.objects.get(id=session_id)
            
            if agent_type == 'mock_examiner':
                session.status = 'review'
                session.invention_disclosure.update({
                    'mock_examiner_review': result.get('result', {}),
                    'reviewed_at': datetime.utcnow().isoformat(),
                })
            elif agent_type == 'specification_perfection':
                session.status = 'perfecting'
                session.specification.update({
                    'perfection_result': result.get('result', {}),
                    'perfected_at': datetime.utcnow().isoformat(),
                })
            
            session.save()
        except PatentSession.DoesNotExist:
            pass
    
    def get_next_reset_date(self) -> datetime:
        """Get next quota reset date (first of next month)."""
        now = timezone.now()
        if now.month == 12:
            return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0)
        return now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0)


class PatentSessionView(APIView):
    """Manage patent drafting sessions."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        """List user's patent sessions."""
        sessions = PatentSession.objects.filter(user=request.user)
        
        data = [{
            'id': s.id,
            'title': s.title,
            'status': s.status,
            'invention_title': s.invention_title,
            'technical_field': s.technical_field,
            'created_at': s.created_at.isoformat(),
            'updated_at': s.updated_at.isoformat(),
        } for s in sessions]
        
        return Response({'sessions': data})
    
    def post(self, request):
        """Create a new patent session."""
        import uuid
        
        session = PatentSession.objects.create(
            id=str(uuid.uuid4()),
            user=request.user,
            title=request.data.get('title', 'New Patent'),
            invention_title=request.data.get('invention_title', ''),
            technical_field=request.data.get('technical_field', ''),
            invention_disclosure=request.data.get('invention_disclosure', {}),
            status='drafting'
        )
        
        return Response({
            'id': session.id,
            'title': session.title,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)


class PatentSessionDetailView(APIView):
    """Manage individual patent sessions."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, session_id):
        """Get session details."""
        try:
            session = PatentSession.objects.get(id=session_id, user=request.user)
            
            return Response({
                'id': session.id,
                'title': session.title,
                'status': session.status,
                'invention_title': session.invention_title,
                'technical_field': session.technical_field,
                'invention_disclosure': session.invention_disclosure,
                'claims': session.claims,
                'specification': session.specification,
                'prior_art_references': session.prior_art_references,
                'office_actions': session.office_actions,
                'is_premium': session.is_premium,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
            })
        except PatentSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, session_id):
        """Update session."""
        try:
            session = PatentSession.objects.get(id=session_id, user=request.user)
            
            allowed_fields = [
                'title', 'invention_title', 'technical_field',
                'invention_disclosure', 'claims', 'specification',
                'drawings_description', 'status'
            ]
            
            for field in allowed_fields:
                if field in request.data:
                    setattr(session, field, request.data[field])
            
            session.save()
            
            return Response({
                'id': session.id,
                'status': session.status,
                'updated_at': session.updated_at.isoformat(),
            })
        except PatentSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, session_id):
        """Delete session."""
        try:
            session = PatentSession.objects.get(id=session_id, user=request.user)
            session.delete()
            return Response({'deleted': True})
        except PatentSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


class QuotaStatusView(APIView):
    """Get user's premium agent quota status."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        """Get quota status."""
        user = request.user
        
        try:
            quota = SubscriptionQuota.objects.get(user=user)
        except SubscriptionQuota.DoesNotExist:
            quota = SubscriptionQuota.objects.create(
                user=user,
                tier='free',
                reset_date=self.get_next_reset_date()
            )
        
        return Response({
            'tier': quota.tier,
            'reset_date': quota.reset_date.isoformat(),
            'quotas': {
                'mock_examiner': {
                    'used': quota.mock_examiner_used,
                    'limit': quota.mock_examiner_limit,
                    'remaining': max(0, quota.mock_examiner_limit - quota.mock_examiner_used),
                },
                'office_action_response': {
                    'used': quota.office_action_used,
                    'limit': quota.office_action_limit,
                    'remaining': max(0, quota.office_action_limit - quota.office_action_used),
                },
                'claim_strategy': {
                    'used': quota.claim_strategy_used,
                    'limit': quota.claim_strategy_limit,
                    'remaining': max(0, quota.claim_strategy_limit - quota.claim_strategy_used),
                },
                'specification_perfection': {
                    'used': quota.specification_perfection_used,
                    'limit': quota.specification_perfection_limit,
                    'remaining': max(0, quota.specification_perfection_limit - quota.specification_perfection_used),
                },
            }
        })
    
    def get_next_reset_date(self) -> datetime:
        now = timezone.now()
        if now.month == 12:
            return now.replace(year=now.year + 1, month=1, day=1)
        return now.replace(month=now.month + 1, day=1)


class PremiumAgentsListView(APIView):
    """List available premium agents."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        """Get list of premium agents with descriptions."""
        agents = PremiumAgentFactory.list_agents()
        
        return Response({
            'agents': agents,
            'pricing': {
                'free': {
                    'mock_examiner': 3,
                    'office_action_response': 0,
                    'claim_strategy': 0,
                    'specification_perfection': 0,
                    'patent_searcher': 3,
                    'patent_drafter': 3,
                    'patent_interrogator': 3,
                    'patent_illustrator': 3,
                },
                'pro': {
                    'mock_examiner': 50,
                    'office_action_response': 10,
                    'claim_strategy': 10,
                    'specification_perfection': 20,
                    'patent_searcher': 100,
                    'patent_drafter': 200,
                    'patent_interrogator': 200,
                    'patent_illustrator': 150,
                },
                'enterprise': {
                    'mock_examiner': 'unlimited',
                    'office_action_response': 'unlimited',
                    'claim_strategy': 'unlimited',
                    'specification_perfection': 'unlimited',
                    'patent_searcher': 'unlimited',
                    'patent_drafter': 'unlimited',
                    'patent_interrogator': 'unlimited',
                    'patent_illustrator': 'unlimited',
                }
            }
        })


class FreeAgentsConfigView(APIView):
    """Configuration for free (local) agents."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        """Get free agent configurations."""
        return Response({
            'agents': [
                {
                    'id': 'invention_disclosure',
                    'name': 'Invention Disclosure',
                    'description': 'Analyze invention ideas and extract key features',
                    'mode': 'primary',
                    'local_only': True,
                },
                {
                    'id': 'patent_drafter',
                    'name': 'Patent Drafter',
                    'description': 'Draft patent claims and specification',
                    'mode': 'primary',
                    'local_only': True,
                },
                {
                    'id': 'prior_art_searcher',
                    'name': 'Prior Art Searcher',
                    'description': 'Prepare and structure prior art search queries',
                    'mode': 'subagent',
                    'local_only': True,
                },
                {
                    'id': 'technical_drafter',
                    'name': 'Technical Drawing Description',
                    'description': 'Create detailed drawing descriptions for patent figures',
                    'mode': 'subagent',
                    'local_only': True,
                },
            ],
            'local_providers': ['ollama', 'lm-studio', 'openai-compatible'],
            'recommended_models': {
                'ollama': ['llama3.2', 'mistral', 'codellama'],
                'lm-studio': ['llama-3.2-1b-instruct', 'mistral-7b-instruct'],
            }
        })


class UnifiedAgentsListView(APIView):
    """
    Get unified list of all available agents (local + premium).
    
    GET /api/patent/agents/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        """Get list of all available agents from database and local files."""
        agents = []
        
        for agent_def in AgentDefinition.objects.filter(is_active=True, is_published=True):
            current_version = agent_def.versions.filter(
                is_active_version=True
            ).first()
            
            agent_info = {
                'id': agent_def.id,
                'name': agent_def.name,
                'description': agent_def.description,
                'type': agent_def.agent_type,
                'category': agent_def.category,
                'version': agent_def.current_version,
                'allowed_modes': agent_def.allowed_modes,
                'color': agent_def.color,
                'icon': agent_def.icon,
                'tags': agent_def.tags,
            }
            
            if current_version:
                agent_info['system_prompt'] = current_version.system_prompt
            
            agents.append(agent_info)
        
        return Response({
            'agents': agents,
            'count': len(agents),
        })


class AgentDetailView(APIView):
    """
    Get detailed agent information including all versions.
    
    GET /api/patent/agents/<agent_id>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, agent_id):
        """Get detailed agent information."""
        try:
            agent_def = AgentDefinition.objects.get(id=agent_id, is_active=True)
        except AgentDefinition.DoesNotExist:
            return Response({'error': 'Agent not found'}, status=status.HTTP_404_NOT_FOUND)
        
        versions = [
            {
                'version': v.version,
                'changelog': v.changelog,
                'is_active': v.is_active_version,
                'created_at': v.created_at.isoformat(),
            }
            for v in agent_def.versions.order_by('-created_at')
        ]
        
        current_version = agent_def.versions.filter(is_active_version=True).first()
        
        return Response({
            'id': agent_def.id,
            'name': agent_def.name,
            'description': agent_def.description,
            'type': agent_def.agent_type,
            'category': agent_def.category,
            'current_version': agent_def.current_version,
            'allowed_modes': agent_def.allowed_modes,
            'color': agent_def.color,
            'icon': agent_def.icon,
            'tags': agent_def.tags,
            'config': agent_def.config,
            'system_prompt': current_version.system_prompt if current_version else None,
            'versions': versions,
            'created_by': agent_def.created_by_id,
            'created_at': agent_def.created_at.isoformat(),
            'updated_at': agent_def.updated_at.isoformat(),
        })


class AgentCreateView(APIView):
    """
    Create a new agent definition.
    
    POST /api/patent/agents/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        """Create a new agent."""
        import uuid
        
        data = request.data
        
        agent = AgentDefinition.objects.create(
            id=data.get('id', f"agent_{uuid.uuid4().hex[:8]}"),
            name=data['name'],
            description=data.get('description', ''),
            agent_type=data.get('agent_type', 'local'),
            category=data.get('category', 'custom'),
            allowed_modes=data.get('allowed_modes', ['chat']),
            color=data.get('color', '#3B82F6'),
            icon=data.get('icon', ''),
            tags=data.get('tags', []),
            config=data.get('config', {}),
            created_by=request.user,
        )
        
        AgentVersion.objects.create(
            agent=agent,
            version='v1',
            system_prompt=data['system_prompt'],
            changelog=data.get('changelog', 'Initial version'),
            is_active_version=True,
        )
        
        return Response({
            'id': agent.id,
            'name': agent.name,
            'type': agent.agent_type,
            'version': agent.current_version,
        }, status=status.HTTP_201_CREATED)


class AgentUpdateView(APIView):
    """
    Update an agent and create a new version.
    
    PATCH /api/patent/agents/<agent_id>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def patch(self, request, agent_id):
        """Update agent and create new version."""
        try:
            agent = AgentDefinition.objects.get(id=agent_id)
        except AgentDefinition.DoesNotExist:
            return Response({'error': 'Agent not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        
        if 'name' in data:
            agent.name = data['name']
        if 'description' in data:
            agent.description = data['description']
        if 'allowed_modes' in data:
            agent.allowed_modes = data['allowed_modes']
        if 'color' in data:
            agent.color = data['color']
        if 'icon' in data:
            agent.icon = data['icon']
        if 'tags' in data:
            agent.tags = data['tags']
        if 'is_active' in data:
            agent.is_active = data['is_active']
        if 'is_published' in data:
            agent.is_published = data['is_published']
        
        if 'system_prompt' in data:
            old_version = agent.current_version
            new_version = self.increment_version(old_version)
            
            AgentVersion.objects.filter(agent=agent, is_active_version=True).update(
                is_active_version=False
            )
            
            AgentVersion.objects.create(
                agent=agent,
                version=new_version,
                system_prompt=data['system_prompt'],
                changelog=data.get('changelog', f'Updated from {old_version}'),
                is_active_version=True,
            )
            
            agent.current_version = new_version
        
        agent.save()
        
        return Response({
            'id': agent.id,
            'name': agent.name,
            'current_version': agent.current_version,
        })
    
    def increment_version(self, version: str) -> str:
        """Increment version number (v1 -> v2)."""
        if version.startswith('v'):
            try:
                num = int(version[1:])
                return f'v{num + 1}'
            except ValueError:
                pass
        return 'v2'


class OrchestratorPlanView(APIView):
    """
    Create an orchestration plan for a patent task.
    
    POST /api/patent/orchestrator/plan/
    
    Request body:
    {
        "request": "Help me draft a patent for my solar panel inverter",
        "technology": "software",  // software, ai, biotech, mechanics
        "session_id": "uuid"  // optional
    }
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        import asyncio
        
        user = request.user
        user_request = request.data.get('request')
        technology = request.data.get('technology', 'software')
        session_id = request.data.get('session_id')
        
        if not user_request:
            return Response({
                'error': 'request is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get session context if provided
            session_context = {}
            if session_id:
                try:
                    session = PatentSession.objects.get(id=session_id, user=user)
                    session_context = {
                        'invention_title': session.invention_title,
                        'technical_field': session.technical_field,
                        'claims': session.claims,
                        'specification': session.specification,
                    }
                except PatentSession.DoesNotExist:
                    pass
            
            # Create orchestrator and plan
            orchestrator = OrchestratorAgent(session_context)
            
            plan = asyncio.run(
                orchestrator.create_plan(
                    user_request=user_request,
                    technology=technology,
                )
            )
            
            return Response({
                'success': True,
                'plan': {
                    'tasks': [
                        {
                            'id': t.id,
                            'agent': t.agent,
                            'task': t.task,
                            'depends_on': t.depends_on,
                            'expected_output': t.expected_output,
                        }
                        for t in plan.tasks
                    ],
                    'technology': plan.technology,
                    'estimated_time': plan.estimated_time,
                    'premium_agents_needed': plan.premium_agents_needed,
                    'local_agents_needed': plan.local_agents_needed,
                },
                'thinking_log': orchestrator.get_thinking_log(),
                'formatted_plan': orchestrator.format_plan_for_display(),
            })
            
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrchestratorExecuteView(APIView):
    """
    Execute an orchestration plan.
    
    POST /api/patent/orchestrator/execute/
    
    Request body:
    {
        "request": "Help me draft a patent for my solar panel inverter",
        "technology": "software",
        "session_id": "uuid"  // optional
    }
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        import asyncio
        
        user = request.user
        user_request = request.data.get('request')
        technology = request.data.get('technology', 'software')
        session_id = request.data.get('session_id')
        
        if not user_request:
            return Response({
                'error': 'request is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get session if provided
            session = None
            session_context = {}
            if session_id:
                try:
                    session = PatentSession.objects.get(id=session_id, user=user)
                    session_context = {
                        'invention_title': session.invention_title,
                        'technical_field': session.technical_field,
                        'claims': session.claims,
                        'specification': session.specification,
                    }
                except PatentSession.DoesNotExist:
                    pass
            
            # Create orchestrator
            orchestrator = OrchestratorAgent(session_context)
            
            # Create and execute plan
            plan = asyncio.run(
                orchestrator.create_plan(
                    user_request=user_request,
                    technology=technology,
                )
            )
            
            results = asyncio.run(
                orchestrator.execute_plan(
                    user=user,
                    session=session,
                )
            )
            
            return Response({
                'success': True,
                'completed_tasks': [t.id for t in results["completed"]],
                'failed_tasks': [t.id for t in results["failed"]],
                'skipped_tasks': [t.id for t in results["skipped"]],
                'thinking_log': orchestrator.get_thinking_log(),
            })
            
        except Exception as e:
            logger.error(f"Failed to execute plan: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrchestratorThinkingView(APIView):
    """
    Get thinking log for a session.
    
    GET /api/patent/orchestrator/thinking/<session_id>/
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, session_id):
        """Get thinking log for a session."""
        try:
            session = PatentSession.objects.get(id=session_id, user=request.user)
            
            # Return mock thinking log for now
            # In production, this would be stored in the session or cache
            return Response({
                'session_id': session_id,
                'thinking_log': [],
                'formatted_plan': session.invention_disclosure.get('formatted_plan', 'No plan available'),
            })
            
        except PatentSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


class OrchestratorTemplatesView(APIView):
    """
    Get available orchestrator templates.
    
    GET /api/patent/orchestrator/templates/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get list of available templates."""
        templates = [
            {
                'id': 'software',
                'name': 'Software',
                'description': 'Templates for software and computer-implemented inventions',
            },
            {
                'id': 'ai',
                'name': 'AI/ML',
                'description': 'Templates for artificial intelligence and machine learning',
            },
            {
                'id': 'biotech',
                'name': 'Biotech/Pharma',
                'description': 'Templates for biotechnology and pharmaceutical patents',
            },
            {
                'id': 'mechanics',
                'name': 'Mechanics',
                'description': 'Templates for mechanical inventions',
            },
        ]
        
        return Response({
            'templates': templates,
            'default': 'software',
        })
