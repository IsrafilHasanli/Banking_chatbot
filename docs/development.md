# Development

## Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env
docker compose up -d postgres qdrant
python -m app.core.db.run_migrations
python -m uvicorn app.main:app --reload
```

Use `AUTH_PROVIDER=postgres` for local development unless you have AWS Cognito configured.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies API calls to `http://127.0.0.1:8000`.

To update the backend-served static UI:

```bash
cd frontend
npm run build
```

## Validation

```bash
pytest
python -m compileall app tests
```

## Public Repository Hygiene

- Do not commit `.env`, logs, IDE files, `node_modules`, `.venv`, caches, or local database volumes.
- Keep `.env.example` placeholder-only.
- Prefer adding small tests around behavior that can be checked without live cloud services.
