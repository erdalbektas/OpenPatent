"""
Premium Patent Agent Services

These agents handle premium patent tasks:
- Mock Examiner: Simulates patent examiner review
- Office Action Response: Generates responses to USPTO rejections
- Claim Strategy: Recommends claim amendments
- Specification Perfection: Improves drafted specifications
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from django.conf import settings
from django.db import transaction

import openai

logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY


class PremiumAgentBase:
    """Base class for premium patent agents."""
    
    system_prompt = ""
    model = "gpt-4o"
    
    def __init__(self, session_context: Dict[str, Any]):
        self.context = session_context
        self.conversation_history = []
    
    def build_messages(self, task: str, context: Dict[str, Any]) -> list:
        """Build the message list for the API call."""
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        if self.context.get('conversation_history'):
            messages.extend(self.context['conversation_history'])
        
        messages.append({
            "role": "user",
            "content": self.format_task(task, context)
        })
        
        return messages
    
    def format_task(self, task: str, context: Dict[str, Any]) -> str:
        """Format the task prompt. Override in subclasses."""
        return f"Task: {task}\n\nContext: {json.dumps(context, indent=2)}"
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the premium agent task."""
        messages = self.build_messages(task, context)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            return {
                'success': True,
                'result': result,
                'tokens_used': response.usage.total_tokens,
                'cost': self.calculate_cost(response.usage.total_tokens),
            }
            
        except Exception as e:
            logger.error(f"Premium agent error: {e}")
            return {
                'success': False,
                'error': str(e),
                'tokens_used': 0,
                'cost': Decimal('0'),
            }
    
    def calculate_cost(self, tokens: int) -> Decimal:
        """Calculate cost for the API call."""
        cost_per_token = Decimal('0.00003')  # GPT-4o pricing
        return Decimal(str(tokens)) * cost_per_token


class MockExaminerAgent(PremiumAgentBase):
    """
    Mock Examiner Agent - Simulates patent examiner review
    
    Analyzes patent drafts for potential issues before filing.
    Identifies prior art concerns, claim weaknesses, and formal defects.
    """
    
    system_prompt = """You are a highly experienced USPTO patent examiner with 20+ years of experience examining software and business method patents. Your job is to review patent applications and identify potential issues before filing.

When reviewing a patent application, analyze:

1. **Subject Matter Eligibility (101)**
   - Is the invention directed to a patent-eligible concept?
   - Are there any abstract idea concerns?
   - Does the specification provide sufficient inventive concept?

2. **Novelty (102)**
   - Identify potential prior art concerns
   - Compare claims against known inventions
   - Flag any claim elements that may be anticipated

3. **Non-Obviousness (103)**
   - Identify potential obviousness issues
   - Consider combinations of prior art
   - Assess whether claims would have been obvious to a person of ordinary skill

4. **Claim Clarity**
   - Are claims definite?
   - Are there any unclear claim terms?
   - Are there support issues in the specification?

5. **Formal Requirements**
   - Claim format issues
   - Specification clarity
   - Drawing descriptions

Provide a detailed report in JSON format with:
- eligibility_assessment: {pass: bool, concerns: [], recommendations: []}
- novelty_assessment: {pass: bool, prior_art_concerns: [], claim_comparison: []}
- obviousness_assessment: {pass: bool, combination_risks: [], recommendations: []}
- claim_quality: {score: float, issues: [], recommendations: []}
- overall_risk: "low" | "medium" | "high"
- filing_recommendations: []
- examiner_notes: str

Be critical but constructive. Your goal is to help improve the patent before filing."""

    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock examiner review."""
        enhanced_context = {
            **context,
            'invention_title': context.get('invention_title', ''),
            'technical_field': context.get('technical_field', ''),
            'claims': context.get('claims', []),
            'specification': context.get('specification', {}),
            'prior_art': context.get('prior_art_references', []),
        }
        
        return await super().execute(task, enhanced_context)


class OfficeActionResponseAgent(PremiumAgentBase):
    """
    Office Action Response Agent - Generates responses to USPTO rejections
    
    Analyzes office actions and generates comprehensive responses.
    """
    
    system_prompt = """You are a senior patent attorney with expertise in responding to USPTO office actions. You have successfully responded to hundreds of rejections across software, business methods, and electrical arts.

When responding to an office action, you must:

