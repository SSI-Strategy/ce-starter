# Assignment 05 — Clinical Query Tracker

> A lightweight tracker for data-management queries raised against case-report-form data: who raised it, which subject and field, when it was answered, and how long it aged.

**Category:** Clinical ops
**Primary user:** A clinical data manager watching query aging across a single study.
**Concept this teaches:** Time-derived fields — age_days, is_overdue — computed in the API from stored timestamps rather than stored as mutable columns. Teaches the difference between data and derived views over data.

---

## Before you start

1. Read the top-level [`WORKFLOW.md`](../../WORKFLOW.md). If you already have, re-read Phase 1.
2. Tell your reviewer you picked this assignment. They will push back if scope is wrong — better now than later.
3. Open [`index.html`](./index.html) in a browser (drag the file onto a browser window). It is the interactive version of this page, with copy-buttons on every prompt.


## What you will build

A lightweight tracker for data-management queries raised against case-report-form data: who raised it, which subject and field, when it was answered, and how long it aged.

The deliverables are the same as every assignment in the starter program — they are defined by the workflow, not by the app:

- `docs/01-brief.md` — a one-page brief covering user, three user stories, nouns, verbs
- `docs/02-data-model.md` — the data model as a markdown document, not SQL
- `backend/schema.sql`, `backend/seed.sql`, a running SQLite database
- A FastAPI backend with OpenAPI docs at `http://localhost:8000/docs`
- A React + Vite frontend at `http://localhost:5173`
- `docs/06-retro.md` and a 2–3 minute screen recording of the final demo

## What the brainstorm must lock down

Before you run the Phase-1 prompt, decide which of these you have an opinion on and which you want the LLM to push you on. The decisions you make here shape everything downstream.

1. What is a 'query' attached to — a subject, a visit, a specific field? Pick the smallest unit you can still explain.
2. Who raises queries (DM) and who answers them (site)? Both are represented, but only one event changes the clock.
3. What is the SLA — days to respond? Is 'overdue' computed server-side or client-side, and why?

## Guardrails — deliberately out of scope

- No eCRF integration.
- No user roles beyond one logical DM.
- No query threading — each query has one answer.

---

## Phase-by-phase

Each phase below shows the generic prompt from the starter library plus a hint specific to this assignment. Adapt the prompt; keep the structure.

### Phase 1 — Brainstorm the use case

**Artifact:** `docs/01-brief.md`

Sharpen the idea with an LLM until you can name the user, three user stories, the nouns the app tracks, and the verbs the user performs.

**Prompt:**

```
I want to build a small local web application. Help me sharpen the idea by asking me questions. I will answer. After five rounds of questions, summarise what we have agreed on as a one-page brief covering: the user, the three core user stories, the key nouns (things the app tracks), and the key verbs (things the user can do).
```

**For this assignment:** Write a user story about 'the Monday morning aging report'. That is the reason this app exists.

### Phase 2 — Design the data model

**Artifact:** `docs/02-data-model.md`

Every screen, API call, and query descends from this. Get it right before any code exists.

**Prompt:**

```
Read docs/01-brief.md. Based on the nouns listed there, propose a data model for a SQLite database. For each entity, give me: its fields, each field's type and whether it is required, the primary key, any foreign keys, and any uniqueness or check constraints. Show the model as a markdown document, not SQL. Explain every foreign key in one sentence. Then list any ambiguities you had to resolve and why.
```

**For this assignment:** age_days and is_overdue are not columns. They are derived. Say so in the model document.

### Phase 3 — Build the database

**Artifact:** `backend/schema.sql + app.db`

Turn the model into real SQLite. Constraints fail loudly and expose every ambiguity the model left behind.

**Prompt:**

```
Using docs/02-data-model.md as the source of truth, generate backend/schema.sql for SQLite. Include every primary key, foreign key, uniqueness constraint, and check constraint from the model. Add created_at and updated_at where the model specifies them. Then generate backend/seed.sql with 3-5 rows per table covering the happy path and at least one edge case per user story. Finally, wire the schema to apply automatically on backend startup if the database file does not exist.
```

**For this assignment:** Store opened_at and answered_at as timestamps, not ages. Seed a query that is three weeks old and one that was answered same-day.

### Phase 4 — Design and build the API

**Artifact:** `http://localhost:8000/docs`

Design the endpoints as a markdown table first. Build them second. The OpenAPI spec at /docs is the real deliverable.

**Prompt:**

```
Based on the verbs in docs/01-brief.md and the entities in docs/02-data-model.md, propose a REST API. For each endpoint, give me: the method, the path, the request body shape, the response shape, and which user story it serves. Do not write code yet. Return a markdown table.

Once I approve the table, implement these endpoints in FastAPI under backend/app/. Use Pydantic models for every request and response. Use the stdlib sqlite3 module. All routes must be prefixed with /api. Add a GET /api/health that returns {"status": "ok"}. Make sure every endpoint appears in the OpenAPI docs at /docs with a clear summary and a populated example.
```

**For this assignment:** Compute age and overdue flag in the API response, not in SQL schema and not in the frontend. There is exactly one correct place.

### Phase 5 — Build the frontend

**Artifact:** `http://localhost:5173`

Generate TypeScript types from the OpenAPI spec. Design each screen in markdown. Then build.

**Prompt:**

```
Generate TypeScript types for every request and response in the backend OpenAPI spec at http://localhost:8000/openapi.json. Put them in frontend/src/api/types.ts. Then write a thin client.ts in the same directory with one function per endpoint. Every function must use the generated types — no any.

Then, for each of the three user stories in docs/01-brief.md, propose a screen: what the user sees, what they can do, what state changes after each action. Return a short markdown brief per screen. Do not write components yet.

Once I approve the screens, implement them using React and plain CSS. Use the typed client for every API call. Keep each screen to one route. Show loading and error states for every request. Add one Vitest test per screen that renders it with a mocked client.
```

**For this assignment:** The list screen should colour-code by age bucket. Pick the buckets before the UI is built.

### Phase 6 — Integrate and verify

**Artifact:** `docs/06-retro.md + a 2–3 minute screen recording`

The app is done when a stranger can use it to accomplish the user stories.

**Prompt:**

```
Let's verify. Kill both servers. From the repo root, run `uv sync` in backend/, then `npm install` in frontend/, then start both. Walk me through each user story in the browser. If any story fails or any unexpected error appears, tell me which phase's artifact needs to change — do not patch in place.

Then help me write docs/06-retro.md: what surprised me, what I would do differently, where I pushed back on the agent and why. Include the full prompt log from this session.
```

**For this assignment:** Walk an overdue query to resolved and confirm the 'overdue' indicator disappears. If the UI still shows red, the derivation is cached incorrectly somewhere.


---

## When you are done

- All three user stories complete end-to-end in the browser with no console errors.
- `uv sync && uv run uvicorn app.main:app --reload --port 8000` starts the backend clean.
- `npm install && npm run dev` starts the frontend clean.
- Demo recording saved as `docs/demo.mp4` (or similar) and referenced in the retro.
- Retro in `docs/06-retro.md` with your prompt log.

## Where to get help

- `WORKFLOW.md` at the repo root is authoritative for process questions.
- `STACK.md` at the repo root is authoritative for tooling questions.
- Your reviewer is authoritative for scope questions.
