# Kama Banking Chatbot

Kama Banking Chatbot is a FastAPI and React banking assistant prototype. It provides authenticated chat, account and card actions, support request creation, balance checks, transfers, and retrieval-augmented answers over banking tariff and policy PDFs.

## Features

- FastAPI backend with JWT or AWS Cognito authentication modes.
- LangChain/Anthropic-powered banking assistant with scoped tools for balances, transfers, cards, accounts, support tickets, and banking FAQ retrieval.
- PostgreSQL persistence for users, accounts, cards, support requests, and chat cache records.
- Qdrant vector search for document retrieval and optional semantic chat caching.
- Vite/React chat UI served by the backend at `/ui`.
- Docker Compose services for PostgreSQL and Qdrant.

## Technology Stack

- Python 3.12, FastAPI, SQLAlchemy async, asyncpg
- LangChain, LangGraph, Anthropic Claude
- PostgreSQL, Qdrant
- React, Vite, lucide-react
- AWS Cognito and Lambda integrations when `AUTH_PROVIDER=aws`

## Repository Structure

```text
app/
  agents/            LangChain banking agent assembly
  api/               Chat and profile HTTP routes
  auth/              Authentication, JWT, Cognito, and user registration
  core/              Configuration, database, AWS, LLM, and shared errors
  mail/              Email notification integration
  models/            SQLAlchemy ORM models
  product/           Product API endpoints and account creation service
  rag/               PDF ingestion and retrieval helpers
  schemas/           Pydantic request/response schemas
  services/          Business services for products, support, and chat cache
  static/chatbot/    Built frontend assets served at /ui
  tools/             Agent tool adapters
frontend/            Vite/React source for the chat UI
tests/               Unit tests for pure backend behavior
docs/                Architecture and development notes
```

## Prerequisites

- Python 3.12
- Node.js 20 or newer for frontend development
- Docker and Docker Compose for PostgreSQL and Qdrant
- An Anthropic API key for the banking assistant

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

For development and tests:

```bash
pip install -r requirements-dev.txt
```

For frontend development:

```bash
cd frontend
npm install
npm run build
```

The frontend build writes static files to `app/static/chatbot`.

## Environment Setup

Copy `.env.example` to `.env` and replace placeholder values. Do not commit `.env`.

For local PostgreSQL authentication, set:

```env
AUTH_PROVIDER=postgres
SECRET_KEY=replace_with_a_long_random_secret
```

For AWS Cognito authentication, set `AUTH_PROVIDER=aws` and provide the Cognito variables listed in `.env.example`.

## Running Locally

Start infrastructure:

```bash
docker compose up -d postgres qdrant
```

Apply database migrations:

```bash
python -m app.core.db.run_migrations
```

Run the backend:

```bash
python -m uvicorn app.main:app --reload
```

Open the UI at `http://127.0.0.1:8000/ui`.

For frontend-only development with API proxying:

```bash
cd frontend
npm run dev
```

## Tests

```bash
pytest
python -m compileall app tests
```

## Docker

Build and run the backend image after creating a local `.env`:

```bash
docker build -t kama-banking-chatbot .
docker run --env-file .env -p 8000:8000 kama-banking-chatbot
```

Use `docker compose up -d postgres qdrant` for local infrastructure services.

## Configuration

Configuration is centralized in `app/core/config.py` and loaded from environment variables. Secrets must be supplied through `.env`, deployment secrets, or the hosting environment. The application validates required configuration at startup.

Important variables include:

- `AUTH_PROVIDER`: `postgres` or `aws`
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`, or `DATABASE_URL`
- `SECRET_KEY` for PostgreSQL JWT auth
- `CLAUDE_API_KEY` and `CLAUDE_MODEL`
- `QDRANT_URL` and optional `QDRANT_API_KEY`
- `CHAT_CACHE_ENABLED`, `CHAT_SEMANTIC_CACHE_ENABLED`
- AWS Cognito variables when using AWS auth

## Security Notes

- Never commit `.env`, real credentials, logs, local databases, IDE metadata, or dependency folders.
- Rotate credentials if they were ever committed or shared outside a trusted local environment.
- The assistant prompt instructs the model not to reveal hidden instructions or sensitive user/backend data, but backend authorization and tool scoping remain the primary security boundaries.

## Troubleshooting

- `Missing database configuration`: check database variables or set `DATABASE_URL`.
- `CLAUDE_API_KEY is required`: set an Anthropic API key in your environment.
- Qdrant connection errors: confirm Qdrant is running and `QDRANT_URL` matches the service address.
- Authentication failures in local mode: ensure `AUTH_PROVIDER=postgres` and `SECRET_KEY` is stable between restarts.

## License

No license file is currently included. Add a license before publishing if you want others to use, modify, or redistribute the project.
