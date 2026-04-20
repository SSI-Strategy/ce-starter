#!/usr/bin/env python3
"""
Generate per-assignment starter directories under assignments/.

Each assignment directory contains:
  - README.md   (for GitHub browsing)
  - index.html  (opens locally in a browser, styled like the main site)

The source of truth for assignment content lives in ASSIGNMENTS_DATA below.
Re-run this script whenever that data changes.
"""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assignments"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

PHASES = [
    {
        "n": "1",
        "title": "Brainstorm the use case",
        "artifact": "docs/01-brief.md",
        "lede": "Sharpen the idea with an LLM until you can name the user, three user stories, the nouns the app tracks, and the verbs the user performs.",
        "prompt": (
            "I want to build a small local web application. Help me sharpen the idea by asking me "
            "questions. I will answer. After five rounds of questions, summarise what we have agreed "
            "on as a one-page brief covering: the user, the three core user stories, the key nouns "
            "(things the app tracks), and the key verbs (things the user can do)."
        ),
    },
    {
        "n": "2",
        "title": "Design the data model",
        "artifact": "docs/02-data-model.md",
        "lede": "Every screen, API call, and query descends from this. Get it right before any code exists.",
        "prompt": (
            "Read docs/01-brief.md. Based on the nouns listed there, propose a data model for a SQLite "
            "database. For each entity, give me: its fields, each field's type and whether it is "
            "required, the primary key, any foreign keys, and any uniqueness or check constraints. "
            "Show the model as a markdown document, not SQL. Explain every foreign key in one "
            "sentence. Then list any ambiguities you had to resolve and why."
        ),
    },
    {
        "n": "3",
        "title": "Build the database",
        "artifact": "backend/schema.sql + app.db",
        "lede": "Turn the model into real SQLite. Constraints fail loudly and expose every ambiguity the model left behind.",
        "prompt": (
            "Using docs/02-data-model.md as the source of truth, generate backend/schema.sql for "
            "SQLite. Include every primary key, foreign key, uniqueness constraint, and check "
            "constraint from the model. Add created_at and updated_at where the model specifies them. "
            "Then generate backend/seed.sql with 3-5 rows per table covering the happy path and at "
            "least one edge case per user story. Finally, wire the schema to apply automatically on "
            "backend startup if the database file does not exist."
        ),
    },
    {
        "n": "4",
        "title": "Design and build the API",
        "artifact": "http://localhost:8000/docs",
        "lede": "Design the endpoints as a markdown table first. Build them second. The OpenAPI spec at /docs is the real deliverable.",
        "prompt": (
            "Based on the verbs in docs/01-brief.md and the entities in docs/02-data-model.md, "
            "propose a REST API. For each endpoint, give me: the method, the path, the request body "
            "shape, the response shape, and which user story it serves. Do not write code yet. "
            "Return a markdown table.\n\n"
            "Once I approve the table, implement these endpoints in FastAPI under backend/app/. Use "
            "Pydantic models for every request and response. Use the stdlib sqlite3 module. All "
            "routes must be prefixed with /api. Add a GET /api/health that returns "
            "{\"status\": \"ok\"}. Make sure every endpoint appears in the OpenAPI docs at /docs "
            "with a clear summary and a populated example."
        ),
    },
    {
        "n": "5",
        "title": "Build the frontend",
        "artifact": "http://localhost:5173",
        "lede": "Generate TypeScript types from the OpenAPI spec. Design each screen in markdown. Then build.",
        "prompt": (
            "Generate TypeScript types for every request and response in the backend OpenAPI spec at "
            "http://localhost:8000/openapi.json. Put them in frontend/src/api/types.ts. Then write a "
            "thin client.ts in the same directory with one function per endpoint. Every function "
            "must use the generated types — no any.\n\n"
            "Then, for each of the three user stories in docs/01-brief.md, propose a screen: what "
            "the user sees, what they can do, what state changes after each action. Return a short "
            "markdown brief per screen. Do not write components yet.\n\n"
            "Once I approve the screens, implement them using React and plain CSS. Use the typed "
            "client for every API call. Keep each screen to one route. Show loading and error "
            "states for every request. Add one Vitest test per screen that renders it with a mocked "
            "client."
        ),
    },
    {
        "n": "6",
        "title": "Integrate and verify",
        "artifact": "docs/06-retro.md + a 2–3 minute screen recording",
        "lede": "The app is done when a stranger can use it to accomplish the user stories.",
        "prompt": (
            "Let's verify. Kill both servers. From the repo root, run `uv sync` in backend/, then "
            "`npm install` in frontend/, then start both. Walk me through each user story in the "
            "browser. If any story fails or any unexpected error appears, tell me which phase's "
            "artifact needs to change — do not patch in place.\n\n"
            "Then help me write docs/06-retro.md: what surprised me, what I would do differently, "
            "where I pushed back on the agent and why. Include the full prompt log from this "
            "session."
        ),
    },
]


