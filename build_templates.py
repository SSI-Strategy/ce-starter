#!/usr/bin/env python3
"""
Generate ten standalone template repositories under templates/.

Each template is a self-contained starting point for one assignment:
  - README.md             human-readable overview + quickstart
  - index.html            styled assignment page (same content as the subdir
                           page in assignments/, but with local stylesheet)
  - styles.css            copy of the site stylesheet
  - .gitignore
  - docs/.gitkeep
  - backend/              FastAPI skeleton with /api/health, uv-managed
  - frontend/             Vite + React + TypeScript skeleton with /api proxy

These directories are meant to be pushed as their own GitHub repositories
(one per assignment) and marked as GitHub templates.

Re-run this script whenever ASSIGNMENTS (in build_assignments.py) changes.
"""

from __future__ import annotations

import html
import shutil
from pathlib import Path

from build_assignments import ASSIGNMENTS, PHASES

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "templates"
STYLES_SRC = ROOT / "styles.css"

SITE_BASE = "https://ssi-strategy.github.io/ce-starter"
REPO_BASE = "https://github.com/SSI-Strategy/ce-starter"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# ---------------------------------------------------------------------------
# Templates: landing page (index.html) — adapted from build_assignments.py
# with self-contained stylesheet and external links to ce-starter.
# ---------------------------------------------------------------------------

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
  <link rel="stylesheet" href="styles.css" />
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
    .quickstart {{ background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius); padding: 26px 30px; }}
    .quickstart pre {{ background: var(--mono-bg); border-radius: var(--radius-sm); padding: 16px 20px; overflow-x: auto; font-family: var(--font-mono); font-size: 13px; line-height: 1.6; margin: 10px 0 18px; }}
    .quickstart p {{ margin: 0 0 12px; color: var(--ink-muted); font-size: 15px; }}
  </style>
