# Assignment Stack

All capability-engineer training assignments use the same stack. This keeps difficulty, tooling, and review criteria consistent across assignments so engineers can focus on the work rather than the environment.

## Runtime

Everything runs locally on the engineer's machine. No Docker, no cloud services, no shared infrastructure. Each assignment should start and run with two commands in two terminals (one backend, one frontend).

## Layers

### Database — SQLite

- File-based, zero-install, ships with Python.
- Database file lives at `backend/app.db` and is gitignored.
- Schema is defined in a single `backend/schema.sql` and applied on startup if tables are missing. No migration tool.
- Seed data (if any) in `backend/seed.sql`, applied via a `make seed` / `uv run seed` script.

### Backend — Python + FastAPI

- Python 3.12+.
- [FastAPI](https://fastapi.tiangolo.com/) for the HTTP layer. Automatic OpenAPI docs at `/docs` are part of the learning surface.
- [uv](https://docs.astral.sh/uv/) for dependency management and virtualenv. `uv sync` to install, `uv run` to execute.
- `sqlite3` from the standard library for database access. No ORM. Engineers write SQL.
- Pydantic models for request/response validation.
- Tests in `backend/tests/` using `pytest`.

Entry point: `uv run uvicorn app.main:app --reload --port 8000`

### Frontend — React + Vite

- [Vite](https://vitejs.dev/) with the React + TypeScript template.
- `npm` for package management.
- Plain `fetch` for API calls. No data-fetching library (TanStack Query, SWR, etc.) unless an assignment explicitly introduces one.
- Minimal styling: plain CSS or CSS modules. No Tailwind, no component library, unless an assignment calls for it.
- Tests with [Vitest](https://vitest.dev/) + React Testing Library.

Entry point: `npm run dev` (serves on `http://localhost:5173`)

### Frontend ↔ Backend

- Vite dev server proxies `/api/*` to `http://localhost:8000` (configured in `vite.config.ts`).
- All backend routes are prefixed with `/api`.
- No auth unless an assignment introduces it. Assume single local user.

## Repository layout

Each assignment is a self-contained directory:

```
assignment-name/
  README.md              # The assignment brief
  backend/
    pyproject.toml
    uv.lock
    schema.sql
    seed.sql             # optional
    app/
      main.py
      ...
    tests/
  frontend/
    package.json
    package-lock.json
    vite.config.ts
    src/
      main.tsx
      App.tsx
      ...
```

## Prerequisites

Engineers must have installed, in this order:

1. Python 3.12+ (`python3 --version`)
2. `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
3. Node.js 20+ LTS (`node --version`)

SQLite ships with Python's standard library — no separate install.

## Out of scope

Deliberately excluded to keep assignments comparable and locally runnable:

- Docker, docker-compose
- Postgres, MySQL, or any networked database
- Authentication providers (OAuth, Auth0)
- Deployment (Vercel, Render, Fly, etc.)
- Background workers, queues, cron
- ORMs (SQLAlchemy, Prisma, Drizzle)
- State managers (Redux, Zustand, Jotai)
- Monorepo tooling (Turborepo, Nx)

An individual assignment may introduce **one** of these if the learning goal requires it, but never as default scaffolding.

## Consistency across assignments

Every assignment must:

- Run with `uv sync && uv run ...` in `backend/` and `npm install && npm run dev` in `frontend/`.
- Ship a working `README.md` with setup steps and acceptance criteria.
- Include at least one backend test (pytest) and one frontend test (vitest).
- Expose a `/api/health` endpoint that returns `{"status": "ok"}`.
- Be completable in roughly the same time window (target to be defined separately).
