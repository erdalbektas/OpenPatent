# Patent Suite Architecture

## Overview

The openpatent Patent Suite is a comprehensive system for patent drafting, search, and analysis. It consists of:

1. **Local Agents** - Run in the desktop application using user's own LLM providers
2. **Premium Agents** - Run on the Django server using OpenAI GPT-4o
3. **Orchestrator** - Plans and delegates tasks to appropriate agents

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           openpatent Desktop App                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        packages/desktop                                   │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │   Tauri     │  │   SolidJS   │  │   Local     │  │  Local      │    │ │
│  │  │   Shell     │  │     UI      │  │   Agents    │  │  Providers  │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTPS / WebSocket
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         openpatent Django Server                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                         openpatent_django                                   │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │  Auth &     │  │  Premium    │  │  Orchestrator│ │  Provider   │    │ │
│  │  │  Billing    │  │  Agents     │  │             │  │  Proxy      │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  │                                                                        │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    PostgreSQL Database                            │   │ │
│  │  │  - Users, Sessions, Quotas                                      │   │ │
│  │  │  - Agent Definitions, Versions                                  │   │ │
│  │  │  - Patent Sessions, Claims, Office Actions                      │   │ │
│  │  └─────────────────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Optional Future
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Future: Mobile & Web Clients                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  Mobile     │  │   Web       │  │  Document   │  │  Team       │        │ │
│  │  App        │  │   App       │  │  Sync       │  │  Sharing    │        │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Agent Types

### Local Agents (Free)

Run locally in the desktop application. Use the user's configured LLM providers.

| Agent                             | Description                                      | Mode     |
| --------------------------------- | ------------------------------------------------ | -------- |
| **Invention Disclosure**          | Analyze invention ideas and extract key features | primary  |
| **Patent Drafter**                | Draft patent claims and specification            | primary  |
| **Prior Art Searcher**            | Prepare and structure prior art search queries   | subagent |
| **Technical Drawing Description** | Create detailed drawing descriptions             | subagent |

### Premium Agents (Server)

Run on the Django server using OpenAI GPT-4o. Require subscription.

| Agent                        | Description                             | Free Tier | Pro Tier  |
| ---------------------------- | --------------------------------------- | --------- | --------- |
| **Mock Examiner**            | Simulates USPTO examiner review         | 3/month   | 50/month  |
| **Office Action Response**   | Generates responses to USPTO rejections | 0         | 10/month  |
| **Claim Strategy**           | Recommends claim amendments             | 0         | 10/month  |
| **Specification Perfection** | Improves drafted specifications         | 0         | 20/month  |
| **Patent Searcher**          | Prior art search with boolean logic     | 3/month   | 100/month |
| **Patent Drafter**           | Full specification and claims drafting  | 3/month   | 200/month |
| **Patent Interrogator**      | Identifies disclosure gaps              | 3/month   | 200/month |
| **Patent Illustrator**       | Creates technical drawing descriptions  | 3/month   | 150/month |

## Directory Structure

```
openpatent_django/
├── apps/
│   ├── patent/
│   │   ├── agents/              # Agent Markdown definitions
│   │   │   ├── patent_searcher.md
│   │   │   ├── patent_drafter.md
│   │   │   ├── patent_examiner.md
│   │   │   ├── patent_interrogator.md
│   │   │   └── patent_illustrator.md
│   │   ├── migrations/
│   │   ├── models.py            # AgentDefinition, AgentVersion, etc.
│   │   ├── services/
│   │   │   ├── orchestrator.py  # Planning and delegation
│   │   │   └── premium_agents.py # Premium agent implementations
│   │   ├── templates/           # Orchestrator templates
│   │   ├── tests/
│   │   │   └── test_agents.py   # Integration tests
│   │   ├── views.py             # API endpoints
│   │   └── urls.py              # URL routing
│   └── ...
└── ...

packages/desktop/
└── src/
    └── components/
        └── dialog-settings.tsx  # Agent management UI
```

## API Endpoints

### Authentication

```
POST /api/auth/register/     # Register new user
POST /api/auth/login/        # Get JWT tokens
POST /api/auth/refresh/      # Refresh token
```

### Agents

```
GET  /api/patent/agents/premium/list/    # List premium agents
GET  /api/patent/agents/                  # List unified agents (local + premium)
GET  /api/patent/agents/<id>/             # Get agent details
POST /api/patent/agents/create/           # Create new agent
PATCH /api/patent/agents/<id>/update/     # Update agent
```

### Premium Agent Execution

```
POST /api/patent/agents/premium/          # Execute premium agent
```

