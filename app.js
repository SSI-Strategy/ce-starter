/* ============================================================
   Capability Engineer Starter Program — site behaviour
   Vanilla JS. No deps. Drop into GitHub Pages as-is.
   ============================================================ */

(() => {
  "use strict";

  /* ---------- data: workflow phases ---------- */

  const phases = [
    {
      title: "Brainstorm the use case",
      concept: "Sharpen the idea with an LLM until you can name the user, three stories, the nouns, and the verbs.",
      artifact: "docs/01-brief.md",
      verify: "Read the brief out loud. Any vague sentence gets sent back.",
      pitfall: "Jumping to features before the user story is nailed."
    },
    {
      title: "Design the data model",
      concept: "Every screen, API call, and query descends from this. Getting it right before code is the single highest-leverage decision.",
      artifact: "docs/02-data-model.md",
      verify: "Walk through each user story. Can every state be represented?",
      pitfall: "Modelling what the UI will show, instead of what the domain is."
    },
    {
      title: "Build the database",
      concept: "Turning the model into a real SQLite schema exposes every ambiguity. Constraints fail loudly.",
      artifact: "backend/schema.sql + app.db",
      verify: "Open sqlite3 and run .tables, .schema, SELECT.",
      pitfall: "Silent 'improvements' from the agent that drift from the model."
    },
    {
      title: "Design and build the API",
      concept: "Design first as a markdown table of endpoints. Build second. The OpenAPI spec is the deliverable — the Python is scaffolding.",
      artifact: "http://localhost:8000/docs",
      verify: "Complete every user story using only the 'Try it out' UI.",
      pitfall: "CRUD for every table when only a few operations serve a story."
    },
    {
      title: "Build the frontend",
      concept: "Generate TypeScript types from OpenAPI. The API contract is already signed — the frontend's job is narrow.",
      artifact: "http://localhost:5173",
      verify: "Complete each user story end to end with a human watching.",
      pitfall: "Ignoring the generated types and falling back to 'any'."
    },
    {
      title: "Integrate and verify",
      concept: "The application is done when a stranger can use it to accomplish the user stories. Anything else is scaffolding.",
      artifact: "A 2–3 minute screen recording + docs/06-retro.md",
      verify: "Someone else on the team runs it fresh and reproduces your demo.",
      pitfall: "Treating the retro as a formality. It's the evidence of learning."
    }
  ];

  /* ---------- data: prompt library ---------- */

  const prompts = [
    {
      phase: "Phase 1",
      title: "Brainstorm opener",
      body: `I want to build a small local web application. Help me sharpen the idea by asking me questions. I will answer. After five rounds of questions, summarise what we have agreed on as a one-page brief covering: the user, the three core user stories, the key nouns (things the app tracks), and the key verbs (things the user can do).`
    },
    {
      phase: "Phase 2",
      title: "Data-model request",
      body: `Read docs/01-brief.md. Based on the nouns listed there, propose a data model for a SQLite database. For each entity, give me: its fields, each field's type and whether it is required, the primary key, any foreign keys, and any uniqueness or check constraints. Show the model as a markdown document, not SQL. Explain every foreign key in one sentence. Then list any ambiguities you had to resolve and why.`
    },
    {
      phase: "Phase 3",
      title: "Schema + seed generation",
      body: `Using docs/02-data-model.md as the source of truth, generate backend/schema.sql for SQLite. Include every primary key, foreign key, uniqueness constraint, and check constraint from the model. Add created_at and updated_at where the model specifies them. Then generate backend/seed.sql with 3-5 rows per table covering the happy path and at least one edge case per user story. Finally, wire the schema to apply automatically on backend startup if the database file does not exist.`
    },
    {
      phase: "Phase 4a",
      title: "API design (no code yet)",
      body: `Based on the verbs in docs/01-brief.md and the entities in docs/02-data-model.md, propose a REST API. For each endpoint, give me: the method, the path, the request body shape, the response shape, and which user story it serves. Do not write code yet. Return a markdown table.`
    },
    {
      phase: "Phase 4b",
      title: "API implementation",
      body: `Implement these endpoints in FastAPI under backend/app/. Use Pydantic models for every request and response. Use the stdlib sqlite3 module. All routes must be prefixed with /api. Add a GET /api/health that returns {"status": "ok"}. Make sure every endpoint appears in the OpenAPI docs at /docs with a clear summary and a populated example.`
    },
    {
      phase: "Phase 5a",
      title: "Typed API client",
      body: `Generate TypeScript types for every request and response in the backend OpenAPI spec at http://localhost:8000/openapi.json. Put them in frontend/src/api/types.ts. Then write a thin client.ts in the same directory with one function per endpoint. Every function must use the generated types — no any.`
    },
    {
      phase: "Phase 5b",
      title: "Screen briefs",
      body: `For each of the three user stories in docs/01-brief.md, propose a screen: what the user sees, what they can do, what state changes on the screen after each action. Return a short markdown brief per screen. Do not write components yet.`
    },
    {
      phase: "Phase 5c",
      title: "Screen implementation",
      body: `Implement the screens from the brief using React and plain CSS. Use the typed client for every API call. Keep each screen to one route. Show loading and error states for every request. Add one Vitest test per screen that renders it with a mocked client.`
    }
  ];

  /* ---------- data: assignments ---------- */

  const SLUGS = {
    "01": "cro-time-invoice-tracker",
    "02": "vendor-bid-comparison",
    "03": "protocol-deviation-log",
    "04": "site-feasibility-tracker",
    "05": "clinical-query-tracker",
    "06": "habit-tracker",
    "07": "standup-blocker-log",
    "08": "expense-splitter",
    "09": "reading-list",
    "10": "agent-skill-library"
  };

  const assignments = [
    {
      n: "01",
      category: "clinical",
      title: "CRO Time & Invoice Tracker",
      pitch: "Log billable hours against studies. See month-to-date spend by person. Compare against a simple monthly budget.",
      user: "A project manager at a small CRO who owns monthly burn for one or more studies.",
      concept: "Aggregation with GROUP BY and a date range, driven from the UI via query parameters.",
      lockDown: [
        "What is the unit of billable work — a day's entry, an hour's entry, or a whole invoice line?",
        "Is a person's billing rate fixed per project, per role, or per entry?",
        "What counts as 'budget' — a dollar cap per month, per project, per person, or per account code?"
      ],
      guardrails: "No PDF parsing. No multi-currency. No multi-user auth. No approval workflow on time entries.",
      anchor: "Anchored on a representative CRO invoice and monthly time-tracking report — your reviewer will share real examples."
    },
    {
      n: "02",
      category: "clinical",
      title: "Competitive Vendor Bid Comparison",
      pitch: "Enter line-item bids from multiple vendors for the same scope of work. View side-by-side with totals and per-line deltas.",
      user: "A sourcing lead evaluating two or three CRO proposals for the same study.",
      concept: "Pivoting normalised rows into a comparison matrix at the API boundary.",
      lockDown: [
        "Is 'scope' a fixed list defined before bids come in, or does each vendor define their own?",
        "What does a line item consist of — description, quantity, unit, unit price? All four?",
        "What is shown as the comparison — lowest bid per line, deltas from cheapest, or deltas from a baseline?"
      ],
      guardrails: "No document upload. No vendor-managed accounts. No currency conversion."
    },
    {
      n: "03",
      category: "clinical",
      title: "Protocol Deviation Log",
      pitch: "Record protocol deviations observed at study sites, categorise them, and track each one from open to resolved.",
      user: "A clinical monitor responsible for one study across several sites.",
      concept: "Workflow status as a first-class domain concept — CHECK constraints, allowed transitions, and a derived 'overdue' view.",
      lockDown: [
        "Fixed enum (Major / Minor / Other) or free-text taxonomy? Pick the enum.",
        "What states — Open, Under review, Resolved, Cancelled? Which transitions are allowed?",
        "What does 'overdue' mean — days since open without resolution?"
      ],
      guardrails: "No audit log / history table. No file attachments. No site-user login."
    },
    {
      n: "04",
      category: "clinical",
      title: "Study Site Feasibility Tracker",
      pitch: "Track candidate sites for a new study. Record each site's survey answers. Rank them.",
      user: "A feasibility lead selecting sites for a new trial.",
      concept: "Modelling a question-answer relationship — two tables vs a JSON column, each with stated trade-offs.",
      lockDown: [
        "Same survey questions across all studies, or study-specific?",
        "How is a site ranked — sum of numeric answers, a separate score field, or sorted by one attribute?",
        "Does this app need both sites (organisations) and investigators (people)?"
      ],
      guardrails: "No email-out to sites. No survey versioning. No branching logic inside a survey."
    },
    {
      n: "05",
      category: "clinical",
      title: "Clinical Query Tracker",
      pitch: "Track data-management queries against case-report-form data: who raised it, which field, when it was answered, how old it is.",
      user: "A clinical data manager watching query aging across a single study.",
      concept: "Time-derived fields — computed in the API from stored timestamps, never stored as mutable columns.",
      lockDown: [
        "What is a query attached to — a subject, a visit, a specific field?",
        "Who raises queries (DM), who answers them (site)? Only one state changes the clock.",
        "What's the SLA — days to respond? Computed server-side or client-side?"
      ],
      guardrails: "No eCRF integration. No user roles beyond one DM. No query threading."
    },
    {
      n: "06",
      category: "general",
      title: "Habit Tracker",
      pitch: "Define recurring habits. Check them off daily. See streaks and a weekly completion rate.",
      user: "You.",
      concept: "Computed-on-read fields (streak length, completion rate) vs stored fields — and how much logic belongs in SQL vs Python.",
      lockDown: [
        "Is a habit just a name, or does it carry a target (e.g., 3 times per week)?",
        "Is a check-in a boolean per day, or can it carry a count or a note?",
        "What is a streak — consecutive days, or consecutive expected days?"
      ],
      guardrails: "No reminders or scheduling. No multi-user. No calendar integration."
    },
    {
      n: "07",
      category: "general",
      title: "Team Standup & Blocker Log",
      pitch: "Post a short daily update and list current blockers. Screen that shows all open blockers across the team, sorted by age.",
      user: "A team lead running async standups for four to six people.",
      concept: "A uniqueness constraint UNIQUE(user_id, date) as a real design choice — and what the API does when the constraint fires.",
      lockDown: [
        "Is a blocker attached to a standup entry, or independent?",
        "Who resolves a blocker — the person who raised it, anyone, the team lead?",
        "Does the app enforce one standup per person per day, or allow many?"
      ],
      guardrails: "No login. No Slack/email notifications. No historical analytics beyond blocker age."
    },
    {
      n: "08",
      category: "general",
      title: "Expense Splitter (lite)",
      pitch: "A small group tracks shared expenses — who paid, how much, for whom. The app computes who owes whom.",
      user: "A four-person apartment or a trip group.",
      concept: "Derived balances — never store 'what Alice owes Bob'. Always compute from the expense log. Single source of truth.",
      lockDown: [
        "Is every expense split equally, or can each specify a subset of members?",
        "Does 'who owes whom' settle through a central pool, or as direct pairs?",
        "What does 'settle' mean — a record zeroing balances, or just a UI filter?"
      ],
      guardrails: "No OAuth. No currencies. Max ten members per group (CHECK constraint)."
    },
    {
      n: "09",
      category: "general",
      title: "Reading List",
      pitch: "Books across want-to-read, reading, finished. Rating and a short note. A pages-per-week report.",
      user: "You, again.",
      concept: "Normalisation as a reversible decision — produce two candidate data models (author-as-string vs Author-as-table), then pick.",
      lockDown: [
        "Is an author a separate entity, or just a text field on the book?",
        "How is 'pages per week' derived — from a session log, or start/end dates?",
        "What does it mean to move a book from 'reading' back to 'want to read'?"
      ],
      guardrails: "No cover-image upload. No ISBN lookup against external APIs. No recommendations engine."
    },
    {
      n: "10",
      category: "general",
      title: "Agent Skill Library",
      pitch: "A catalogue of agent skills with search and filtering. A companion tool for the work this team is actually doing.",
      user: "A capability engineer who wants to remember and re-find skills they or their team have written.",
      concept: "Many-to-many (Skill ↔ Tag) and the API shape that makes filtering-by-multiple-tags feel natural.",
      lockDown: [
        "What fields does a skill carry? Which are searchable vs merely displayed?",
        "Are tags free-form strings or a controlled vocabulary?",
        "What does 'search' mean — substring, tag filter, or both combined?"
      ],
      guardrails: "No markdown renderer in the UI — raw text. No skill versioning. No import from external file formats."
    }
  ];

  /* ---------- render: phases ---------- */

  const phaseListEl = document.getElementById("phaseList");
  if (phaseListEl) {
    phaseListEl.innerHTML = phases.map(p => `
      <li class="phase">
        <div class="phase-marker" aria-hidden="true"></div>
        <div class="phase-body">
          <h3>${p.title}</h3>
          <p class="phase-concept">${p.concept}</p>
          <dl class="phase-meta">
            <div>
              <dt>Artifact</dt>
              <dd><code>${p.artifact}</code></dd>
            </div>
            <div>
              <dt>Verify</dt>
              <dd>${p.verify}</dd>
            </div>
            <div>
              <dt>Common pitfall</dt>
              <dd>${p.pitfall}</dd>
            </div>
          </dl>
        </div>
      </li>
    `).join("");
  }

  /* ---------- render: prompts ---------- */

  const promptListEl = document.getElementById("promptList");
  if (promptListEl) {
    promptListEl.innerHTML = prompts.map(pr => `
      <article class="prompt-card">
        <div class="prompt-head">
          <h3 class="prompt-title">${pr.title}</h3>
          <span class="prompt-phase">${pr.phase}</span>
        </div>
        <div class="prompt-body">
          <button class="copy-btn" type="button" data-copy>Copy</button>
          <span class="prompt-text">${escapeHTML(pr.body)}</span>
        </div>
      </article>
    `).join("");

    promptListEl.addEventListener("click", async (e) => {
      const btn = e.target.closest("[data-copy]");
      if (!btn) return;
      const text = btn.parentElement.querySelector(".prompt-text").textContent;
      const ok = await copyToClipboard(text);
      if (ok) {
        btn.textContent = "Copied";
        btn.classList.add("is-copied");
        setTimeout(() => {
          btn.textContent = "Copy";
          btn.classList.remove("is-copied");
        }, 1600);
      }
    });
  }

  /* ---------- render: assignments ---------- */

  const gridEl = document.getElementById("assignmentGrid");
  if (gridEl) {
    gridEl.innerHTML = assignments.map(a => `
      <button type="button" class="assignment" data-cat="${a.category}" aria-expanded="false">
        <div class="assignment-head">
          <span class="assignment-num">${a.n}</span>
          <span class="assignment-cat" data-cat="${a.category}">${a.category === "clinical" ? "Clinical ops" : "General"}</span>
        </div>
        <h3 class="assignment-title">${a.title}</h3>
        <p class="assignment-pitch">${a.pitch}</p>
        <div class="assignment-foot">
          <span><span class="concept">Teaches:</span> ${truncate(a.concept, 52)}</span>
          <span class="expand-hint" aria-hidden="true"></span>
        </div>
        <div class="assignment-details">
          <div class="details-block">
            <p class="details-label">Primary user</p>
            <p class="details-text">${a.user}</p>
          </div>
          ${a.anchor ? `
          <div class="details-block">
            <p class="details-label">Anchor</p>
            <p class="details-text">${a.anchor}</p>
          </div>` : ""}
          <div class="details-block">
            <p class="details-label">What the brainstorm must lock down</p>
            <ul class="details-list">
              ${a.lockDown.map(q => `<li>${q}</li>`).join("")}
            </ul>
          </div>
          <div class="details-block">
            <p class="details-label">Concept this teaches</p>
            <p class="details-text">${a.concept}</p>
          </div>
          <div class="details-block">
            <p class="details-label">Guardrails</p>
            <p class="details-text">${a.guardrails}</p>
          </div>
          <div class="details-block details-cta">
            <a class="details-link" href="assignments/${a.n}-${SLUGS[a.n]}/">Open assignment page →</a>
          </div>
        </div>
      </button>
    `).join("");

    gridEl.addEventListener("click", (e) => {
      if (e.target.closest(".details-link")) return;
      const card = e.target.closest(".assignment");
      if (!card) return;
      const open = card.classList.toggle("is-open");
      card.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- filter pills ---------- */

  const pills = document.querySelectorAll(".filter-pill");
  pills.forEach(pill => {
    pill.addEventListener("click", () => {
      pills.forEach(p => {
        p.classList.remove("is-active");
        p.setAttribute("aria-selected", "false");
      });
      pill.classList.add("is-active");
      pill.setAttribute("aria-selected", "true");
      const filter = pill.dataset.filter;
      document.querySelectorAll(".assignment").forEach(card => {
        const show = filter === "all" || card.dataset.cat === filter;
        card.classList.toggle("is-hidden", !show);
        if (!show) {
          card.classList.remove("is-open");
          card.setAttribute("aria-expanded", "false");
        }
      });
    });
  });

  /* ---------- nav: sticky shadow + active section ---------- */

  const nav = document.getElementById("siteNav");
  const navLinks = document.querySelectorAll(".nav-links a");
  const navTargets = [...navLinks].map(a => {
    const id = a.getAttribute("href").slice(1);
    return { link: a, el: document.getElementById(id) };
  }).filter(t => t.el);

  const onScroll = () => {
    if (window.scrollY > 8) nav.classList.add("is-stuck");
    else nav.classList.remove("is-stuck");

    const y = window.scrollY + 120;
    let active = navTargets[0];
    for (const t of navTargets) {
      if (t.el.offsetTop <= y) active = t;
    }
    navLinks.forEach(l => l.classList.remove("is-active"));
    if (active) active.link.classList.add("is-active");
  };

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- utilities ---------- */

  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); } catch { /* no-op */ }
      document.body.removeChild(ta);
      return true;
    }
  }

  function escapeHTML(s) {
    return s.replace(/[&<>"']/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[c]);
  }

  function truncate(s, n) {
    return s.length > n ? s.slice(0, n).trimEnd() + "…" : s;
  }
})();
