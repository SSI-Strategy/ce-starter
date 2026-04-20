# Assignment 10 — Agent Skill Library

> A catalogue of agent 'skills' (name, description, tags, when-to-trigger, example prompts) with search and filtering. A companion tool for the work this team is actually doing.

**Category:** General-purpose
**Primary user:** A CE who wants to remember and re-find skills they or their team have written.
**Concept this teaches:** Many-to-many relationships (Skill ↔ Tag) and the API shape that makes filtering by multiple tags feel natural. Also a small, honest lesson in SQLite's LIKE for search before reaching for anything fancier.

---

## Before you start

1. Read the top-level [`WORKFLOW.md`](../../WORKFLOW.md). If you already have, re-read Phase 1.
2. Tell your reviewer you picked this assignment. They will push back if scope is wrong — better now than later.
3. Open [`index.html`](./index.html) in a browser (drag the file onto a browser window). It is the interactive version of this page, with copy-buttons on every prompt.

4. Before you start, open two or three existing agent skills on disk — ~/.claude/skills/*/SKILL.md. Notice the structure. Your app stores metadata about skills, not the skill content itself.


## What you will build

A catalogue of agent 'skills' (name, description, tags, when-to-trigger, example prompts) with search and filtering. A companion tool for the work this team is actually doing.

The deliverables are the same as every assignment in the starter program — they are defined by the workflow, not by the app:

- `docs/01-brief.md` — a one-page brief covering user, three user stories, nouns, verbs
- `docs/02-data-model.md` — the data model as a markdown document, not SQL
- `backend/schema.sql`, `backend/seed.sql`, a running SQLite database
- A FastAPI backend with OpenAPI docs at `http://localhost:8000/docs`
- A React + Vite frontend at `http://localhost:5173`
- `docs/06-retro.md` and a 2–3 minute screen recording of the final demo

## What the brainstorm must lock down

Before you run the Phase-1 prompt, decide which of these you have an opinion on and which you want the LLM to push you on. The decisions you make here shape everything downstream.

1. What fields does a skill carry, and which are searchable versus merely displayed?
2. Are tags free-form strings or a controlled vocabulary? Your answer determines whether there is a Tag table.
3. What does 'search' mean — substring match on name/description, tag filter, or both combined?

## Guardrails — deliberately out of scope

- No markdown renderer in the UI — show raw text.
- No versioning of skills.
- No import from external file formats.

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

**For this assignment:** Write three user stories as the skills author, not as a consumer. 'Find the skill I wrote last week' is a real story.

### Phase 2 — Design the data model

**Artifact:** `docs/02-data-model.md`

Every screen, API call, and query descends from this. Get it right before any code exists.

**Prompt:**

```
Read docs/01-brief.md. Based on the nouns listed there, propose a data model for a SQLite database. For each entity, give me: its fields, each field's type and whether it is required, the primary key, any foreign keys, and any uniqueness or check constraints. Show the model as a markdown document, not SQL. Explain every foreign key in one sentence. Then list any ambiguities you had to resolve and why.
```

**For this assignment:** If tags are a controlled vocabulary, draw the three tables (Skill, Tag, SkillTag) explicitly. If free-form, decide whether you still want a separate Tag table for listing.

### Phase 3 — Build the database

**Artifact:** `backend/schema.sql + app.db`

Turn the model into real SQLite. Constraints fail loudly and expose every ambiguity the model left behind.

**Prompt:**

```
Using docs/02-data-model.md as the source of truth, generate backend/schema.sql for SQLite. Include every primary key, foreign key, uniqueness constraint, and check constraint from the model. Add created_at and updated_at where the model specifies them. Then generate backend/seed.sql with 3-5 rows per table covering the happy path and at least one edge case per user story. Finally, wire the schema to apply automatically on backend startup if the database file does not exist.
```

**For this assignment:** Seed fifteen skills with overlapping tags. Without overlap, the filter UI does not teach anything.

### Phase 4 — Design and build the API

**Artifact:** `http://localhost:8000/docs`

Design the endpoints as a markdown table first. Build them second. The OpenAPI spec at /docs is the real deliverable.

**Prompt:**

```
Based on the verbs in docs/01-brief.md and the entities in docs/02-data-model.md, propose a REST API. For each endpoint, give me: the method, the path, the request body shape, the response shape, and which user story it serves. Do not write code yet. Return a markdown table.

Once I approve the table, implement these endpoints in FastAPI under backend/app/. Use Pydantic models for every request and response. Use the stdlib sqlite3 module. All routes must be prefixed with /api. Add a GET /api/health that returns {"status": "ok"}. Make sure every endpoint appears in the OpenAPI docs at /docs with a clear summary and a populated example.
```

**For this assignment:** The filter-by-multiple-tags endpoint is the interesting one. Discuss AND vs OR semantics with the agent before it writes code. Pick one.

### Phase 5 — Build the frontend

**Artifact:** `http://localhost:5173`

Generate TypeScript types from the OpenAPI spec. Design each screen in markdown. Then build.

**Prompt:**

```
Generate TypeScript types for every request and response in the backend OpenAPI spec at http://localhost:8000/openapi.json. Put them in frontend/src/api/types.ts. Then write a thin client.ts in the same directory with one function per endpoint. Every function must use the generated types — no any.

Then, for each of the three user stories in docs/01-brief.md, propose a screen: what the user sees, what they can do, what state changes after each action. Return a short markdown brief per screen. Do not write components yet.

Once I approve the screens, implement them using React and plain CSS. Use the typed client for every API call. Keep each screen to one route. Show loading and error states for every request. Add one Vitest test per screen that renders it with a mocked client.
```

**For this assignment:** The list screen probably wants tag chips that are clickable filters. That is the teaching moment.

### Phase 6 — Integrate and verify

**Artifact:** `docs/06-retro.md + a 2–3 minute screen recording`

The app is done when a stranger can use it to accomplish the user stories.

**Prompt:**

```
Let's verify. Kill both servers. From the repo root, run `uv sync` in backend/, then `npm install` in frontend/, then start both. Walk me through each user story in the browser. If any story fails or any unexpected error appears, tell me which phase's artifact needs to change — do not patch in place.

Then help me write docs/06-retro.md: what surprised me, what I would do differently, where I pushed back on the agent and why. Include the full prompt log from this session.
```

**For this assignment:** Filter by two tags simultaneously in the UI. If the intersection logic is wrong, you will notice immediately.


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
