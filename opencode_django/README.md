# OpenPatent Django Server

A Django-based server for OpenPatent that provides authentication, premium patent agents, session management, rate limiting, and Stripe payment integration.

## Features

- **Authentication**: JWT-based authentication with email/password
- **Premium Agents**: GPT-4o powered patent agents (Mock Examiner, Office Action Response, Claim Strategy, etc.)
- **Sessions**: PostgreSQL-backed session storage with WebSocket support
- **Rate Limiting**: PostgreSQL sliding window rate limiter
- **Billing**: Stripe subscription management (Free, Pro, Enterprise plans)
- **Orchestrator**: AI-powered task planning and delegation
- **WebSocket**: Real-time session sharing via Django Channels

## Requirements

- Python 3.12+
- PostgreSQL 16+
- Redis 7+ (for Channels)
- Stripe account
- OpenAI API key (for premium agents)

## Quick Start

### 1. Clone and Setup

```bash
cd openpatent_django

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:

- `DJANGO_SECRET_KEY` - Secret key for Django
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - OpenAI API key for premium agents
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key

### 3. Run with Docker

```bash
docker-compose up -d
```

### 4. Run Locally

```bash
# Start PostgreSQL and Redis
docker-compose up db redis -d

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver 0.0.0.0:8000
```

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Get JWT tokens
- `POST /api/auth/refresh/` - Refresh token
- `GET /api/auth/me/` - Get current user

### Patent Agents

- `GET /api/patent/agents/premium/list/` - List available premium agents
- `POST /api/patent/agents/premium/` - Execute premium agent
- `GET /api/patent/agents/` - List unified agents (local + premium)
- `GET /api/patent/agents/<id>/` - Get agent details

### Orchestrator

- `POST /api/patent/orchestrator/plan/` - Create orchestration plan
- `POST /api/patent/orchestrator/execute/` - Execute plan
- `GET /api/patent/orchestrator/templates/` - List templates
- `GET /api/patent/orchestrator/thinking/<id>/` - Get thinking log

### Sessions

- `GET /api/sessions/` - List sessions
- `POST /api/sessions/` - Create session
- `GET /api/sessions/{id}/` - Get session
- `DELETE /api/sessions/{id}/` - Delete session
- `POST /api/sessions/{id}/share/` - Share session
- `DELETE /api/sessions/{id}/share/` - Unshare session
- `GET /api/sessions/{id}/messages/` - Get messages

### Quota & Billing

- `GET /api/patent/quota/` - Get quota status
- `POST /billing/checkout/` - Create Stripe checkout
- `POST /billing/portal/` - Create billing portal session
- `GET /billing/subscription/` - Get subscription status
- `POST /billing/cancel/` - Cancel subscription

### WebSocket

- `WS /ws/share/{session_id}/?secret=xxx` - Share polling

## Premium Agents

| Agent                    | Description                  | Free    | Pro       |
| ------------------------ | ---------------------------- | ------- | --------- |
| Mock Examiner            | USPTO Examiner simulation    | 3/month | 50/month  |
| Office Action Response   | Generate rejection responses | 0       | 10/month  |
| Claim Strategy           | Recommend claim amendments   | 0       | 10/month  |
| Specification Perfection | Improve drafted specs        | 0       | 20/month  |
| Patent Searcher          | Prior art search             | 3/month | 100/month |
| Patent Drafter           | Full specification & claims  | 3/month | 200/month |
| Patent Interrogator      | Disclosure gap analysis      | 3/month | 200/month |
| Patent Illustrator       | Drawing descriptions         | 3/month | 150/month |

## Rate Limits

| Plan       | Requests/Hour | Tokens/Hour |
| ---------- | ------------- | ----------- |
| Free       | 100           | 100,000     |
| Pro        | 500           | 1,000,000   |
| Enterprise | 2,000         | 5,000,000   |

## Stripe Setup

1. Create products and prices in Stripe Dashboard
2. Set price IDs in environment variables:
   - `STRIPE_PRICE_ID_PRO`
   - `STRIPE_PRICE_ID_ENTERPRISE`
3. Set up webhook endpoint: `https://your-domain.com/billing/webhook/`
4. Add webhook secret: `STRIPE_WEBHOOK_SECRET`

## Development

```bash
# Run tests
python manage.py test apps.patent.tests.test_agents

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

## Production Deployment

1. Set `DEBUG=False`
2. Generate secure `DJANGO_SECRET_KEY`
3. Configure allowed hosts
4. Set up SSL/TLS with nginx
5. Use gunicorn with multiple workers

## Project Structure

```
openpatent_django/
├── config/                 # Django configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── core/              # Base models
│   ├── accounts/          # Authentication
│   ├── api/               # REST API & provider proxy
│   ├── sessions/          # Session storage
│   ├── channels/          # WebSocket
│   ├── billing/           # Stripe integration
│   └── patent/            # Patent agents & orchestrator
│       ├── agents/        # Agent Markdown definitions
│       ├── services/      # Premium agent implementations
│       ├── templates/     # Orchestrator templates
│       └── tests/         # Integration tests
├── static/
│   ├── css/main.css
│   └── js/app.js
├── scripts/               # Migration scripts
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```