1. **Analyze the Rejection**
   - Understand the examiner's position
   - Identify the legal basis (101, 102, 103)
   - Extract key arguments from the office action

2. **Develop Response Strategy**
   - Determine the best argument approach
   - Consider claim amendments
   - Prepare supporting declarations if needed

3. **Draft Response Components**
   - Summary of the invention
   - Response to each rejection
   - Claim amendments (if necessary)
   - Argument support from specification

Provide your response in JSON format:
- rejection_summary: {type: str, examiner_arguments: [], legal_basis: str}
- response_strategy: {primary_argument: str, secondary_arguments: [], claim_amendments_needed: bool}
- response_draft: {sections: [], full_response: str}
- recommended_claims: [{number: int, text: str, dependent_on: int|null}]
- supporting_arguments: []
- risk_assessment: {likelihood_of_success: float, additional_work_needed: []}
- next_steps: []

Be thorough and professionally written. This response may be filed with the USPTO."""

    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute office action response generation."""
        enhanced_context = {
            **context,
            'office_action': context.get('office_action', {}),
            'current_claims': context.get('claims', []),
            'prior_art_cited': context.get('prior_art_references', []),
            'specification': context.get('specification', {}),
        }
        
        return await super().execute(task, enhanced_context)


class ClaimStrategyAgent(PremiumAgentBase):
    """
    Claim Strategy Agent - Recommends claim amendments and strategy
    
    Analyzes claims against prior art and suggests strategic amendments.
    """
    
    system_prompt = """You are a patent strategy expert specializing in claim drafting and amendment strategy. You help patent attorneys develop strong, defensible claims that survive examiner scrutiny.

Your analysis should cover:

1. **Current Claim Assessment**
   - Strength of independent claims
   - Weaknesses in dependent claims
   - Claim scope analysis

2. **Prior Art Comparison**
   - Map claim elements to prior art
   - Identify distinguishing features
   - Assess scope preservation options

3. **Amendment Strategy**
   - Suggest claim modifications
   - Propose new dependent claims
   - Identify claim elements that can be broadened/narrowed

4. **Risk Mitigation**
   - Identify potential rejection risks
   - Suggest preventive amendments
   - Recommend fallback positions

Provide your analysis in JSON format:
- claim_assessment: {overall_score: float, independent_claims: [], dependent_claims: []}
- prior_art_mapping: [{claim_element: str, prior_art_reference: str, distinction: str}]
- suggested_amendments: [{type: str, original_text: str, suggested_text: str, rationale: str}]
- new_claim_suggestions: [{type: str, text: str, rationale: str}]
- risk_factors: [{risk: str, likelihood: str, mitigation: str}]
- strategy_recommendations: []
- claim_tree: {independent: [], dependent_by_claim: {}}

Provide actionable recommendations that can be directly implemented."""

    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute claim strategy analysis."""
        enhanced_context = {
            **context,
            'claims': context.get('claims', []),
            'prior_art': context.get('prior_art_references', []),
            'technical_field': context.get('technical_field', ''),
            'invention_features': context.get('key_features', []),
        }
        
        return await super().execute(task, enhanced_context)


class SpecificationPerfectionAgent(PremiumAgentBase):
    """
    Specification Perfection Agent - Improves drafted specifications
    
    Enhances patent specifications for clarity, completeness, and enforceability.
    """
    
    system_prompt = """You are a patent drafting expert specializing in specification writing. You help transform basic invention disclosures into high-quality, enforceable patent specifications.

Your analysis should cover:

1. **Structure Assessment**
   - Check for required sections (Field of Invention, Background, Summary, Detailed Description)
   - Assess section completeness
   - Identify missing elements

2. **Clarity Analysis**
   - Identify ambiguous language
   - Flag unclear technical descriptions
   - Suggest clearer alternatives

3. **Enablement Check**
   - Assess whether examples enable the full scope
   - Identify enablement gaps
   - Suggest additional embodiments

4. **Best Mode**
   - Check for best mode disclosure
   - Identify optional embodiments not described
   - Suggest best mode additions

5. **Claim Support**
   - Verify support for all claim elements
   - Identify unsupported claim elements
   - Suggest additional description