Request body:

```json
{
  "agent_type": "mock_examiner",
  "session_id": "uuid",
  "task": "Review my patent draft",
  "context": {
    "invention_title": "...",
    "claims": [...],
    "specification": {...}
  }
}
```

### Orchestrator

```
POST /api/patent/orchestrator/plan/       # Create orchestration plan
POST /api/patent/orchestrator/execute/    # Execute plan
GET  /api/patent/orchestrator/templates/  # List templates
GET  /api/patent/orchestrator/thinking/<id>/  # Get thinking log
```

### Quota & Billing

```
GET /api/patent/quota/                    # Get quota status
POST /billing/checkout/                   # Create Stripe checkout
POST /billing/portal/                     # Billing portal
```

## Database Schema

### Core Models

```
AgentDefinition
├── id: str (primary key)
├── name: str
├── description: text
├── agent_type: str (local/premium)
├── category: str (drafting, review, analysis, etc.)
├── is_active: bool
├── is_published: bool
├── current_version: str
├── allowed_modes: json
├── color: str
├── icon: str
├── tags: json
└── created_by: FK to User

AgentVersion
├── agent: FK to AgentDefinition
├── version: str (v1, v2, etc.)
├── system_prompt: text
├── changelog: text
├── config_snapshot: json
└── is_active_version: bool

SubscriptionQuota
├── user: FK to User (one-to-one)
├── tier: str (free/pro/enterprise)
├── [agent]_used: int (per agent)
└── [agent]_limit: int (per agent)

PatentSession
├── id: str (UUID)
├── user: FK to User
├── title: str
├── status: str
├── invention_disclosure: json
├── claims: json
├── specification: json
└── ...
```

## Agent System Prompts

All premium agents use GPT-4o with the following settings:

- **Model**: gpt-4o
- **Temperature**: 0.3
- **Max Tokens**: 4000
- **Response Format**: JSON object

### Example: Mock Examiner System Prompt

```python
"""You are a highly experienced USPTO patent examiner with 20+ years of
experience examining software and business method patents. Your job is to
review patent applications and identify potential issues before filing.

When reviewing a patent application, analyze:
1. Subject Matter Eligibility (101)
2. Novelty (102)
3. Non-Obviousness (103)
4. Claim Clarity
5. Formal Requirements

Provide a detailed report in JSON format with:
- eligibility_assessment: {...}
- novelty_assessment: {...}
- obviousness_assessment: {...}
- claim_quality: {...}
- overall_risk: "low" | "medium" | "high"
- filing_recommendations: []
- examiner_notes: str
"""
```

## Orchestrator

The orchestrator plans and delegates tasks to appropriate agents:

1. **Plan Creation**: Uses LLM to create task plan based on user request
2. **Task Delegation**: Routes tasks to local or premium agents
3. **Fallback Handling**: Retries with same agent, different agent, simplified analysis, or skips
4. **Progress Tracking**: Maintains thinking log for UI display

### Fallback Levels

1. **Level 1**: Retry with same agent
2. **Level 2**: Try different agent configuration
3. **Level 3**: Simplified local analysis
4. **Level 4**: Skip premium step, continue with draft

## Subscription Tiers

| Feature                  | Free    | Pro       | Enterprise |
| ------------------------ | ------- | --------- | ---------- |
| Mock Examiner            | 3/month | 50/month  | Unlimited  |
| Office Action Response   | 0       | 10/month  | Unlimited  |
| Claim Strategy           | 0       | 10/month  | Unlimited  |
| Specification Perfection | 0       | 20/month  | Unlimited  |
| Patent Searcher          | 3/month | 100/month | Unlimited  |
| Patent Drafter           | 3/month | 200/month | Unlimited  |
| Patent Interrogator      | 3/month | 200/month | Unlimited  |
| Patent Illustrator       | 3/month | 150/month | Unlimited  |

## Development

### Running Tests

```bash
cd openpatent_django
python manage.py test apps.patent.tests.test_agents
```

### Creating New Agents

1. **Local Agent**: Create Markdown file in `.openpatent/agent/`
2. **Premium Agent**: Add to `premium_agents.py` and `AgentDefinition` model

### Database Migrations

```bash
cd openpatent_django
python manage.py makemigrations patent
python manage.py migrate
```

## Future Enhancements

1. **Mobile App**: iOS/Android apps connecting to Django server
2. **Web Interface**: Browser-based patent drafting
3. **Document Sync**: Cloud storage for patent documents
4. **Team Sharing**: Collaborative patent drafting
5. **Additional Agents**: Design-around search, provisional filing, etc.
