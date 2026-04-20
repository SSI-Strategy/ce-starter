# Assignment Workflow

This is the process every assignment follows, from blank directory to a working full-stack application. It is also a pedagogical scaffold: each phase teaches one concept, produces one human-readable artifact, and ends with a check the engineer can run without reading code.

## Who does what

- **The capability engineer (CE) is the architect and product owner.** They decide what the application does, what the data looks like, how the API is shaped, and what "done" means.
- **The agent (Claude Code / Codex) is the implementer.** It writes every line of code. The CE never edits code directly.
- **Learning happens in the questions the CE asks, the decisions they make, and the artifacts they review** — not in reading source files.

If at any point the CE feels they need to read code to make progress, that is a signal the wrong question is being asked. Redirect to the artifact, not the implementation.

## The artifacts

Each phase produces one artifact. The artifact is the contract between phases: it is what the CE reviews, what they show to others, and what the next phase is built on top of.

| Phase | Artifact                             | Form                              |
| ----- | ------------------------------------ | --------------------------------- |
| 1     | Use-case brief                       | `docs/01-brief.md`                |
| 2     | Data model                           | `docs/02-data-model.md`           |
| 3     | Database schema and seed data        | `backend/schema.sql`, running DB  |
| 4     | API and OpenAPI specification        | `/docs` endpoint in the browser   |
| 5     | Frontend application                 | The running app at `:5173`        |
| 6     | Integration proof                    | A short demo the CE records       |

None of these artifacts require reading code to evaluate.

---

## Phase 1 — Brainstorm the Use Case

**Concept.** Every application exists to help someone do something. Before anything is built, the CE needs a sharp answer to three questions: *Who is the user? What are they trying to do? What changes in the world when they do it?*

**Input.** A rough idea, or nothing at all.

**What to do.** Open a conversation with an LLM (this can be the same agent in a separate session, or a chat interface). Use this as the opening prompt:

> I want to build a small local web application. Help me sharpen the idea by asking me questions. I will answer. After five rounds of questions, summarise what we have agreed on as a one-page brief covering: the user, the three core user stories, the key nouns (things the app tracks), and the key verbs (things the user can do).

**Questions the CE should be ready to push on.**

- Is there exactly one kind of user, or several? (More than one means the problem is probably too big for this assignment.)
- For each user story, what is the "before" and "after" state of the world?
- Which nouns are things the user types or picks, and which are things the system generates?
- Which verbs change data, and which only read it?

**Deliverable.** A single-page brief in `docs/01-brief.md` with:

1. One-sentence product description.
2. The user (role, context, what they care about).
3. Three user stories in the form *"As [user], I want to [verb], so that [outcome]."*
4. A list of nouns (will become entities).
5. A list of verbs (will become API operations).

**How to verify.** Read the brief out loud. If any sentence is vague ("users can manage things"), send it back. If the nouns and verbs don't match the user stories, send it back.

**Common pitfalls.** Jumping to features ("it needs a dashboard") before nailing the user story. Inventing a second user type to justify complexity. Writing verbs in technical language ("PATCH the resource") instead of user language ("mark as done").

---

## Phase 2 — Design the Data Model

**Concept.** The data model is the blueprint for the entire application. Every screen, every API call, every SQL query descends from it. Getting this right — before writing a single line of code — is the single highest-leverage decision the CE makes.

**Input.** `docs/01-brief.md`.

**What to ask the agent.**

> Read `docs/01-brief.md`. Based on the nouns listed there, propose a data model for a SQLite database. For each entity, give me: its fields, each field's type and whether it is required, the primary key, any foreign keys, and any uniqueness or check constraints. Show the model as a markdown document, not SQL. Explain every foreign key in one sentence. Then list any ambiguities you had to resolve and why.

**Questions the CE should push on.**

- Is every noun from the brief represented? Is anything present that doesn't appear in the brief?
- For each relationship: is it one-to-one, one-to-many, or many-to-many? Does the foreign-key direction match that?
- What is unique about a row? (If two rows can be identical, the model is usually wrong.)
- What timestamps are needed (`created_at`, `updated_at`)? What happens to child rows when a parent is deleted?
- Which fields have a small fixed set of values? (Those often want a `CHECK` constraint, not a separate table.)