ASSIGNMENTS = [
    {
        "n": "01",
        "slug": "cro-time-invoice-tracker",
        "category": "clinical",
        "category_label": "Clinical ops",
        "title": "CRO Time & Invoice Tracker",
        "pitch": (
            "A local tool where a CRO project manager logs billable hours against studies, sees "
            "month-to-date spend by person, and compares it to a simple monthly budget."
        ),
        "user": "A project manager at a small CRO who owns monthly burn for one or more studies.",
        "anchor": (
            "Before you start, ask your reviewer for a representative CRO invoice and a monthly "
            "time-tracking report. Open both. Notice the vocabulary: study, project, account code, "
            "role, hourly rate, period. Your data model should carry these words."
        ),
        "concept": (
            "Aggregation with GROUP BY across a date range, driven from the UI via query "
            "parameters. The report screen is a pivot the CE designs before the agent builds it."
        ),
        "lock_down": [
            "What is the unit of billable work — a day's entry, an hour's entry, or a whole invoice line? Pick one and defend it.",
            "Is a person's billing rate fixed per project, or per role, or per entry? The model changes depending on the answer.",
            "What counts as 'budget' — a dollar cap per month, per project, per person, or per account code?",
        ],
        "guardrails": [
            "No PDF parsing. The sample invoice is a reference only — not something the app ingests.",
            "No multi-currency. USD everywhere.",
            "No user auth. Single local user.",
            "No approval workflow on time entries — entered is entered.",
        ],
        "phase_hints": {
            "1": "Anchor every user story in a concrete action the PM does today (log hours, check burn, flag an overrun).",
            "2": "Decide how 'billing rate' is stored before you write any SQL. If the rate lives on the person, one row affects every project; if it lives on the time entry, history is preserved. There is no neutral choice.",
            "3": "Seed at least one person with multiple projects so the month-to-date grouping has something to aggregate over.",
            "4": "The month-to-date view almost certainly needs query parameters — /api/report/spend?month=2026-03 or similar. Ask the agent to justify any design that puts the date filter somewhere else.",
            "5": "The report screen is the most interesting piece of UI. Sketch it in the screen brief before any component exists.",
            "6": "Walk the 'flag an overrun' story deliberately. If the UI does not make an overrun obvious, the screen is missing an affordance.",
        },
    },
    {
        "n": "02",
        "slug": "vendor-bid-comparison",
        "category": "clinical",
        "category_label": "Clinical ops",
        "title": "Competitive Vendor Bid Comparison",
        "pitch": (
            "A tool to enter line-item bids from multiple vendors for the same scope of work and "
            "view them side-by-side with totals and per-line deltas."
        ),
        "user": "A sourcing lead evaluating two or three CRO proposals for the same study.",
        "anchor": None,
        "concept": (
            "Pivoting normalised rows into a comparison matrix at the API boundary — not in the "
            "frontend. The shape of the comparison endpoint is the most interesting design "
            "decision in the assignment."
        ),
        "lock_down": [
            "Is 'scope' a fixed list of line items defined before bids come in, or does each vendor define their own? Strongly prefer fixed — otherwise comparison is ill-defined.",
            "What does a line item consist of — description, quantity, unit, unit price? All four?",
            "What is shown as the 'comparison' — lowest bid per line, deltas from the cheapest, or deltas from a baseline vendor?",
        ],
        "guardrails": [
            "No document upload. The sourcing lead enters bids by hand.",
            "No vendor-managed accounts — one local user.",
            "No currency conversion.",
        ],
        "phase_hints": {
            "1": "Write a user story for 'cheapest does not win'. If the story does not exist, the comparison is a calculator instead of a tool.",
            "2": "The scope-as-fixed-list decision is load-bearing. Make sure the model reflects it: line items belong to the RFP, not to a vendor.",
            "3": "Seed two vendors bidding on the same three line items, with at least one vendor missing a line (null bid). Your comparison must handle that.",
            "4": "The comparison endpoint is the headline. Design its response shape on paper before the agent writes any code.",
            "5": "A comparison matrix is hard to render well on narrow screens. Plan for that in the screen brief.",
            "6": "Ask a colleague which vendor they would pick from your app. If they struggle, the comparison screen is not doing its job.",
        },
    },
    {
        "n": "03",
        "slug": "protocol-deviation-log",
        "category": "clinical",
        "category_label": "Clinical ops",
        "title": "Protocol Deviation Log",
        "pitch": (
            "A log where monitors record protocol deviations observed at study sites, categorise "
            "them, and track each one from open to resolved."
        ),
        "user": "A clinical monitor responsible for one study across several sites.",
        "anchor": None,
        "concept": (
            "Workflow status as a first-class domain concept: a status column with a CHECK "
            "constraint, allowed transitions enforced at the API, and an 'overdue' view computed "
            "on the fly."
        ),
        "lock_down": [
            "Fixed enum (Major / Minor / Other) or free-text taxonomy? For starter scope, pick the fixed enum.",
            "What states does a deviation move through — Open, Under review, Resolved, Cancelled? Which transitions are allowed, and from where?",
            "What does 'overdue' mean — days since opened without resolution, against what threshold?",
        ],
        "guardrails": [
            "No audit log / history table. Wanting one is a second assignment.",
            "No file attachments.",
            "No site-user login. The monitor enters deviations observed at sites.",
        ],
        "phase_hints": {
            "1": "Make the monitor's job real in your head. What does a 'bad week' look like — ten deviations across three sites? Write the stories around that.",
            "2": "Status is not just a column — it is a state machine. Define the allowed transitions in the model document, not in your head.",
            "3": "A CHECK constraint on status values is your first line of defence. The API is the second. Without both, drift is inevitable.",
            "4": "Refuse invalid transitions at the API. A 409 Conflict with a useful message is the right answer — not a silent success.",
            "5": "The 'overdue' badge is the single most important piece of UI. Make sure the list screen surfaces it on row one.",
            "6": "Try to move a Resolved deviation back to Open via the UI. If the app lets you, the state machine is leaky.",
        },
    },
    {
        "n": "04",
        "slug": "site-feasibility-tracker",
        "category": "clinical",
        "category_label": "Clinical ops",
        "title": "Study Site Feasibility Tracker",
        "pitch": (
            "A tool for a feasibility lead to track candidate sites for a new study, record each "
            "site's survey answers, and rank them."
        ),
        "user": "A feasibility lead selecting sites for a new trial.",
        "anchor": None,
        "concept": (
            "Modelling a question-answer relationship — either as two tables (Question, Response) "
            "or as a JSON column. Each has trade-offs the CE must articulate."
        ),
        "lock_down": [
            "Are the survey questions the same across all studies, or study-specific? Either works, but pick one — this is the central modelling decision.",
            "How is a site 'ranked' — sum of numeric answers, a separate score field, or sorted by one attribute?",
            "What is the difference between a site (an organisation) and an investigator (a person)? Does this app need both?",
        ],
        "guardrails": [
            "No email-out to sites.",
            "No versioning of surveys.",
            "No branching logic inside a survey.",
        ],
        "phase_hints": {
            "1": "The feasibility lead's question is always 'which three sites do I invite'. Work backwards from that.",
            "2": "Produce two candidate data models side by side — one with Question and Response tables, one with a JSON blob per site. State the trade-offs. Pick one. Write down why.",
            "3": "If you chose the normalised model, seed realistic survey answers across five sites. If you chose JSON, enforce the shape with a CHECK constraint on JSON validity.",
            "4": "The ranking endpoint should accept a scoring strategy as a parameter, not hard-code it. Ask the agent to push back on any implementation that bakes in a single rule.",
            "5": "The list screen is a leaderboard. Design it so the #1 site is visually distinct from #2.",
            "6": "Change the scoring rule and confirm the leaderboard updates without resubmitting survey data. If it does not, scoring is stored somewhere it should not be.",
        },
    },
    {
        "n": "05",
        "slug": "clinical-query-tracker",
        "category": "clinical",
        "category_label": "Clinical ops",
        "title": "Clinical Query Tracker",
        "pitch": (
            "A lightweight tracker for data-management queries raised against case-report-form "
            "data: who raised it, which subject and field, when it was answered, and how long "
            "it aged."
        ),
        "user": "A clinical data manager watching query aging across a single study.",
        "anchor": None,
        "concept": (
            "Time-derived fields — age_days, is_overdue — computed in the API from stored "
            "timestamps rather than stored as mutable columns. Teaches the difference between "
            "data and derived views over data."
        ),
        "lock_down": [
            "What is a 'query' attached to — a subject, a visit, a specific field? Pick the smallest unit you can still explain.",
            "Who raises queries (DM) and who answers them (site)? Both are represented, but only one event changes the clock.",
            "What is the SLA — days to respond? Is 'overdue' computed server-side or client-side, and why?",
        ],
        "guardrails": [
            "No eCRF integration.",
            "No user roles beyond one logical DM.",
            "No query threading — each query has one answer.",
        ],
        "phase_hints": {
            "1": "Write a user story about 'the Monday morning aging report'. That is the reason this app exists.",
            "2": "age_days and is_overdue are not columns. They are derived. Say so in the model document.",
            "3": "Store opened_at and answered_at as timestamps, not ages. Seed a query that is three weeks old and one that was answered same-day.",
            "4": "Compute age and overdue flag in the API response, not in SQL schema and not in the frontend. There is exactly one correct place.",
            "5": "The list screen should colour-code by age bucket. Pick the buckets before the UI is built.",
            "6": "Walk an overdue query to resolved and confirm the 'overdue' indicator disappears. If the UI still shows red, the derivation is cached incorrectly somewhere.",
        },
    },
    {
        "n": "06",
        "slug": "habit-tracker",
        "category": "general",
        "category_label": "General-purpose",
        "title": "Habit Tracker",
        "pitch": (
            "A personal tool to define recurring habits, check them off daily, and see streaks "
            "and a weekly completion rate."
        ),
        "user": "You. This is a tool you would actually use.",
        "anchor": None,
        "concept": (
            "Computed-on-read fields (streak length, completion rate) versus stored fields, and "
            "how much of that logic belongs in SQL versus Python."
        ),
        "lock_down": [
            "What is a habit — just a name, or does it carry a target (e.g., 'three times per week')?",
            "What is a check-in — a boolean per day, or can it carry a count or a note?",
            "What is a 'streak' — consecutive days, or consecutive expected days? Your answer changes the aggregation.",
        ],
        "guardrails": [
            "No reminders or scheduling.",
            "No multi-user.",
            "No calendar integration.",
        ],
        "phase_hints": {
            "1": "Pick one habit you actually want to track. Use that habit in every user story. Abstract habits make vague apps.",
            "2": "Decide whether a streak is a stored field or a derived one. Derived is the right answer; make sure your model reflects that.",
            "3": "Seed a month of check-ins with at least one missed day, so the streak logic has something to break on.",
            "4": "Return streak and completion-rate in the GET /habits response, computed on the fly. Do not store them.",
            "5": "The grid of days is the screen. Spend your design time there.",
            "6": "Check off yesterday and confirm your streak updates. If it does not, the computed-on-read promise is broken somewhere.",
        },
    },
    {
        "n": "07",
        "slug": "standup-blocker-log",
        "category": "general",
        "category_label": "General-purpose",
        "title": "Team Standup & Blocker Log",
        "pitch": (
            "A tool a small team uses to post a short daily update and list their current "
            "blockers, and a screen that shows all open blockers across the team, sorted by age."
        ),
        "user": "A team lead running async standups for four to six people.",
        "anchor": None,
        "concept": (
            "A uniqueness constraint (UNIQUE(user_id, date)) as a real design choice with "
            "behavioural consequences — and what the API does when the constraint fires."
        ),
        "lock_down": [
            "Is a blocker attached to a standup entry, or independent? If independent, standups are almost vestigial.",
            "Who resolves a blocker — the person who raised it, anyone, the team lead?",
            "Does the app enforce one standup per person per day, or allow many? Both are defensible; pick one.",
        ],
        "guardrails": [
            "No login.",
            "No Slack/email notifications.",
            "No historical analytics beyond 'how old is this blocker'.",
        ],
        "phase_hints": {
            "1": "Name the six people on the imaginary team. Use their names in the stories. This keeps the model real.",
            "2": "If you enforce one standup per person per day, put UNIQUE(user_id, date) in the model document — not as an afterthought in the schema.",
            "3": "Seed one day where every person submitted, and one where two people are missing. The open-blockers view should handle both.",
            "4": "When the client posts a duplicate standup, the API returns 409, not 500. Verify this manually in /docs.",
            "5": "The all-blockers screen is the money view. Age-in-days is the sort key. Red for old, grey for fresh.",
            "6": "Submit two standups as the same user on the same day. Confirm the second one errors cleanly.",
        },
    },
    {
        "n": "08",
        "slug": "expense-splitter",
        "category": "general",
        "category_label": "General-purpose",
        "title": "Expense Splitter (lite)",
        "pitch": (
            "A small group tracks shared expenses — who paid, how much, for whom — and the app "
            "computes who owes whom."
        ),
        "user": "A four-person apartment or a trip group.",
        "anchor": None,
        "concept": (
            "Derived balances — never store 'what Alice owes Bob'. Always compute from the "
            "expense log. A clean example of single-source-of-truth thinking."
        ),
        "lock_down": [
            "Is every expense split equally among all members, or can each expense specify which subset it applies to?",
            "Does 'who owes whom' settle through a central pool, or as direct pairs? Pairs is simpler but produces n² lines.",
            "What does 'settle' mean — a record that zeroes balances up to that point, or just a UI filter?",
        ],
        "guardrails": [
            "No OAuth with any group-chat tool.",
            "No currencies.",
            "Max ten members in a group — enforce with a CHECK constraint.",
        ],
        "phase_hints": {
            "1": "Use a real group: name the four people and list three expenses they genuinely had last month.",
            "2": "Balances are not columns. Write 'derived' in the model for every balance-like concept. If a teammate asks 'where is balance stored', the answer is nowhere.",
            "3": "Seed expenses such that at least one person owes and one person is owed. If everyone is even, the derivation is not tested.",
            "4": "The GET /balances endpoint returns the full n × n matrix (or the direct-pair list). Its shape is the most interesting API decision.",
            "5": "The balance screen is the headline. Make 'you owe' and 'you are owed' visually distinct at a glance.",
            "6": "Add a new expense and confirm every balance in the UI updates. If any row is stale, you are caching derived state where you should not.",
        },
    },
    {
        "n": "09",
        "slug": "reading-list",
        "category": "general",
        "category_label": "General-purpose",
        "title": "Reading List",
        "pitch": (
            "A personal tracker for books: want-to-read, reading, finished; with a rating and "
            "a short note per book, and a pages-per-week report."
        ),
        "user": "You. Again. Pick books you would actually read.",
        "anchor": None,
        "concept": (
            "Normalisation as a reversible decision — produce two candidate data models "
            "(author-as-string vs Author-as-table), state the trade-offs, then pick one."
        ),
        "lock_down": [
            "Is an author a separate entity (normalised) or just a text field on the book?",
            "How is 'pages read per week' derived — from a reading-session log, or just from start and end dates on a book?",
            "What does it mean to move a book from 'reading' back to 'want to read'?",
        ],
        "guardrails": [
            "No book-cover image upload.",
            "No ISBN lookups against external APIs.",
            "No recommendations engine.",
        ],
        "phase_hints": {
            "1": "Pick ten real books you have read or want to read. Use them in your seed data. Abstract 'Book 1' seed data teaches nothing.",
            "2": "The author question is load-bearing. Write out both candidate models and list the consequences of each. Then pick.",
            "3": "If you normalised authors, seed two books by the same author so the relationship has something to test.",
            "4": "The pages-per-week report is an aggregation across sessions or books. Design its endpoint shape before the agent writes it.",
            "5": "The list screen probably wants status as a left-edge indicator. Try it with and without; keep what communicates faster.",
            "6": "Move a book backwards through states. If the app resists ('books cannot unfinish'), decide if that is a feature or a bug.",
        },
    },
    {
        "n": "10",
        "slug": "agent-skill-library",
        "category": "general",
        "category_label": "General-purpose",
        "title": "Agent Skill Library",
        "pitch": (
            "A catalogue of agent 'skills' (name, description, tags, when-to-trigger, example "
            "prompts) with search and filtering. A companion tool for the work this team is "
            "actually doing."
        ),
        "user": "A CE who wants to remember and re-find skills they or their team have written.",
        "anchor": (
            "Before you start, open two or three existing agent skills on disk — "
            "~/.claude/skills/*/SKILL.md. Notice the structure. Your app stores metadata about "
            "skills, not the skill content itself."
        ),
        "concept": (
            "Many-to-many relationships (Skill ↔ Tag) and the API shape that makes filtering by "
            "multiple tags feel natural. Also a small, honest lesson in SQLite's LIKE for search "
            "before reaching for anything fancier."
        ),
        "lock_down": [
            "What fields does a skill carry, and which are searchable versus merely displayed?",
            "Are tags free-form strings or a controlled vocabulary? Your answer determines whether there is a Tag table.",
            "What does 'search' mean — substring match on name/description, tag filter, or both combined?",
        ],
        "guardrails": [
            "No markdown renderer in the UI — show raw text.",
            "No versioning of skills.",
            "No import from external file formats.",
        ],
        "phase_hints": {
            "1": "Write three user stories as the skills author, not as a consumer. 'Find the skill I wrote last week' is a real story.",
            "2": "If tags are a controlled vocabulary, draw the three tables (Skill, Tag, SkillTag) explicitly. If free-form, decide whether you still want a separate Tag table for listing.",
            "3": "Seed fifteen skills with overlapping tags. Without overlap, the filter UI does not teach anything.",
            "4": "The filter-by-multiple-tags endpoint is the interesting one. Discuss AND vs OR semantics with the agent before it writes code. Pick one.",
            "5": "The list screen probably wants tag chips that are clickable filters. That is the teaching moment.",
            "6": "Filter by two tags simultaneously in the UI. If the intersection logic is wrong, you will notice immediately.",
        },
    },
]


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