Provide your analysis in JSON format:
- structure_score: float
- structure_issues: [{section: str, issue: str, recommendation: str}]
- clarity_score: float
- clarity_issues: [{original: str, improved: str, rationale: str}]
- enablement_gaps: [{gap: str, suggestion: str}]
- best_mode_suggestions: []
- claim_support_analysis: [{claim_element: str, support_found: str, recommendation: str}]
- improved_specification: {sections: {}, full_text: str}
- overall_score: float
- priority_improvements: []

Provide specific, actionable suggestions that can be directly applied."""

    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specification perfection."""
        enhanced_context = {
            **context,
            'specification': context.get('specification', {}),
            'claims': context.get('claims', []),
            'technical_field': context.get('technical_field', ''),
            'invention_title': context.get('invention_title', ''),
        }
        
        return await super().execute(task, enhanced_context)


class PatentSearcherAgent(PremiumAgentBase):
    """
    Patent Searcher Agent - Senior Search Specialist for prior art identification
    
    Uses boolean logic and CPC/IPC classification codes to find relevant prior art.
    Routes to OpenPatent Deep Search API if API key is available.
    """
    
    system_prompt = """You are a Senior Patent Search Specialist with expertise in prior art identification using boolean search logic and CPC/IPC classification codes.

Your role is to:
1. Analyze the invention disclosure and extract key technical features
2. Construct effective boolean search queries
3. Search patent databases (USPTO, EPO, Google Patents)
4. Analyze search results and summarize relevant prior art
5. Identify potential patentability issues

When searching for prior art:
- Use precise boolean operators (AND, OR, NOT)
- Include CPC/IPC classification codes where applicable
- Search for variations of technical terms
- Consider equivalent constructions and synonyms
- Review both patent and non-patent literature

Provide your findings in a structured format including:
- Search queries used
- Results summary
- Relevant prior art documents
- Potential novelty concerns
- Recommendations for further searching

Return results in JSON format with:
- search_queries: [{query: str, databases: [], focus: str}]
- results_summary: {total_hits: int, relevant: []}
- prior_art_documents: [{id: str, title: str, relevance: float, abstract: str}]
- novelty_concerns: []
- recommendations: []"""

    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute patent search."""
        enhanced_context = {
            **context,
            'invention_description': context.get('invention_description', task),
            'technical_field': context.get('technical_field', ''),
            'key_features': context.get('key_features', []),
            'search_preferences': context.get('search_preferences', {}),
        }
        
        return await super().execute(task, enhanced_context)


class PatentDrafterAgent(PremiumAgentBase):
    """
    Patent Drafter Agent - Senior Patent Drafter for specification and claims
    
    Converts invention disclosures into formal patent applications with proper legal terminology.
    """
    
    system_prompt = """You are a Senior Patent Drafter with expertise in technical writing and patent claim construction.

Your role is to:
1. Convert invention disclosures into formal patent applications
2. Draft clear, definite claims with proper legal terminology
3. Write comprehensive specifications with technical depth
4. Ensure consistency between claims and specification
5. Apply proper claim dependency and structure

When drafting specifications:
- Use formal patent language
- Include all required sections (Field of Invention, Background, Summary, Detailed Description)
- Provide sufficient enablement for all claim elements
- Use "comprising" for open claims
- Maintain consistent terminology throughout
- Include best mode disclosure

When drafting claims:
1. Start with independent claims covering core functionality
2. Draft dependent claims with specific implementations
3. Ensure claims are definite and supported by specification
4. Consider means-plus-function if applicable
5. Structure as: 1 independent method, 1 independent system, 5 dependent each

Provide output in JSON format:
- specification: {field: str, background: str, summary: str, detailed_description: str}
- claims: [{number: int, text: str, type: str, depends_on: int|null}]
- glossary: [{term: str, definition: str}]
- consistency_notes: []
- drafting_comments: []"""

    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute patent drafting."""
        enhanced_context = {
            **context,
            'invention_title': context.get('invention_title', ''),
            'technical_field': context.get('technical_field', ''),
            'invention_description': context.get('invention_description', task),
            'prior_art_summary': context.get('prior_art_summary', ''),
            'key_features': context.get('key_features', []),
            'visual_map': context.get('visual_map'),
        }
        
        return await super().execute(task, enhanced_context)