**Deliverable.** `docs/02-data-model.md` with a section per entity, relationships diagrammed as a short bullet list (*"A Task belongs to one Project; a Project has many Tasks"*), and a glossary explaining any domain terms.

**How to verify.** Walk through each user story from phase 1 and confirm the data model can represent every state that story implies, including the "before" state. If any story cannot be expressed as a sequence of inserts/updates on this model, the model is incomplete.

**Common pitfalls.** Modelling what the UI will show rather than what the domain actually is. Over-normalising (a separate table for every value that could be an enum). Under-normalising (repeating the same text in every row instead of a lookup table). Forgetting that deletions cascade somewhere.

---

## Phase 3 — Build the Database

**Concept.** Turning the data model into a real schema exposes every ambiguity that survived phase 2. SQLite is unforgiving in a useful way: if a constraint doesn't match the model, inserts fail.

**Input.** `docs/02-data-model.md`.

**What to ask the agent.**

> Using `docs/02-data-model.md` as the source of truth, generate `backend/schema.sql` for SQLite. Include every primary key, foreign key, uniqueness constraint, and check constraint from the model. Add `created_at` and `updated_at` where the model specifies them. Then generate `backend/seed.sql` with 3–5 rows per table covering the happy path and at least one edge case per user story. Finally, wire the schema to apply automatically on backend startup if the database file does not exist.

**Questions the CE should push on.**

- Does the agent's schema match the model exactly, or did it silently "improve" things?
- What does the agent's seed data demonstrate? If the CE cannot narrate each row ("this is Alice's overdue task"), the seed data is not teaching anything.
- What happens if you try to insert a row that violates a constraint? The CE should ask the agent to run one such insert and show the resulting error.

**Deliverable.** A `backend/app.db` file that can be inspected with the `sqlite3` CLI. The CE should be able to run three queries without the agent's help:

```sql
.tables
.schema <table>
SELECT * FROM <table>;
```

**How to verify.** The CE opens `sqlite3 backend/app.db` and confirms each table from the data model exists, each has sensible rows, and one deliberately-broken insert is rejected.

**Common pitfalls.** Agent generates the schema but forgets `NOT NULL` everywhere. Agent invents tables or columns not in the model. Seed data is generic ("User 1, User 2") and teaches nothing about the domain.

---

## Phase 4 — Design and Build the API

**Concept.** The API is the contract between backend and frontend. Once the OpenAPI spec is stable, the frontend can be built against it in parallel — and any client, not just the one we write, could use it. The OpenAPI spec is the deliverable, not the Python code.

**Input.** `docs/02-data-model.md`, the running database.

**What to ask the agent, in this order.**

First, design:

> Based on the verbs in `docs/01-brief.md` and the entities in `docs/02-data-model.md`, propose a REST API. For each endpoint, give me: the method, the path, the request body shape, the response shape, and which user story it serves. Do not write code yet. Return a markdown table.

Review the table. Push back on anything ugly. Then:

> Implement these endpoints in FastAPI under `backend/app/`. Use Pydantic models for every request and response. Use the stdlib `sqlite3` module. All routes must be prefixed with `/api`. Add a `GET /api/health` that returns `{"status": "ok"}`. Make sure every endpoint appears in the OpenAPI docs at `/docs` with a clear summary and a populated example.

**Questions the CE should push on.**

- Does each endpoint serve a user story? If an endpoint doesn't, why does it exist?
- Are response shapes consistent? (Does a single Task look the same when returned alone and when returned in a list?)
- Are errors shaped consistently? What does the API return when the client sends garbage?
- Is the OpenAPI `summary` for each endpoint readable by a non-technical stakeholder?

**Deliverable.** A running backend at `http://localhost:8000`. The CE opens `http://localhost:8000/docs` and uses the built-in "Try it out" button to exercise every endpoint without touching code.

**How to verify.** The CE completes each user story end-to-end using only the `/docs` UI. If any story can't be completed that way, an endpoint is missing or wrong.

**Common pitfalls.** Agent generates CRUD for every table even when the brief only calls for a few operations. Request/response shapes drift (one endpoint returns `user_id`, another returns `userId`). Error responses are inconsistent. Agent bypasses Pydantic "to keep it simple" and the OpenAPI spec loses its types.

