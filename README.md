<p align="center">
  <a href="https://openpatent.ai">
    <picture>
      <source srcset="packages/console/app/src/asset/logo-ornate-dark.svg" media="(prefers-color-scheme: dark)">
      <source srcset="packages/console/app/src/asset/logo-ornate-light.svg" media="(prefers-color-scheme: light)">
      <img src="packages/console/app/src/asset/logo-ornate-light.svg" alt="OpenPatent logo">
    </picture>
  </a>
</p>
<p align="center">The open source AI patent department.</p>
<p align="center">
  <a href="https://openpatent.ai/discord"><img alt="Discord" src="https://img.shields.io/discord/1391832426048651334?style=flat-square&label=discord" /></a>
</p>

---

## About OpenPatent

OpenPatent is a free and open source patent suite designed for inventors, patent attorneys, and R&D teams. It provides a comprehensive set of AI-powered tools for the entire patent lifecycle:

- **Patent Search** - Prior art identification using boolean logic and CPC/IPC classification codes
- **Patent Drafting** - Claims and specification drafting with proper legal terminology
- **Patent Examination** - Mock USPTO Examiner to identify potential rejections
- **Patent Interrogation** - Technical disclosure gap analysis
- **Patent Illustration** - Technical drawing descriptions for patent figures

### Key Features

- **Local & Premium Agents** - Choose between free local agents or premium server-side agents
- **Orchestrated Workflows** - Plan and execute complex patent tasks automatically
- **Subscription Tiers** - Free tier for individual inventors, pro/enterprise for firms
- **Provider Agnostic** - Use your own API keys (OpenAI, Anthropic, Google) or local models
- **Open Source** - 100% transparent, auditable, and extensible

---

## Installation

### Desktop App (Beta)

Download the desktop application from [openpatent.ai/download](https://openpatent.ai/download):

| Platform              | Download                                |
| --------------------- | --------------------------------------- |
| macOS (Apple Silicon) | `openpatent-desktop-darwin-aarch64.dmg` |
| macOS (Intel)         | `openpatent-desktop-darwin-x64.dmg`     |
| Windows               | `openpatent-desktop-windows-x64.exe`    |
| Linux                 | `.deb`, `.rpm`, or AppImage             |

```bash
# macOS (Homebrew)
brew install --cask openpatent-desktop
```

### Django Server (For API Access)

For API access, premium agents, and team features:

```bash
# Clone and setup
git clone https://github.com/openpatent/openpatent.git
cd openpatent

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

The server provides:

- REST API for all patent operations
- Premium agent endpoints (GPT-4o powered)
- JWT authentication
- Subscription management (Stripe integration)
- Real-time updates via WebSocket

---

## Agents

OpenPatent includes both local and premium agents:

### Local Agents (Free)

Run locally using your own LLM providers:

| Agent                     | Description                                      |
| ------------------------- | ------------------------------------------------ |
| **Invention Disclosure**  | Analyze invention ideas and extract key features |
| **Patent Drafter**        | Draft patent claims and specification            |
| **Prior Art Searcher**    | Prepare prior art search queries                 |
| **Technical Illustrator** | Create detailed drawing descriptions             |

### Premium Agents (Server)

Run on the OpenPatent server using GPT-4o:

| Agent                        | Free    | Pro       |
| ---------------------------- | ------- | --------- |
| **Mock Examiner**            | 3/month | 50/month  |
| **Office Action Response**   | 0       | 10/month  |
| **Claim Strategy**           | 0       | 10/month  |
| **Specification Perfection** | 0       | 20/month  |
| **Patent Searcher**          | 3/month | 100/month |
| **Patent Drafter**           | 3/month | 200/month |
| **Patent Interrogator**      | 3/month | 200/month |
| **Patent Illustrator**       | 3/month | 150/month |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     OpenPatent Desktop App                          │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Tauri Shell  │  SolidJS UI  │  Local Agents  │  Providers    │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTPS / WebSocket
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OpenPatent Django Server                         │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Auth & Billing  │  Premium Agents  │  Orchestrator  │  API   │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │              PostgreSQL Database                               │ │
│  │  Users, Sessions, Quotas, Agent Definitions, Patent Data       │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## API Documentation

### Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login (get JWT token)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Premium Agents

```bash
# Execute premium agent
curl -X POST http://localhost:8000/api/patent/agents/premium/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "mock_examiner",
    "task": "Review my patent draft",
    "context": {
      "invention_title": "Laser Toaster",
      "claims": ["1. A toaster comprising..."],
      "specification": {"field": "The present invention..."}
    }
  }'
```

### Orchestrator

```bash
# Create plan
curl -X POST http://localhost:8000/api/patent/orchestrator/plan/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Draft a patent for my laser toaster invention",
    "technology": "software"
  }'

# Execute plan
curl -X POST http://localhost:8000/api/patent/orchestrator/execute/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "<plan_uuid>"}'
```

---

## Configuration

### Desktop App

Configure via Settings > Providers:

- **OpenAI** - Use your API key for premium agents
- **Anthropic** - Claude models for local agents
- **Google** - Gemini models
- **Local** - LM Studio, Ollama, or OpenAI-compatible servers

### Django Server

Environment variables in `.env`:

```env
DJANGO_SECRET_KEY=your-secret-key
POSTGRES_DB=openpatent
POSTGRES_USER=openpatent
POSTGRES_PASSWORD=openpatent
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
OPENAI_API_KEY=sk-...
```

---

## Development

### Running Tests

# Django tests

cd openpatent
python manage.py test apps.patent.tests.test_agents

# Frontend tests

cd packages/desktop
bun test

```

### Project Structure

```

openpatent/
├── openpatent_django/ # Django server
│ ├── apps/
│ │ ├── patent/ # Patent agents and models
│ │ │ ├── agents/ # Agent Markdown definitions
│ │ │ ├── services/ # Premium agent implementations
│ │ │ └── tests/ # Integration tests
│ │ ├── accounts/ # Authentication
│ │ ├── billing/ # Stripe integration
│ │ └── api/ # API endpoints
│ └── config/ # Django configuration
├── packages/
│ ├── desktop/ # Tauri desktop app
│ ├── app/ # SolidJS core UI
│ ├── openpatent/ # CLI tool (patent workflow automation)
│ └── sdk/ # SDK for integrations
├── docs/ # Documentation
│ └── PATENT_ARCHITECTURE.md
└── patent_suite/ # Standalone Python patent tools

```

---

## Contributing

OpenPatent is open source and welcomes contributions. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before submitting pull requests.

### Adding New Agents

1. **Local Agent**: Create a Markdown file in `packages/opencode/agent/`
2. **Premium Agent**: Add to `openpatent_django/apps/patent/services/premium_agents.py`
3. **Update Models**: Add quota fields in `openpatent_django/apps/patent/models.py`
4. **Add Tests**: Create tests in `openpatent_django/apps/patent/tests/`

---

## License

OpenPatent is open source under the MIT License. See [LICENSE](./LICENSE) for details.

---

## Links

- **Website**: https://openpatent.ai
- **Documentation**: https://docs.openpatent.ai
- **Discord**: https://openpatent.ai/discord
- **GitHub**: https://github.com/openpatent
```
