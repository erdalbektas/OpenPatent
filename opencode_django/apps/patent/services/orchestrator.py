"""
Orchestrator Agent Service

The Orchestrator Agent plans and delegates patent tasks to specialized agents.
It handles:
- Task planning using LLM with customizable prompts
- Delegation to local and premium agents
- Fallback procedures on failure
- Progress tracking and display
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

import openai
from django.conf import settings
from django.db import transaction

from apps.patent.models import (
    PatentSession,
    PremiumAgentUsage,
    SubscriptionQuota,
    AgentDefinition,
)
from apps.patent.services.premium_agents import PremiumAgentFactory

logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY


class AgentType(Enum):
    LOCAL = "local"
    PREMIUM = "premium"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlannedTask:
    id: int
    agent: str
    task: str
    input_data: Dict[str, Any]
    expected_output: str
    depends_on: List[int] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class OrchestrationPlan:
    tasks: List[PlannedTask]
    technology: str = "software"
    estimated_time: str = "5-10 minutes"
    premium_agents_needed: List[str] = field(default_factory=list)
    local_agents_needed: List[str] = field(default_factory=list)


class OrchestratorTemplateLoader:
    """Load and manage orchestrator templates per technology."""
    
    TEMPLATE_DIR = Path(__file__).parent / "templates"
    DEFAULT_TEMPLATE = "orchestrator_software.md"
    
    @classmethod
    def load_template(cls, technology: str = "software") -> str:
        """Load orchestrator template for the given technology."""
        template_file = cls.TEMPLATE_DIR / f"orchestrator_{technology}.md"
        
        if not template_file.exists():
            logger.warning(f"Template not found for {technology}, using default")
            template_file = cls.TEMPLATE_DIR / cls.DEFAULT_TEMPLATE
        
        try:
            return template_file.read_text()
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            return cls.get_default_template()
    
    @classmethod
    def load_local_template(cls, project_path: Path) -> Optional[str]:
        """Load custom template from project (.openpatent/orchestrator.md)."""
        orchestrator_file = project_path / ".openpatent" / "orchestrator.md"
        
        if orchestrator_file.exists():
            try:
                content = orchestrator_file.read_text()
                # Check if it's a valid template
                if "---" in content and "TECHNOLOGY:" in content:
                    return content
            except Exception as e:
                logger.error(f"Failed to load local template: {e}")
        
        return None
    
    @classmethod
    def get_default_template(cls) -> str:
        """Get the default software template."""
        return cls.load_template("software")


class OrchestratorAgent:
    """Main orchestrator agent that plans and delegates tasks."""
    
    def __init__(self, session_context: Dict[str, Any]):
        self.context = session_context
        self.plan: Optional[OrchestrationPlan] = None
        self.completed_tasks: List[PlannedTask] = []
        self.failed_tasks: List[PlannedTask] = []
        self.thinking_log: List[Dict[str, str]] = []
        self._available_agents: Optional[List[Dict[str, Any]]] = None
    
    def think(self, stage: str, message: str):
        """Log thinking for display in thinking tab."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": stage,
            "message": message,
        }
        self.thinking_log.append(entry)
        logger.info(f"[ORCHESTRATOR {stage}] {message}")
    
    def load_available_agents(self) -> List[Dict[str, Any]]:
        """Load available agents from database."""
        if self._available_agents is not None:
            return self._available_agents
        
        agents = []
        for agent_def in AgentDefinition.objects.filter(is_active=True):
            current_version = agent_def.versions.filter(is_active_version=True).first()
            
            agent_info = {
                'id': agent_def.id,
                'name': agent_def.name,
                'type': agent_def.agent_type,
                'category': agent_def.category,
                'version': agent_def.current_version,
                'system_prompt': current_version.system_prompt if current_version else '',
            }
            agents.append(agent_info)
        
        self._available_agents = agents
        return agents
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific agent by ID."""
        agents = self.load_available_agents()
        for agent in agents:
            if agent['id'] == agent_id:
                return agent
        return None
    
    def get_agents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get agents by category."""
        agents = self.load_available_agents()
        return [a for a in agents if a.get('category') == category]
    
    def format_agents_for_prompt(self) -> str:
        """Format available agents for inclusion in LLM prompt."""
        agents = self.load_available_agents()
        
        if not agents:
            return "No agents registered in the system."
        
        lines = ["\n\n## Available Agents:"]
        for agent in agents:
            lines.append(f"- **{agent['id']}**: {agent['name']} ({agent['type']}, {agent.get('category', 'general')})")
        
        return "\n".join(lines)
    
    def think(self, stage: str, message: str):
        """Log thinking for display in thinking tab."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": stage,
            "message": message,
        }
        self.thinking_log.append(entry)
        logger.info(f"[ORCHESTRATOR {stage}] {message}")
    
    async def create_plan(
        self,
        user_request: str,
        technology: str = "software",
        project_path: Optional[Path] = None
    ) -> OrchestrationPlan:
        """Create an execution plan based on user request."""
        self.think("planning", f"Analyzing user request: {user_request[:100]}...")
        
        # Load template (local takes priority)
        local_template = None
        if project_path:
            local_template = OrchestratorTemplateLoader.load_local_template(project_path)
        
        if local_template:
            self.think("planning", "Using custom orchestrator template from project")
            system_prompt = local_template
        else:
            self.think("planning", f"Loading {technology} template")
            system_prompt = OrchestratorTemplateLoader.load_template(technology)
        
        # Add available agents to the prompt
        agents_section = self.format_agents_for_prompt()
        system_prompt = system_prompt + agents_section
        
        # Extract the JSON part from the template
        prompt = f"""{system_prompt}