README_TPL = """# Assignment {n} — {title}

> {pitch}

**Category:** {category_label}
**Primary user:** {user}
**Concept this teaches:** {concept}

---

## Before you start

1. Read the top-level [`WORKFLOW.md`](../../WORKFLOW.md). If you already have, re-read Phase 1.
2. Tell your reviewer you picked this assignment. They will push back if scope is wrong — better now than later.
3. Open [`index.html`](./index.html) in a browser (drag the file onto a browser window). It is the interactive version of this page, with copy-buttons on every prompt.
{anchor_md}

## What you will build

{pitch}

The deliverables are the same as every assignment in the starter program — they are defined by the workflow, not by the app:

- `docs/01-brief.md` — a one-page brief covering user, three user stories, nouns, verbs
- `docs/02-data-model.md` — the data model as a markdown document, not SQL
- `backend/schema.sql`, `backend/seed.sql`, a running SQLite database
- A FastAPI backend with OpenAPI docs at `http://localhost:8000/docs`
- A React + Vite frontend at `http://localhost:5173`
- `docs/06-retro.md` and a 2–3 minute screen recording of the final demo

## What the brainstorm must lock down

Before you run the Phase-1 prompt, decide which of these you have an opinion on and which you want the LLM to push you on. The decisions you make here shape everything downstream.

{lock_down_md}

## Guardrails — deliberately out of scope

{guardrails_md}

---

## Phase-by-phase

Each phase below shows the generic prompt from the starter library plus a hint specific to this assignment. Adapt the prompt; keep the structure.

{phases_md}

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
"""