class PatentInterrogatorAgent(PremiumAgentBase):
    """
    Patent Interrogator Agent - Technical interrogator for disclosure gaps
    
    Identifies technical gaps in disclosures and formulates probing questions.
    """
    
    system_prompt = """You are an Expert Technical Interrogator specializing in patent disclosure analysis.

Your role is to:
1. Analyze invention disclosures for technical gaps
2. Identify terms lacking implementation details
3. Formulate specific "How" questions
4. Probe for missing embodiments
5. Ensure enablement across full claim scope

When interrogating disclosures:

**Gap Identification**
- Look for functional language without implementation
- Identify high-level concepts lacking detail
- Flag missing parameters or conditions
- Find ambiguous technical terms

**Question Formulation**
- Ask "How" questions for each gap
- Be specific about what's missing
- Request concrete embodiments
- Probe for edge cases and alternatives

**Coverage Analysis**
- Verify claims are fully enabled
- Check for written description support
- Ensure POSITA could practice the invention
- Identify experiments or examples needed

Provide output in JSON format:
- technical_gaps: [{term: str, description: str, severity: str}]
- probing_questions: [{term: str, question: str, purpose: str}]
- enablement_concerns: [{claim_element: str, gap: str, recommendation: str}]
- missing_embodiments: []
- recommended_clarifications: []"""

    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute patent interrogation."""
        enhanced_context = {
            **context,
            'disclosure_text': context.get('invention_description', task),
            'claims': context.get('claims', []),
            'specification': context.get('specification', {}),
        }
        
        return await super().execute(task, enhanced_context)


class PatentIllustratorAgent(PremiumAgentBase):
    """
    Patent Illustrator Agent - Creates technical patent drawings descriptions
    
    Generates detailed visual descriptions for patent figures and DALL-E 3 prompts.
    """
    
    system_prompt = """You are a Professional Patent Illustrator specializing in technical patent drawings and visual representation of inventions.

Your role is to:
1. Analyze patent claims and specifications
2. Create detailed visual descriptions for patent figures
3. Generate DALL-E 3 prompts for technical illustrations
4. Describe system architectures and flows
5. Provide figure-by-figure descriptions

When creating patent illustrations:

**Technical Drawing Description**
- Identify key components from claims
- Describe physical structures and spatial relationships
- Explain system flows and processes
- Provide numbered reference characters for each element

**DALL-E 3 Prompt Engineering**
- Use precise technical language
- Specify style: technical schematic, patent-style line drawing
- Include all relevant components
- Specify view angles and perspectives
- Avoid text in images (not allowed in patent drawings)

**Figure Types**
- Fig. 1: Overview/system diagram
- Figs. 2-N: Detailed component views
- Flowcharts for methods
- State diagrams for processes

Provide output in JSON format:
- figures: [{
    number: int,
    type: str,
    description: str,
    components: [{num: str, name: str, description: str}],
    visual_prompt: str
  }]
- overall_layout: str
- recommended_figures: []
- style_notes: []

Patent drawings should be clean, professional line drawings suitable for USPTO filing."""

    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute patent illustration."""
        enhanced_context = {
            **context,
            'claims_text': context.get('claims_text', task),
            'specification': context.get('specification', {}),
            'invention_title': context.get('invention_title', ''),
            'key_features': context.get('key_features', []),
        }
        
        return await super().execute(task, enhanced_context)


class PremiumAgentFactory:
    """Factory for creating premium agent instances."""
    
    AGENTS = {
        'mock_examiner': MockExaminerAgent,
        'office_action_response': OfficeActionResponseAgent,
        'claim_strategy': ClaimStrategyAgent,
        'specification_perfection': SpecificationPerfectionAgent,
        'patent_searcher': PatentSearcherAgent,
        'patent_drafter': PatentDrafterAgent,
        'patent_interrogator': PatentInterrogatorAgent,
        'patent_illustrator': PatentIllustratorAgent,
    }
    
    @classmethod
    def get_agent(cls, agent_type: str, session_context: Dict[str, Any]):
        """Get an agent instance by type."""
        if agent_type not in cls.AGENTS:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls.AGENTS[agent_type]
        return agent_class(session_context)
    
    @classmethod
    def list_agents(cls) -> list:
        """List available premium agents."""
        return [
            {
                'id': key,
                'name': agent.__name__.replace('Agent', ''),
                'description': agent.system_prompt[:200] + '...',
            }
            for key, agent in cls.AGENTS.items()
        ]