USER REQUEST:
{user_request}

Based on the above request, create a detailed execution plan in JSON format.
Use the agent IDs from the available agents list when specifying tasks.
"""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            
            content = response.choices[0].message.content
            
            # Parse the plan from the response
            plan_data = self._parse_plan_response(content)
            
            if plan_data:
                self.plan = self._build_plan(plan_data, technology)
                self.think("planning", f"Plan created with {len(self.plan.tasks)} tasks")
                
                # Log the plan
                for task in self.plan.tasks:
                    agent_type = "Premium" if task.agent.startswith("premium:") or task.agent in ["mock_examiner", "office_action_response", "claim_strategy", "specification_perfection"] else "Local"
                    self.think(
                        "planning",
                        f"Task {task.id}: {task.agent} ({agent_type}) - {task.task}"
                    )
                
                return self.plan
            else:
                raise ValueError("Failed to parse plan from response")
                
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            self.think("error", f"Failed to create plan: {str(e)}")
            raise
    
    def _parse_plan_response(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse the plan from the LLM response."""
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON directly
        json_start = content.find('{"plan"')
        if json_start >= 0:
            try:
                # Find the matching closing brace
                brace_count = 0
                json_end = json_start
                for i, char in enumerate(content[json_start:], start=json_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                return json.loads(content[json_start:json_end])
            except (json.JSONDecodeError, ValueError):
                pass
        
        return None
    
    def _build_plan(self, plan_data: Dict[str, Any], technology: str) -> OrchestrationPlan:
        """Build an OrchestrationPlan from parsed data."""
        tasks = []
        
        for task_data in plan_data.get("plan", []):
            task = PlannedTask(
                id=task_data["id"],
                agent=task_data["agent"],
                task=task_data["task"],
                input_data={"user_input": task_data.get("input_from_user", "")},
                expected_output=task_data.get("expected_output", ""),
                depends_on=task_data.get("depends_on", []),
            )
            tasks.append(task)
        
        return OrchestrationPlan(
            tasks=tasks,
            technology=technology,
            estimated_time=plan_data.get("estimated_time", "5-10 minutes"),
            premium_agents_needed=plan_data.get("premium_agents_needed", []),
            local_agents_needed=plan_data.get("local_agents_needed", []),
        )
    
    async def execute_plan(
        self,
        user,
        session: Optional[PatentSession] = None,
        fallback_level: int = 1,
    ) -> Dict[str, Any]:
        """Execute the plan with fallback handling."""
        if not self.plan:
            raise ValueError("No plan created. Call create_plan first.")
        
        self.think("execution", f"Starting execution with {len(self.plan.tasks)} tasks")
        
        results = {
            "plan": self.plan,
            "completed": [],
            "failed": [],
            "skipped": [],
            "thinking_log": self.thinking_log,
        }
        
        # Get quota status
        try:
            quota = SubscriptionQuota.objects.get(user=user)
        except SubscriptionQuota.DoesNotExist:
            quota = SubscriptionQuota.objects.create(
                user=user,
                tier='free',
                reset_date=self._get_next_reset_date()
            )
        
        for task in self.plan.tasks:
            # Check if dependencies are met
            if not self._dependencies_met(task, results["completed"]):
                self.think("execution", f"Task {task.id} skipped - dependencies not met")
                task.status = TaskStatus.SKIPPED
                results["skipped"].append(task.id)
                continue
            
            self.think("execution", f"Task {task.id}: Starting - {task.task}")
            task.status = TaskStatus.IN_PROGRESS
            
            try:
                # Determine if this is a premium or local task
                is_premium = self._is_premium_agent(task.agent)
                
                if is_premium:
                    # Check quota
                    allowed, used, limit = quota.can_use_agent(task.agent)
                    if not allowed:
                        self.think("execution", f"Task {task.id}: Quota exceeded, using local fallback")
                        result = await self._execute_local_fallback(task)
                    else:
                        result = await self._execute_premium_task(task, user, session)
                else:
                    result = await self._execute_local_task(task)
                
                if result.get("success"):
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    results["completed"].append(task)
                    self.think("execution", f"Task {task.id}: Completed")
                else:
                    raise Exception(result.get("error", "Task failed"))
                    
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                results["failed"].append(task)
                
                # Handle fallback
                if fallback_level <= 4:
                    self.think("execution", f"Task {task.id} failed: {str(e)}")
                    self.think("execution", f"Applying fallback level {fallback_level + 1}")
                    
                    fallback_result = await self._apply_fallback(
                        task, user, session, fallback_level, results["completed"]
                    )
                    
                    if fallback_result.get("success"):
                        task.status = TaskStatus.COMPLETED
                        task.result = fallback_result
                        results["completed"].append(task)
                        results["failed"].remove(task)
                        self.think("execution", f"Task {task.id}: Recovered via fallback")
                    else:
                        self.think("execution", f"Task {task.id}: Fallback failed")
                else:
                    self.think("error", f"Task {task.id}: All fallbacks exhausted")
        
        return results
    
    def _is_premium_agent(self, agent: str) -> bool:
        """Check if an agent is premium."""
        if not agent:
            return False
        return agent.startswith("premium/")
    
    def _dependencies_met(self, task: PlannedTask, completed: List[PlannedTask]) -> bool:
        """Check if all dependencies are completed."""
        completed_ids = {t.id for t in completed}
        return all(dep_id in completed_ids for dep_id in task.depends_on)
    
    async def _execute_local_task(self, task: PlannedTask) -> Dict[str, Any]:
        """Execute a local task (placeholder - would connect to local LLM)."""
        # In the actual implementation, this would call the local LLM
        # For now, return a placeholder response
        self.think("local", f"Executing local task with {task.agent}")
        
        return {
            "success": True,
            "agent": task.agent,
            "task": task.task,
            "result": {
                "output": f"Local result from {task.agent}",
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
    
    async def _execute_premium_task(
        self,
        task: PlannedTask,
        user,
        session: Optional[PatentSession],
    ) -> Dict[str, Any]:
        """Execute a premium task via API."""
        self.think("premium", f"Executing premium task with {task.agent}")
        
        # Extract agent type from premium/agent_id format
        agent_type = task.agent
        if task.agent.startswith("premium/"):
            agent_type = task.agent[8:]  # Remove "premium/" prefix
        
        # Create usage record
        usage = PremiumAgentUsage.objects.create(
            user=user,
            session=session,
            agent_type=agent_type,
            request_data={"task": task.task, "context": task.input_data},
            status='processing'
        )
        
        try:
            # Get the appropriate premium agent
            agent = PremiumAgentFactory.get_agent(agent_type, self.context)
            
            # Execute the agent
            result = await agent.execute(task.task, task.input_data)
            
            if result["success"]:
                usage.status = 'completed'
                usage.response_data = result.get("result", {})
                usage.tokens_used = result.get("tokens_used", 0)
                usage.cost = result.get("cost", 0)
                usage.save()
                
                # Update quota
                try:
                    quota = SubscriptionQuota.objects.get(user=user)
                    quota.increment_usage(agent_type)
                except SubscriptionQuota.DoesNotExist:
                    pass
                
                return {
                    "success": True,
                    "agent": task.agent,
                    "task": task.task,
                    "result": result.get("result", {}),
                }
            else:
                usage.status = 'failed'
                usage.error_message = result.get("error", "Unknown error")
                usage.save()
                raise Exception(result.get("error", "Agent execution failed"))
                
        except Exception as e:
            usage.status = 'failed'
            usage.error_message = str(e)
            usage.save()
            raise
    
    async def _execute_local_fallback(self, task: PlannedTask) -> Dict[str, Any]:
        """Execute a simplified local fallback for a premium task."""
        self.think("fallback", f"Using local simplified fallback for {task.agent}")
        
        # Return a simplified result that allows continuation
        return {
            "success": True,
            "agent": task.agent,
            "task": task.task,
            "result": {
                "output": "Simplified local analysis (premium unavailable)",
                "fallback": True,
            },
        }
    
    async def _apply_fallback(
        self,
        task: PlannedTask,
        user,
        session: Optional[PatentSession],
        current_level: int,
        completed: List[PlannedTask],
    ) -> Dict[str, Any]:
        """Apply fallback procedure for a failed task."""
        fallback_descriptions = {
            1: "Retrying with same agent",
            2: "Retrying with different agent configuration",
            3: "Using simplified local analysis",
            4: "Skipping premium step, continuing with draft",
        }
        
        self.think("fallback", f"Fallback {current_level}: {fallback_descriptions.get(current_level, 'Unknown')}")
        
        if current_level == 1:
            # Retry same agent
            task.retry_count += 1
            if self._is_premium_agent(task.agent):
                return await self._execute_premium_task(task, user, session)
            else:
                return await self._execute_local_task(task)
        
        elif current_level == 2:
            # Try different agent - use a different premium agent for the same task
            fallback_agents = {
                "premium/mock_examiner": ["premium/claim_strategy"],
                "premium/office_action_response": ["premium/claim_strategy"],
                "premium/claim_strategy": ["premium/mock_examiner"],
                "premium/specification_perfection": ["premium/claim_strategy"],
            }
            
            original_agent = task.agent
            if original_agent in fallback_agents:
                task.agent = fallback_agents[original_agent][0]
                self.think("fallback", f"Switching to {task.agent}")
                
                if self._is_premium_agent(task.agent):
                    return await self._execute_premium_task(task, user, session)
            
            # If no fallback agent, skip to level 3
            return await self._apply_fallback(task, user, session, 3, completed)
        
        elif current_level == 3:
            # Simplified local analysis
            return await self._execute_local_fallback(task)
        
        elif current_level == 4:
            # Skip premium step
            self.think("fallback", f"Skipping premium step, continuing with draft")
            return {
                "success": True,
                "agent": task.agent,
                "task": task.task,
                "result": {
                    "output": "Premium step skipped",
                    "skipped": True,
                },
                "skipped": True,
            }
        
        return {"success": False, "error": "All fallbacks exhausted"}
    
    def _get_next_reset_date(self) -> datetime:
        """Get next quota reset date (first of next month)."""
        from django.utils import timezone
        now = timezone.now()
        if now.month == 12:
            return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0)
        return now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0)
    
    def get_thinking_log(self) -> List[Dict[str, str]]:
        """Get the thinking log for display."""
        return self.thinking_log
    
    def format_plan_for_display(self) -> str:
        """Format the plan for display in thinking tab."""
        if not self.plan:
            return "No plan created yet."
        
        lines = [
            f"📋 **Orchestration Plan** ({self.plan.technology})",
            f"⏱️  Estimated time: {self.plan.estimated_time}",
            "",
        ]
        
        for task in self.plan.tasks:
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.SKIPPED: "⏭️",
            }.get(task.status, "  ")
            
            agent_icon = "🔒" if self._is_premium_agent(task.agent) else "📝"
            
            deps = f" (depends on {task.depends_on})" if task.depends_on else ""
            
            lines.append(f"{status_icon} {agent_icon} **{task.id}. {task.task}**{deps}")
        
        return "\n".join(lines)