</head>
<body>
  <header class="site-nav is-stuck">
    <div class="nav-inner">
      <a href="{site}/" class="brand">
        <span class="brand-mark">CE</span>
        <span class="brand-text">Starter Program</span>
      </a>
      <nav class="nav-links" aria-label="Primary">
        <a href="{site}/#stack">Stack</a>
        <a href="{site}/#workflow">Workflow</a>
        <a href="{site}/#prompts">Prompts</a>
        <a href="{site}/#assignments">Assignments</a>
      </nav>
    </div>
  </header>

  <main>
    <section class="assignment-hero">
      <div class="wrap">
        <p class="breadcrumb">
          <a href="{site}/">CE Starter</a><span>/</span>
          <a href="{site}/#assignments">Assignments</a><span>/</span>
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

    <section class="section">
      <div class="wrap">
        <h2 class="section-title">Quickstart</h2>
        <div class="quickstart">
          <p>From the root of your cloned template repository, open two terminals.</p>
          <p><strong>Terminal 1 — backend</strong> (FastAPI on <code>:8000</code>, OpenAPI at <code>/docs</code>):</p>
          <pre>cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000</pre>
          <p><strong>Terminal 2 — frontend</strong> (Vite on <code>:5173</code>, proxies <code>/api/*</code> to backend):</p>
          <pre>cd frontend
npm install
npm run dev</pre>
          <p>The scaffolding is deliberately minimal. There is a <code>/api/health</code> endpoint and an empty React app. Everything else is for you to design with your agent, phase by phase, below.</p>
        </div>
      </div>
    </section>

    {anchor_section}

    <section class="section section-alt">
      <div class="wrap">
        <h2 class="section-title">Before you start — the three decisions</h2>
        <p class="lede-sm" style="margin: 0 0 32px;">Your Phase-1 brainstorm must lock these down. Do not start the data model before all three have an answer.</p>
        <ul class="lock-down">
          {lock_down_html}
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <h2 class="section-title">The six phases</h2>
        <p class="lede-sm" style="margin: 0 0 32px;">Each phase shows the generic prompt plus a hint specific to this assignment. Copy the prompt. Adapt its references. Keep its structure.</p>
        {phases_html}
      </div>
    </section>

    <section class="section section-alt">
      <div class="wrap">
        <h2 class="section-title">Deliberately out of scope</h2>
        <p class="lede-sm" style="margin: 0 0 32px;">If the agent tries to add any of these to your app, push back. They do not serve the three user stories.</p>
        <ul class="guardrails">
          {guardrails_html}
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="wrap" style="text-align: center;">
        <h2 class="section-title" style="margin-bottom: 12px;">Ready?</h2>
        <p class="lede" style="margin: 0 auto 32px;">Open a fresh agent session in this directory. Start with the Phase-1 prompt above. Keep a log of every prompt you send — that log is the evidence of your learning.</p>
        <a href="{site}/#assignments" class="back-cta">All assignments</a>
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
        <a href="{site}/STACK.md">STACK.md</a>
        <a href="{site}/WORKFLOW.md">WORKFLOW.md</a>
        <a href="{site}/ASSIGNMENTS.md">ASSIGNMENTS.md</a>
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
        site=SITE_BASE,
    )


# ---------------------------------------------------------------------------
# Template: README
# ---------------------------------------------------------------------------

README_TPL = """# {title}

> Assignment {n} of 10 · Capability Engineer Starter Program

{pitch}

- **Primary user:** {user}
- **Concept this teaches:** {concept}
- **Envelope:** 4 ± 1 entities · 3 user stories · 3 ± 1 screens · one aggregation report · one state transition

---

## How to use this repository

This is a **template repository**. Click "Use this template" on GitHub (or run `gh repo create <your-name> --template SSI-Strategy/ce-{n}-{slug} --public`) to make your own copy. Then clone it and work in your copy — not in the template itself.

The template ships with an empty but runnable backend (FastAPI + SQLite + uv) and frontend (Vite + React + TypeScript). Everything else is for you to design with your agent, phase by phase, following [the starter workflow]({site}/#workflow).

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Node.js 20+ LTS

### Run the skeleton

**Terminal 1 — backend**

```
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` to see the OpenAPI UI. The only endpoint is `GET /api/health`. The rest is for you to design.

**Terminal 2 — frontend**

```
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The Vite dev server proxies `/api/*` to the backend on `:8000`.

### Browse the assignment brief

Open `index.html` in a browser. It is the interactive version of this README, with copy-buttons on every phase prompt.

---

## What you will build

{pitch}

The deliverables are the same as every assignment in the starter program — they are defined by the workflow, not by the app:

- `docs/01-brief.md` — a one-page brief covering user, three user stories, nouns, verbs
- `docs/02-data-model.md` — the data model as a markdown document, not SQL
- `backend/schema.sql`, `backend/seed.sql`, a running SQLite database
- A FastAPI backend with OpenAPI docs at `http://localhost:8000/docs`
- A React + Vite frontend at `http://localhost:5173`
- `docs/06-retro.md` and a 2–3 minute screen recording of the final demo

---

## Before you start — the three decisions

Your Phase-1 brainstorm must lock these down. Do not start the data model before all three have an answer.

{lock_down_md}

## Deliberately out of scope

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

---

## References

- [Starter program overview]({site}/)
- [STACK.md]({site}/STACK.md)
- [WORKFLOW.md]({site}/WORKFLOW.md)
- [Full assignment catalogue]({site}/ASSIGNMENTS.md)
"""


def render_readme(a: dict) -> str:
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

    return README_TPL.format(
        n=a["n"],
        slug=a["slug"],
        title=a["title"],
        pitch=a["pitch"],
        user=a["user"],
        concept=a["concept"],
        lock_down_md=lock_lines,
        guardrails_md=guard_lines,
        phases_md="\n".join(phase_chunks),
        site=SITE_BASE,
    )


# ---------------------------------------------------------------------------
# Backend scaffold (static across assignments)
# ---------------------------------------------------------------------------

BACKEND_PYPROJECT = """[project]
name = "{slug}-backend"
version = "0.1.0"
description = "Backend for the CE starter assignment: {title}"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic>=2.8",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8",
    "httpx>=0.27",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]
"""

BACKEND_PYTHON_VERSION = "3.12\n"

BACKEND_MAIN = '''"""FastAPI entrypoint for the {title} assignment.

This is a skeleton. As you work through the workflow phases, you will add
schema, endpoints, and Pydantic models under this package. The only thing
that ships with the template is a health endpoint and automatic application
of schema.sql on startup when the database file does not exist.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import FastAPI

BACKEND_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BACKEND_DIR / "app.db"
SCHEMA_PATH = BACKEND_DIR / "schema.sql"
SEED_PATH = BACKEND_DIR / "seed.sql"


def _init_db_if_missing() -> None:
    if DB_PATH.exists():
        return
    if not SCHEMA_PATH.exists():
        return
    schema = SCHEMA_PATH.read_text()
    if not schema.strip():
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema)
        if SEED_PATH.exists() and SEED_PATH.read_text().strip():
            conn.executescript(SEED_PATH.read_text())
        conn.commit()
    finally:
        conn.close()


app = FastAPI(
    title="{title}",
    description="Capability Engineer starter assignment {n} of 10.",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    _init_db_if_missing()


@app.get("/api/health", summary="Health check", tags=["health"])
def health() -> dict[str, str]:
    """Return OK if the backend is up. Used by tests and smoke checks."""
    return {{"status": "ok"}}
'''

BACKEND_TEST = '''"""Smoke test for the backend skeleton."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
'''

BACKEND_README = """# Backend — {title}

FastAPI + SQLite, managed by [uv](https://docs.astral.sh/uv/).

## Run

```
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

OpenAPI docs: http://localhost:8000/docs

## Test

```
uv run pytest
```

## What's here

- `app/main.py` — FastAPI entrypoint with `GET /api/health`.
- `schema.sql` — your database schema (empty; you fill this in Phase 3).
- `seed.sql` — your seed data (empty; you fill this in Phase 3).
- `tests/` — pytest tests; the skeleton ships with a single health-check test.

## What to add

Follow the starter workflow. In short:

1. Phase 2 — design the data model in `../docs/02-data-model.md`.
2. Phase 3 — fill `schema.sql` and `seed.sql` from that model.
3. Phase 4 — add Pydantic models and routes under `app/`. All routes prefixed `/api`.

Do not edit the schema outside of `schema.sql`. The source of truth is the model document one step up.
"""

BACKEND_SCHEMA_SQL = """-- Phase 3 — fill this in based on docs/02-data-model.md.
-- The backend applies this file on startup if app.db does not exist.
-- Add every entity from the model, with primary keys, foreign keys, uniqueness
-- constraints, and CHECK constraints as the model specifies.
"""

BACKEND_SEED_SQL = """-- Phase 3 — fill this in after schema.sql is complete.
-- Aim for 3–5 rows per table covering the happy path and at least one edge
-- case per user story. Use concrete domain vocabulary, not placeholder names.
"""

BACKEND_GITIGNORE = """app.db
__pycache__/
*.pyc
.venv/
.uv/
"""

# ---------------------------------------------------------------------------
# Frontend scaffold (static across assignments)
# ---------------------------------------------------------------------------

FRONTEND_PACKAGE_JSON = """{{
  "name": "{slug}-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest"
  }},
  "dependencies": {{
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  }},
  "devDependencies": {{
    "@testing-library/jest-dom": "^6.5.0",
    "@testing-library/react": "^16.0.1",
    "@types/react": "^18.3.11",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.2",
    "jsdom": "^25.0.1",
    "typescript": "^5.6.2",
    "vite": "^5.4.8",
    "vitest": "^2.1.2"
  }}
}}
"""

FRONTEND_VITE_CONFIG = """import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/setupTests.ts"],
  },
});
"""

FRONTEND_TSCONFIG = """{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitAny": true,
    "skipLibCheck": true,
    "allowImportingTsExtensions": false,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "isolatedModules": true,
    "resolveJsonModule": true,
    "types": ["vite/client", "vitest/globals", "@testing-library/jest-dom"]
  },
  "include": ["src"]
}
"""

FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""

FRONTEND_MAIN_TSX = """import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./App.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""

FRONTEND_APP_TSX = '''import {{ useEffect, useState }} from "react";

type Health = {{ status: string }};

export default function App() {{
  const [health, setHealth] = useState<Health | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {{
    fetch("/api/health")
      .then(r => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then(setHealth)
      .catch(e => setErr(String(e)));
  }}, []);

  return (
    <main className="shell">
      <header>
        <p className="kicker">CE Starter · Assignment {n}</p>
        <h1>{title}</h1>
        <p className="pitch">{pitch}</p>
      </header>
      <section className="status">
        <h2>Backend health</h2>
        {{err && <p className="err">Error: {{err}}</p>}}
        {{!err && !health && <p>Checking…</p>}}
        {{health && <p className="ok">{{health.status}}</p>}}
      </section>
      <section className="next">
        <h2>Next</h2>
        <p>
          This is the scaffold. Follow the starter workflow, phase by phase. Open <code>index.html</code> at the repo root for the assignment brief with copyable prompts.
        </p>
      </section>
    </main>
  );
}}
'''

FRONTEND_APP_CSS = """:root {
  --bg: #f7f3ea;
  --ink: #1a1816;
  --ink-muted: #5e5852;
  --accent: #115362;
  --accent-soft: #dfeaed;
  --rule: #e3ddd0;
  --ok: #2f7d56;
  --err: #b4524c;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  min-height: 100vh;
}

.shell {
  max-width: 720px;
  margin: 0 auto;
  padding: 72px 28px 96px;
}

.kicker {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  margin: 0 0 12px;
}

h1 {
  font-size: 40px;
  line-height: 1.1;
  margin: 0 0 14px;
  letter-spacing: -0.02em;
  font-family: "Fraunces", Georgia, serif;
  font-weight: 500;
}

h2 {
  font-family: "Fraunces", Georgia, serif;
  font-weight: 500;
  font-size: 20px;
  margin: 0 0 10px;
  letter-spacing: -0.01em;
}

.pitch {
  font-size: 18px;
  color: var(--ink-muted);
  margin: 0 0 40px;
  line-height: 1.55;
}

section {
  margin-top: 32px;
  padding: 24px 26px;
  background: #fff;
  border: 1px solid var(--rule);
  border-radius: 14px;
}

.ok {
  color: var(--ok);
  font-weight: 600;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  margin: 0;
}

.err {
  color: var(--err);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  margin: 0;
}

code {
  background: var(--accent-soft);
  color: var(--accent);
  padding: 0.06em 0.4em;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.92em;
}
"""

FRONTEND_SETUP_TESTS = '''import "@testing-library/jest-dom";
'''

FRONTEND_APP_TEST = '''import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "./App";

describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the title", () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok" }),
      }),
    );
    render(<App />);
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
  });
});
'''

FRONTEND_VITE_ENV = """/// <reference types="vite/client" />
"""

FRONTEND_CLIENT_TS = """/*
 * Typed API client — fill this in during Phase 5.
 *
 * The recommended flow:
 *   1. Make sure the backend is running at http://localhost:8000.
 *   2. Ask your agent: "Generate TypeScript types for every request and
 *      response in the backend OpenAPI spec at /openapi.json. Put them in
 *      ./types.ts. Then populate this file with one function per endpoint
 *      that uses those types."
 *   3. No any types. If the agent reaches for any, push back.
 */

export {};
"""

FRONTEND_TYPES_TS = """/*
 * Placeholder — generated from the OpenAPI spec in Phase 5.
 * Do not hand-author types here; regenerate from /openapi.json instead.
 */

export {};
"""

FRONTEND_GITIGNORE = """node_modules
dist
coverage
.env.local
.DS_Store
"""

FRONTEND_README = """# Frontend — {title}

Vite + React + TypeScript.

## Run

```
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api/*` to the backend at `:8000`.

## Test

```
npm test
```

## What's here

- `src/App.tsx` — skeleton shell that checks `/api/health` on mount.
- `src/api/client.ts`, `src/api/types.ts` — placeholders. Generate types from the OpenAPI spec in Phase 5.
- `vite.config.ts` — the `/api` proxy.

## What to add

Follow the starter workflow. In short:

1. Phase 5 — generate `src/api/types.ts` from the backend OpenAPI spec, write `client.ts` against those types, then implement one screen per user story.
"""

# ---------------------------------------------------------------------------
# Root files
# ---------------------------------------------------------------------------

ROOT_GITIGNORE = """# python
__pycache__/
*.pyc
.venv/
.uv/

# node
node_modules/
dist/
coverage/

# SQLite DB (created on first run)
backend/app.db

# editor & OS
.DS_Store
.vscode/
.idea/
"""

DOCS_GITKEEP = """# Artifacts from the workflow phases land here:
# 01-brief.md, 02-data-model.md, 06-retro.md, demo.mp4, etc.
"""


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_one(a: dict) -> Path:
    dirname = f"{a['n']}-{a['slug']}"
    d = OUT / dirname

    # Root files
    write(d / "index.html", render_index(a))
    write(d / "README.md", render_readme(a))
    write(d / ".gitignore", ROOT_GITIGNORE)
    shutil.copyfile(STYLES_SRC, d / "styles.css")

    # docs placeholder
    write(d / "docs" / ".gitkeep", DOCS_GITKEEP)

    # backend scaffold
    write(d / "backend" / "pyproject.toml", BACKEND_PYPROJECT.format(slug=a["slug"], title=a["title"]))
    write(d / "backend" / ".python-version", BACKEND_PYTHON_VERSION)
    write(d / "backend" / "README.md", BACKEND_README.format(title=a["title"]))
    write(d / "backend" / "schema.sql", BACKEND_SCHEMA_SQL)
    write(d / "backend" / "seed.sql", BACKEND_SEED_SQL)
    write(d / "backend" / ".gitignore", BACKEND_GITIGNORE)
    write(d / "backend" / "app" / "__init__.py", "")
    write(
        d / "backend" / "app" / "main.py",
        BACKEND_MAIN.format(title=a["title"].replace('"', r'\"'), n=a["n"]),
    )
    write(d / "backend" / "tests" / "__init__.py", "")
    write(d / "backend" / "tests" / "test_health.py", BACKEND_TEST)

    # frontend scaffold
    write(d / "frontend" / "package.json", FRONTEND_PACKAGE_JSON.format(slug=a["slug"]))
    write(d / "frontend" / "vite.config.ts", FRONTEND_VITE_CONFIG)
    write(d / "frontend" / "tsconfig.json", FRONTEND_TSCONFIG)
    write(d / "frontend" / "index.html", FRONTEND_HTML.format(title=esc(a["title"])))
    write(d / "frontend" / "README.md", FRONTEND_README.format(title=a["title"]))
    write(d / "frontend" / ".gitignore", FRONTEND_GITIGNORE)
    write(d / "frontend" / "src" / "main.tsx", FRONTEND_MAIN_TSX)
    write(
        d / "frontend" / "src" / "App.tsx",
        FRONTEND_APP_TSX.format(
            n=a["n"],
            title=esc(a["title"]),
            pitch=esc(a["pitch"]),
        ),
    )
    write(d / "frontend" / "src" / "App.css", FRONTEND_APP_CSS)
    write(d / "frontend" / "src" / "App.test.tsx", FRONTEND_APP_TEST)
    write(d / "frontend" / "src" / "setupTests.ts", FRONTEND_SETUP_TESTS)
    write(d / "frontend" / "src" / "vite-env.d.ts", FRONTEND_VITE_ENV)
    write(d / "frontend" / "src" / "api" / "client.ts", FRONTEND_CLIENT_TS)
    write(d / "frontend" / "src" / "api" / "types.ts", FRONTEND_TYPES_TS)

    return d


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for a in ASSIGNMENTS:
        d = build_one(a)
        print(f"  built {d.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