---

## Phase 5 — Build the Frontend

**Concept.** The frontend is a view over the API. Because the API is already specified by OpenAPI, the frontend's job is narrow: render state, capture input, call endpoints. The CE's leverage here is in UX decisions, not in component architecture.

**Input.** A running backend with OpenAPI docs at `/docs`.

**What to ask the agent, in this order.**

First, generate the contract:

> Generate TypeScript types for every request and response in the backend OpenAPI spec at `http://localhost:8000/openapi.json`. Put them in `frontend/src/api/types.ts`. Then write a thin `client.ts` in the same directory with one function per endpoint. Every function must use the generated types — no `any`.

Then, design the UI:

> For each of the three user stories in `docs/01-brief.md`, propose a screen: what the user sees, what they can do, what state changes on the screen after each action. Return a short markdown brief per screen. Do not write components yet.

Then, build:

> Implement the screens from the brief using React and plain CSS. Use the typed client for every API call. Keep each screen to one route. Show loading and error states for every request. Add one Vitest test per screen that renders it with a mocked client.

**Questions the CE should push on.**

- Can the user complete each story on the screen without referring to the API docs? If not, the screen is missing an affordance.
- What happens when the backend is off? When a request fails? When a list is empty?
- Does the screen show the user what changed after an action, or do they have to guess?

**Deliverable.** A running frontend at `http://localhost:5173`. The CE completes each user story from phase 1 end-to-end in the browser, with a human watching.

**How to verify.** Do the demo. No console errors. No unexplained loading spinners. No "the data is there but the screen didn't update."

**Common pitfalls.** Agent ignores the generated types and uses `any`. Loading and error states are skipped "for later" and never added. Screens get crowded with features not in any user story. Vite proxy isn't configured and CORS errors block everything.

---

## Phase 6 — Integrate and Verify

**Concept.** The application is done when a stranger can use it to accomplish the user stories. Anything else is scaffolding.

**What to do.**

1. Kill everything. Start fresh from the repo: `uv sync`, `npm install`, start both servers.
2. Open the frontend. Walk through every user story from phase 1 without touching the API docs or the database directly.
3. Record a 2–3 minute screen capture showing the walkthrough. This is the assignment's submission artifact.
4. Write a short retrospective (`docs/06-retro.md`): what surprised you, what you would do differently, where you pushed back on the agent and why.

**How to verify.** Someone else on the team runs `uv sync && npm install`, starts the servers, watches the recording, and can reproduce the demo on their own machine.

---

## Cross-cutting guidance

### Prompts are the primary artifact of learning

The CE should keep a running log of the prompts they sent the agent at each phase (this will become exhibit A in the retrospective). A good prompt names the artifact it produces, cites the artifact it descends from, and states at least one acceptance criterion. A bad prompt is "add the API."

### When the agent does something unexpected

Do not read the code to figure out what happened. Instead, ask the agent to explain what it did and why, in the language of the artifact for that phase. If the explanation doesn't match the artifact, instruct the agent to align with the artifact — not the other way around.

### When to revise an earlier phase

If phase 4 reveals an ambiguity in the data model, go back to phase 2, update `docs/02-data-model.md`, then instruct the agent to regenerate the schema. Never patch the schema in place without updating the model. The model is the source of truth.

### Size and pacing

A well-scoped assignment fits in one working day. If a phase is taking more than 90 minutes, the scope is too large — or the previous phase's artifact was too vague. The remedy is almost always to go back and sharpen the artifact, not to push harder on the current phase.

---

## Toward an interactive format

This document is the prose version of the workflow. A future interactive form should, at minimum:

- Gate each phase behind the previous phase's artifact existing and passing its check.
- Surface the suggested prompts as copy-buttons the CE can paste into their agent session.
- Let the CE record the prompts they actually used, so the retrospective writes itself.
- Show the current state of the running app (health endpoint, OpenAPI doc count, frontend route count) so the CE always knows which phase they are really in, regardless of which phase they think they are in.
- Never show source code. The interactive app reinforces the core rule: the artifact is the contract, not the implementation.
