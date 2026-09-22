# Development Guide

This guide covers local setup, development workflow, validation, and repository hygiene.

## Backend Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Edit `.env` with local values. For day-to-day development, use local PostgreSQL auth unless AWS Cognito is specifically being tested:

```env
AUTH_PROVIDER=postgres
SECRET_KEY=replace_with_a_long_random_secret
```

## Local Services

Start PostgreSQL and Qdrant:

```bash
docker compose up -d postgres qdrant
```

Apply migrations:

```bash
python -m app.core.db.run_migrations
```

Run the backend:

```bash
python -m uvicorn app.main:app --reload
```

The backend serves:

- API docs at `http://127.0.0.1:8000/docs`
- Built UI at `http://127.0.0.1:8000/ui`

## Frontend Workflow

Install dependencies:

```bash
cd frontend
npm install
```

Run Vite during UI development:

```bash
npm run dev
```

Build static assets for the backend:

```bash
npm run build
```

The build output is written to `app/static/chatbot`.

## Validation Checklist

Run before opening a pull request or publishing changes:

```bash
pytest
ruff check app tests
python -m compileall app tests
cd frontend
npm ci
npm run build
```

The GitHub Actions workflow runs the same core backend and frontend checks.

## Database Changes

Add schema changes as SQL migration files under:

```text
app/core/db/migrations/
```

Use a timestamped filename and keep migrations idempotent where practical. The migration runner records applied filenames in `schema_migrations`.

## Configuration Guidelines

- Add new settings to `app/core/config.py`.
- Document new environment variables in `.env.example` and `README.md`.
- Avoid reading environment variables directly from route handlers or business services.
- Do not add real credentials to examples, docs, tests, or fixtures.

## Code Organization Guidelines

- Put HTTP-specific logic in route modules.
- Put business behavior in `app/services`.
- Put SQLAlchemy models in `app/models`.
- Put LangChain tool wrappers in `app/tools`.
- Keep provider/client setup in `app/core`.
- Add small focused tests for behavior that can run without live cloud services.

## Repository Hygiene

Do not commit:

- `.env` or other secret files
- `.venv`
- `node_modules`
- logs
- IDE metadata
- Python caches
- local database volumes
- generated temporary exports

The root `.gitignore` and `.dockerignore` already cover these paths.

## Publishing Notes

Before making the repository public, confirm:

- `.env` is absent from Git status and history.
- `.env.example` contains placeholders only.
- tests and builds pass locally.
- credentials used during development have been rotated if they were ever exposed outside the local environment.