INDEX_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Assignment {n} — {title} · CE Starter</title>
  <meta name="description" content="{pitch_attr}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../../styles.css" />
  <style>
    .assignment-hero {{ padding: clamp(56px, 9vw, 96px) 0 clamp(32px, 5vw, 56px); }}
    .breadcrumb {{ font-size: 13px; color: var(--ink-muted); margin-bottom: 28px; }}
    .breadcrumb a {{ color: var(--ink-muted); text-decoration: none; }}
    .breadcrumb a:hover {{ color: var(--ink); }}
    .breadcrumb span {{ margin: 0 8px; color: var(--ink-subtle); }}
    .hero-meta {{ display: flex; gap: 16px; flex-wrap: wrap; align-items: center; margin-bottom: 24px; }}
    .hero-meta .big-num {{ font-family: var(--font-display); font-variation-settings: "opsz" 144; font-size: 72px; line-height: 0.85; color: var(--accent); font-weight: 500; letter-spacing: -0.04em; }}
    .hero-meta .cat-tag {{ font-size: 11px; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; padding: 6px 12px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); }}
    .a-title {{ font-family: var(--font-display); font-variation-settings: "opsz" 144; font-weight: 500; font-size: clamp(34px, 5vw, 56px); line-height: 1.04; letter-spacing: -0.025em; margin: 0 0 20px; max-width: 18ch; }}
    .a-pitch {{ font-size: clamp(17px, 1.4vw, 20px); color: var(--ink-muted); max-width: 60ch; margin: 0; }}
    .facts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-top: 44px; padding: 28px 0 0; border-top: 1px solid var(--rule); }}
    .fact-label {{ font-size: 11px; font-weight: 600; letter-spacing: 0.16em; text-transform: uppercase; color: var(--ink-subtle); margin: 0 0 6px; }}
    .fact-body {{ margin: 0; font-size: 15px; color: var(--ink); line-height: 1.5; }}
    .callout {{ background: var(--surface); border: 1px solid var(--rule); border-left: 3px solid var(--accent); border-radius: var(--radius); padding: 22px 26px; margin: 0 0 32px; }}
    .callout h3 {{ font-family: var(--font-display); font-variation-settings: "opsz" 36; font-size: 18px; font-weight: 500; margin: 0 0 8px; }}
    .callout p {{ margin: 0; color: var(--ink-muted); font-size: 15px; line-height: 1.55; }}
    .lock-down, .guardrails {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }}
    .lock-down li, .guardrails li {{ padding: 16px 20px; background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius-sm); color: var(--ink-muted); font-size: 15px; line-height: 1.55; display: grid; grid-template-columns: 28px 1fr; gap: 14px; }}
    .lock-down li::before {{ content: "→"; color: var(--accent); font-weight: 600; }}
    .guardrails li::before {{ content: "×"; color: #b4524c; font-weight: 600; font-size: 18px; }}
    .phase-block {{ background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius); padding: 28px 30px 30px; margin-bottom: 20px; }}
    .phase-head-row {{ display: flex; align-items: baseline; gap: 18px; margin-bottom: 10px; flex-wrap: wrap; }}
    .phase-num {{ font-family: var(--font-display); font-variation-settings: "opsz" 48; font-size: 32px; font-weight: 500; color: var(--accent); line-height: 1; }}
    .phase-num::before {{ content: "0"; }}
    .phase-block h3 {{ font-family: var(--font-display); font-variation-settings: "opsz" 48; font-size: 22px; font-weight: 500; margin: 0; line-height: 1.15; }}
    .phase-artifact {{ font-family: var(--font-mono); font-size: 12px; color: var(--ink-subtle); margin-left: auto; }}
    .phase-lede {{ color: var(--ink-muted); margin: 0 0 18px; font-size: 15.5px; }}
    .phase-hint {{ background: var(--bg-alt); border-radius: var(--radius-sm); padding: 14px 18px; margin-top: 16px; font-size: 14.5px; color: var(--ink); line-height: 1.55; }}
    .phase-hint-label {{ font-size: 11px; font-weight: 600; letter-spacing: 0.16em; text-transform: uppercase; color: var(--accent); margin-right: 8px; }}
    .back-cta {{ display: inline-flex; align-items: center; gap: 8px; padding: 11px 20px; border: 1px solid var(--rule-strong); border-radius: 999px; font-size: 14px; font-weight: 500; text-decoration: none; color: var(--ink); background: transparent; transition: all 140ms ease; }}
    .back-cta:hover {{ border-color: var(--ink); }}
    .section-title {{ font-family: var(--font-display); font-variation-settings: "opsz" 64; font-size: clamp(24px, 3vw, 32px); font-weight: 500; letter-spacing: -0.015em; margin: 0 0 24px; }}
  </style>
</head>
<body>
  <header class="site-nav is-stuck">
    <div class="nav-inner">
      <a href="../../index.html" class="brand">
        <span class="brand-mark">CE</span>
        <span class="brand-text">Starter Program</span>
      </a>
      <nav class="nav-links" aria-label="Primary">
        <a href="../../index.html#stack">Stack</a>
        <a href="../../index.html#workflow">Workflow</a>
        <a href="../../index.html#prompts">Prompts</a>
        <a href="../../index.html#assignments">Assignments</a>
      </nav>
    </div>
  </header>

  <main>
    <section class="assignment-hero">
      <div class="wrap">
        <p class="breadcrumb">
          <a href="../../index.html">CE Starter</a><span>/</span>
          <a href="../../index.html#assignments">Assignments</a><span>/</span>
          {n}
        </p>
        <div class="hero-meta">
          <span class="big-num">{n}</span>
          <span class="cat-tag">{category_label}</span>
        </div>
        <h1 class="a-title">{title}</h1>
        <p class="a-pitch">{pitch}</p>
        <dl class="facts">
          <div>
            <p class="fact-label">Primary user</p>
            <p class="fact-body">{user}</p>
          </div>
          <div>
            <p class="fact-label">Concept this teaches</p>
            <p class="fact-body">{concept}</p>
          </div>
          <div>
            <p class="fact-label">Envelope</p>
            <p class="fact-body">4 ± 1 entities · 3 user stories · 3 ± 1 screens · one aggregation report · one state transition</p>
          </div>
        </dl>
      </div>
    </section>

    {anchor_section}

    <section class="section">
      <div class="wrap">
        <h2 class="section-title">Before you start — the three decisions</h2>
        <p class="lede-sm" style="margin: 0 0 32px;">Your Phase-1 brainstorm must lock these down. Do not start the data model before all three have an answer.</p>
        <ul class="lock-down">
          {lock_down_html}
        </ul>
      </div>
    </section>

    <section class="section section-alt">
      <div class="wrap">
        <h2 class="section-title">The six phases</h2>
        <p class="lede-sm" style="margin: 0 0 32px;">Each phase shows the generic prompt plus a hint specific to this assignment. Copy the prompt. Adapt its references. Keep its structure.</p>
        {phases_html}
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <h2 class="section-title">Deliberately out of scope</h2>
        <p class="lede-sm" style="margin: 0 0 32px;">If the agent tries to add any of these to your app, push back. They do not serve the three user stories.</p>
        <ul class="guardrails">
          {guardrails_html}
        </ul>
      </div>
    </section>

    <section class="section section-alt">
      <div class="wrap" style="text-align: center;">
        <h2 class="section-title" style="margin-bottom: 12px;">Ready?</h2>
        <p class="lede" style="margin: 0 auto 24px;">Create your own copy of the template repo. Clone it. Open a fresh agent session in the cloned directory and start with the Phase-1 prompt above.</p>
        <p style="margin: 0 0 36px; display: flex; gap: 14px; justify-content: center; flex-wrap: wrap;">
          <a href="https://github.com/SSI-Strategy/ce-{n}-{slug}/generate" target="_blank" rel="noopener" class="btn btn-primary">Use this template</a>
          <a href="https://github.com/SSI-Strategy/ce-{n}-{slug}" target="_blank" rel="noopener" class="btn btn-secondary">View the repo</a>
        </p>
        <a href="../../index.html#assignments" class="back-cta">All assignments</a>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div>
        <p class="footer-brand">Capability Engineer Starter Program</p>
        <p class="footer-text">Assignment {n} of 10 · {title}</p>
      </div>
      <div class="footer-links">
        <a href="../../STACK.md">STACK.md</a>
        <a href="../../WORKFLOW.md">WORKFLOW.md</a>
        <a href="../../ASSIGNMENTS.md">ASSIGNMENTS.md</a>
      </div>
    </div>
  </footer>

  <script>
    document.querySelectorAll("[data-copy]").forEach(btn => {{
      btn.addEventListener("click", async () => {{
        const text = btn.parentElement.querySelector(".prompt-text").textContent;
        try {{ await navigator.clipboard.writeText(text); }} catch {{ /* fallback skipped */ }}
        btn.textContent = "Copied";
        btn.classList.add("is-copied");
        setTimeout(() => {{ btn.textContent = "Copy"; btn.classList.remove("is-copied"); }}, 1600);
      }});
    }});
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------

def esc(s: str) -> str:
    return html.escape(s, quote=True)


def render_readme(a: dict) -> str:
    anchor_md = f"\n4. {a['anchor']}\n" if a.get("anchor") else ""

    lock_lines = "\n".join(f"{i+1}. {q}" for i, q in enumerate(a["lock_down"]))
    guard_lines = "\n".join(f"- {g}" for g in a["guardrails"])

    phase_chunks = []
    for p in PHASES:
        hint = a["phase_hints"].get(p["n"], "")
        chunk = f"""### Phase {p['n']} — {p['title']}

**Artifact:** `{p['artifact']}`

{p['lede']}

**Prompt:**

```
{p['prompt']}
```

**For this assignment:** {hint}
"""
        phase_chunks.append(chunk)
    phases_md = "\n".join(phase_chunks)

    return README_TPL.format(
        n=a["n"],
        title=a["title"],
        pitch=a["pitch"],
        category_label=a["category_label"],
        user=a["user"],
        concept=a["concept"],
        anchor_md=anchor_md,
        lock_down_md=lock_lines,
        guardrails_md=guard_lines,
        phases_md=phases_md,
    )


def render_index(a: dict) -> str:
    lock_down_html = "\n          ".join(
        f"<li>{esc(q)}</li>" for q in a["lock_down"]
    )
    guardrails_html = "\n          ".join(
        f"<li>{esc(g)}</li>" for g in a["guardrails"]
    )

    phase_blocks = []
    for p in PHASES:
        hint = a["phase_hints"].get(p["n"], "")
        block = f"""<article class="phase-block">
          <div class="phase-head-row">
            <span class="phase-num">{p['n']}</span>
            <h3>{esc(p['title'])}</h3>
            <span class="phase-artifact">→ {esc(p['artifact'])}</span>
          </div>
          <p class="phase-lede">{esc(p['lede'])}</p>
          <div class="prompt-body">
            <button class="copy-btn" type="button" data-copy>Copy</button>
            <span class="prompt-text">{esc(p['prompt'])}</span>
          </div>
          <div class="phase-hint"><span class="phase-hint-label">For this assignment</span>{esc(hint)}</div>
        </article>"""
        phase_blocks.append(block)
    phases_html = "\n        ".join(phase_blocks)

    anchor_section = ""
    if a.get("anchor"):
        anchor_section = f"""<section class="section"><div class="wrap"><div class="callout"><h3>Anchor your thinking in the real thing</h3><p>{esc(a['anchor'])}</p></div></div></section>"""

    return INDEX_TPL.format(
        n=a["n"],
        slug=a["slug"],
        title=esc(a["title"]),
        pitch=esc(a["pitch"]),
        pitch_attr=esc(a["pitch"]),
        category_label=esc(a["category_label"]),
        user=esc(a["user"]),
        concept=esc(a["concept"]),
        anchor_section=anchor_section,
        lock_down_html=lock_down_html,
        phases_html=phases_html,
        guardrails_html=guardrails_html,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    index_entries = []
    for a in ASSIGNMENTS:
        dirname = f"{a['n']}-{a['slug']}"
        d = OUT / dirname
        d.mkdir()
        (d / "README.md").write_text(render_readme(a), encoding="utf-8")
        (d / "index.html").write_text(render_index(a), encoding="utf-8")
        index_entries.append(f"- [{a['n']} · {a['title']}](./{dirname}/) — {a['pitch']}")
        print(f"  wrote assignments/{dirname}/")

    toc = f"""# Assignments

Ten starter assignments. Each directory is a standalone starting point — open its `index.html` in a browser for the interactive version, or read `README.md` on GitHub.

{chr(10).join(index_entries)}

See [`ASSIGNMENTS.md`](../ASSIGNMENTS.md) at the repo root for the full catalogue and selection rationale.
"""
    (OUT / "README.md").write_text(toc, encoding="utf-8")
    print(f"  wrote assignments/README.md")


if __name__ == "__main__":
    main()
