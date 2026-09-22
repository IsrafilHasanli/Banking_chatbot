# Kama Banking Chatbot

[![CI](https://github.com/IsrafilHasanli/Banking_chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/IsrafilHasanli/Banking_chatbot/actions/workflows/ci.yml)

Kama Banking Chatbot is a full-stack banking assistant built with FastAPI, React, PostgreSQL, Qdrant, and LangChain. It provides authenticated conversational banking workflows, including balance checks, transfers, account and card actions, support requests, and retrieval-augmented answers over banking policy and tariff documents.

The project is structured as a practical production-ready portfolio application: configuration is environment-driven, local secrets are excluded, the backend and frontend are documented, and CI validates linting, tests, compilation, and frontend builds.

## Core Capabilities

- Authenticated chat API with PostgreSQL JWT auth or AWS Cognito auth.
- LangChain/Anthropic banking assistant with user-scoped tools.
- Account balance lookup, account creation, card creation, card/account blocking, support ticket creation, and money transfer tooling.
- Retrieval-augmented generation over banking PDF documents using Qdrant.
- Exact and semantic chat caching for eligible general banking questions.
- React/Vite chat UI served by the FastAPI backend at `/ui`.
- Docker Compose infrastructure for PostgreSQL and Qdrant.
- GitHub Actions CI for backend and frontend validation.

## Technology Stack

| Area | Technologies |
| --- | --- |
| Backend | Python 3.12, FastAPI, SQLAlchemy async, asyncpg |
| AI orchestration | LangChain, LangGraph, Anthropic Claude |
| Persistence | PostgreSQL |
| Vector search | Qdrant, sentence-transformers |
| Frontend | React, Vite, lucide-react |
| Auth | Local JWT auth or AWS Cognito |
| Integrations | AWS Lambda email dispatch, SMTP payload support |
| Quality | pytest, Ruff, compileall, GitHub Actions |

## Repository Layout

```text
.
|-- app/
|   |-- agents/          LangChain banking agent assembly
|   |-- api/             Chat and profile routes
|   |-- auth/            Signup, login, JWT, and Cognito auth
|   |-- core/            Config, database, AWS, LLM, shared infrastructure
|   |-- mail/            Email notification integration
|   |-- models/          SQLAlchemy ORM models
|   |-- product/         Product/account HTTP endpoints
|   |-- rag/             PDF ingestion and retrieval logic
|   |-- schemas/         Pydantic request and response schemas
|   |-- services/        Business services and cache policy
|   |-- static/chatbot/  Built frontend assets served by FastAPI
|   `-- tools/           Agent tool adapters
|-- frontend/            React/Vite source application
|-- docs/                Architecture, API, and development documentation
|-- tests/               Backend unit tests
|-- docker-compose.yml   Local PostgreSQL and Qdrant services
`-- Dockerfile           Backend container image
```

## Quick Start

### 1. Clone and Install Backend Dependencies

```bash
git clone https://github.com/IsrafilHasanli/Banking_chatbot.git
cd Banking_chatbot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

On macOS/Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

### 2. Configure Environment

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Edit `.env` and provide real local values. For local development, use:

```env
AUTH_PROVIDER=postgres
SECRET_KEY=replace_with_a_long_random_secret
CLAUDE_API_KEY=your_anthropic_api_key_here
```

### 3. Start Infrastructure

```bash
docker compose up -d postgres qdrant
```

### 4. Apply Database Migrations

```bash
python -m app.core.db.run_migrations
```

### 5. Run the Backend

```bash
python -m uvicorn app.main:app --reload
```

Open:

- UI: `http://127.0.0.1:8000/ui`
- OpenAPI docs: `http://127.0.0.1:8000/docs`

## Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies API calls to `http://127.0.0.1:8000`.

To rebuild the backend-served static UI:

```bash
cd frontend
npm run build
```

The build output is written to `app/static/chatbot`.

## API Overview

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/auth/signup` | Register a user |
| `POST` | `/auth/login` | Authenticate and receive tokens |
| `POST` | `/auth/confirm` | Confirm AWS Cognito signup when using AWS auth |
| `POST` | `/chat` | Send an authenticated chat message |
| `GET` | `/Profile/` | Return the current authenticated user |
| `POST` | `/product/create-account` | Create a bank account for the current user |
| `GET` | `/` | Redirect to `/ui` |

See [docs/api.md](docs/api.md) for request examples.

## Configuration

Configuration is centralized in `app/core/config.py` and loaded from environment variables. The application validates required values during startup.

| Variable | Required | Description |
| --- | --- | --- |
| `AUTH_PROVIDER` | Yes | `postgres` for local JWT auth or `aws` for AWS Cognito |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS` | Yes, unless `DATABASE_URL` is set | PostgreSQL connection settings |
| `DATABASE_URL` | Optional | Full SQLAlchemy async database URL |
| `SECRET_KEY` | Required for `postgres` auth | JWT signing key |
| `CLAUDE_API_KEY` | Yes | Anthropic API key used by the banking agent |
| `CLAUDE_MODEL` | Yes | Anthropic model name |
| `QDRANT_URL` | Required when semantic cache or RAG is enabled | Qdrant endpoint |
| `QDRANT_API_KEY` | Optional | Qdrant API key |
| `CHAT_CACHE_ENABLED` | Optional | Enables exact cache for eligible prompts |
| `CHAT_SEMANTIC_CACHE_ENABLED` | Optional | Enables semantic cache in Qdrant |
| `AWS_CLIENT_ID`, `AWS_REGION`, `AWS_USER_POOL_ID` | Required for `aws` auth | AWS Cognito configuration |
| `SMTP_SERVER`, `MAIL_USER`, `MAIL_PASS` | Required for email delivery integration | Email payload values sent to Lambda |

Use `.env.example` as the source of truth for placeholder values. Never commit `.env`.

## Validation

Run the backend checks:

```bash
pytest
ruff check app tests
python -m compileall app tests
```

Run the frontend build:

```bash
cd frontend
npm ci
npm run build
```

## Docker

Build the backend image:

```bash
docker build -t kama-banking-chatbot .
```

Run the backend container with local environment values:

```bash
docker run --env-file .env -p 8000:8000 kama-banking-chatbot
```

Use Docker Compose for local dependencies:

```bash
docker compose up -d postgres qdrant
```

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Development Guide](docs/development.md)

## Security Notes

- Secrets are read from environment variables and must not be committed.
- `.env`, virtual environments, dependency folders, logs, caches, and local database volumes are ignored.
- Rotate any credential that was previously stored in a local `.env` or shared outside a trusted environment.
- The assistant prompt limits sensitive disclosure, but backend authorization and user-scoped tools are the primary security controls.

## Troubleshooting

| Symptom | Likely Fix |
| --- | --- |
| `Missing database configuration` | Set `DATABASE_URL` or all `DB_*` variables |
| `CLAUDE_API_KEY is required` | Add a valid Anthropic API key to `.env` |
| Qdrant connection error | Start Qdrant and verify `QDRANT_URL` |
| Authentication fails after restart | Keep `SECRET_KEY` stable when using `AUTH_PROVIDER=postgres` |
| Vite build is missing | Run `npm install` or `npm ci` in `frontend/` |

## License

No license file is currently included. Add a license before allowing third-party use, modification, or redistribution.
