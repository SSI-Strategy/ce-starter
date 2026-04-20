# Assignment Catalogue

Ten starter assignments vetted against `STACK.md` and `WORKFLOW.md`. Each is a *seed* for phase 1 of the workflow — the capability engineer takes the seed into a brainstorm with an LLM and produces `docs/01-brief.md` from it. The seed is deliberately underspecified: the CE's job is to sharpen it.

## How the list was curated

The raw list of ideas included external-data reconciliation, SDTM mapping, TLF generation, central monitoring with outlier detection, and live clinicaltrials.gov feasibility. Those are good ideas and worth building later — they are not starter assignments. Each would blow up one or more of the criteria below.

### Starter criteria each assignment must meet

1. **Scope fits one working day.** No more than four or five entities, three user stories, three to five screens.
2. **No specialist domain knowledge required to assess correctness.** A reviewer who has never worked on a clinical trial should still be able to tell if the submitted app satisfies the brief.
3. **No external APIs at runtime.** Any real-world data is seeded at build time from a static snapshot. No OAuth, no keys, no network.
4. **No statistics beyond aggregation (`SUM`, `COUNT`, `AVG`, `GROUP BY`).** No outlier detection, no forecasting, no ML.
5. **No file parsing surface.** No PDF ingestion, no Excel upload, no CSV import in the UI. Seeds go into `backend/seed.sql`.
6. **At least one one-to-many relationship and one aggregation report.** This is the minimum needed to exercise the full stack meaningfully.
7. **Teaches one identifiable concept beyond CRUD.** Stated explicitly per assignment.

### Difficulty calibration

Every assignment on this list is sized to land in the same envelope:

- **Entities:** 4 ± 1.
- **User stories:** exactly 3.
- **Screens:** 3 ± 1.
- **One aggregation view** (the "report" screen).
- **One state transition** somewhere (status field with rules, or a derived status).

If a brainstorm produces something notably bigger than this envelope, the CE should cut — not expand the stack.

### Mix

Five are drawn from the team's clinical-operations domain so colleagues with that background have a relatable frame. Five are general-purpose so engineers without that background can pick something they understand as a user. All ten teach the same stack concepts.

---

## Clinical operations assignments

### 1. CRO Time & Invoice Tracker

**Pitch.** A local tool where a CRO project manager logs billable hours against studies, sees month-to-date spend by person, and compares it to a simple monthly budget.

**Seed.** Anchored on a representative CRO invoice and monthly time-tracking report (your reviewer will share real examples). Open those two before brainstorming so the domain vocabulary (study, project, account code, role, rate) is concrete.

**Primary user.** A project manager at a small CRO who owns monthly burn for one or more studies.

**What the brainstorm should lock down.**

- What is the unit of billable work — a day's entry, an hour's entry, or a whole invoice line? (Pick one.)
- Is a person's billing rate fixed per project, or per role, or per entry?
- What counts as "budget" — a dollar cap per month, per project, per person, or per account code?

**Concept this assignment teaches.** Aggregation with `GROUP BY` and a date range, driven from the UI via query parameters. The report screen is a pivot the CE has to design before the agent can build it.

**Guardrails.** No PDF parsing. No multi-currency. No per-user auth — single local user. No approval workflow on time entries.

---

### 2. Competitive Vendor Bid Comparison

**Pitch.** A tool to enter line-item bids from multiple vendors for the same scope of work and view them side-by-side with totals and per-line deltas.

**Primary user.** A sourcing lead evaluating two or three CRO proposals for the same study.

**What the brainstorm should lock down.**

- Is "scope" a fixed list of line items defined before bids come in, or does each vendor define their own? (Strongly prefer fixed — otherwise comparison is ill-defined.)
- What does a line item consist of — description, quantity, unit, unit price? All four?
- What is shown as the "comparison" — lowest bid per line, deltas from the cheapest, or deltas from a baseline?

**Concept this assignment teaches.** Pivoting normalised rows into a comparison matrix at the API boundary, rather than in the frontend. The endpoint that returns the comparison is the most interesting design decision in the assignment.

**Guardrails.** No document upload. No vendor-managed accounts — the sourcing lead enters bids on the vendor's behalf. No currency conversion.

---

### 3. Protocol Deviation Log

**Pitch.** A log where monitors record protocol deviations observed at study sites, categorise them, and track each one from open to resolved.

**Primary user.** A clinical monitor responsible for one study across several sites.

**What the brainstorm should lock down.**

- What categorises a deviation — a fixed enum (Major / Minor / Other) or a free-text taxonomy? (Pick a fixed enum for this size of project.)
- What states does a deviation move through — Open, Under review, Resolved, Cancelled? Which transitions are allowed?
- What does "overdue" mean — days since open without resolution?

**Concept this assignment teaches.** Workflow status as a first-class domain concept: a `status` column with a `CHECK` constraint, allowed transitions enforced at the API, and an "overdue" view computed from `julianday('now') - julianday(opened_at)`.

**Guardrails.** No audit log / history table — if the CE wants that, it's a second assignment. No file attachments. No site-user login.

---

### 4. Study Site Feasibility Tracker

**Pitch.** A tool for a feasibility lead to track candidate sites for a new study, record each site's survey answers, and rank them.

**Primary user.** A feasibility lead selecting sites for a new trial.

**What the brainstorm should lock down.**

- Are the survey questions the same across all studies, or study-specific? (Either is fine, but pick one — this is the central modelling decision.)
- How is a site "ranked" — sum of numeric answers, a separate score field, or just sorted by one key attribute?
- What's the difference between a site (an organisation) and an investigator (a person)? Does this app need both?

**Concept this assignment teaches.** Modelling a question-answer relationship — either as two tables (Question, Response) or as a JSON column, each with trade-offs the CE has to articulate. This is the first time they'll meet a real modelling fork.

**Guardrails.** No email-out to sites. No versioning of surveys. No branching logic inside a survey.

---

### 5. Clinical Query Tracker

**Pitch.** A lightweight tracker for data-management queries raised against case-report-form data: who raised the query, which subject and field it's against, when it was answered, and how long it aged.

**Primary user.** A clinical data manager watching query aging across a single study.

**What the brainstorm should lock down.**

- What is a "query" attached to — a subject, a visit, a specific field? (Pick the smallest unit you can still explain.)
- Who raises queries (DM) and who answers them (site)? Both are represented, but only one state changes the clock.
- What's the SLA — days to respond? Is "overdue" computed server-side or client-side?

**Concept this assignment teaches.** Time-derived fields — `age_days`, `is_overdue` — computed in the API from stored timestamps, rather than stored as mutable columns. Teaches the difference between *data* and *derived views over data*.

**Guardrails.** No eCRF integration. No user roles beyond one logical DM. No query threading — each query has one answer.

---

## General-purpose assignments

### 6. Habit Tracker

**Pitch.** A personal tool to define recurring habits, check them off daily, and see streaks and a weekly completion rate.

**Primary user.** The CE themselves.

**What the brainstorm should lock down.**

- What is a habit — just a name, or does it carry a target (e.g., "3 times per week")?
- What is a check-in — just a boolean per day, or can it carry a count or a note?
- What is a "streak" — consecutive days, or consecutive expected days?

**Concept this assignment teaches.** Computed-on-read fields (streak length, completion rate) versus stored fields, and how much of that logic belongs in SQL versus Python.

**Guardrails.** No reminders or scheduling. No multi-user. No calendar integration.

---

### 7. Team Standup & Blocker Log

**Pitch.** A tool a small team uses to post a short daily update and list their current blockers, and a screen that shows all open blockers across the team, sorted by age.

**Primary user.** A team lead running async standups for four to six people.

**What the brainstorm should lock down.**

- Is a blocker attached to a standup entry, or independent? (If independent, standups are almost vestigial.)
- Who resolves a blocker — the person who raised it, anyone, the team lead?
- Does the app enforce one standup per person per day, or allow many?

**Concept this assignment teaches.** A uniqueness constraint (`UNIQUE(user_id, date)`) as a real design choice with behavioural consequences — and what the API does when the constraint fires.

**Guardrails.** No login. No Slack/email notifications. No historical analytics beyond "how old is this blocker."

---

### 8. Expense Splitter (lite)

**Pitch.** A small group tracks shared expenses (who paid, how much, who the expense is for) and the app computes who owes whom.

**Primary user.** A four-person apartment or a trip group.

**What the brainstorm should lock down.**

- Is every expense split equally among all members, or can each expense specify which subset it applies to?
- Does "who owes whom" settle through a central pool, or as direct pairs? (Direct pairs is simpler but produces n² lines.)
- What does "settle" mean — a record that zeroes balances up to that point, or just a UI filter?

**Concept this assignment teaches.** Derived balances — never store "what Alice owes Bob," always compute it from the expense log. The frontend displays a view the backend computed; the backend computed it from the log. This is a clean example of single-source-of-truth thinking.

**Guardrails.** No OAuth with any group-chat tool. No currencies. Max ten members in a group (a `CHECK` constraint).

---

### 9. Reading List

**Pitch.** A personal tracker for books: want-to-read, reading, finished; with rating and a short note per book, and a page-count-per-week report.

**Primary user.** The CE themselves, again.

**What the brainstorm should lock down.**

- Is an author a separate entity (normalised) or just a text field on the book?
- How is "pages read per week" derived — from a reading-session log, or just from start and end dates on a book?
- What does it mean to move a book from "reading" back to "want to read"?

**Concept this assignment teaches.** Normalisation as a reversible decision — the brainstorm should produce *two* candidate data models (author-as-string vs Author-as-table) with stated trade-offs, then pick one.

**Guardrails.** No book-cover image upload. No ISBN lookups against external APIs. No recommendations engine.

---

### 10. Agent Skill Library

**Pitch.** A catalogue of agent "skills" (name, description, tags, when-to-trigger, example prompts) with search and filtering. A companion tool for the work this team is actually doing.

**Primary user.** A CE who wants to remember and re-find skills they or their team have written.

**What the brainstorm should lock down.**

- What fields does a skill carry, and which are searchable versus merely displayed?
- Are tags free-form strings or a controlled vocabulary?
- What does "search" mean — substring match, tag filter, or both combined?

**Concept this assignment teaches.** Many-to-many relationships (Skill ↔ Tag) and the API shape that makes filtering-by-multiple-tags feel natural. Also a small, honest lesson in SQLite's `LIKE` for search before reaching for anything fancier.

**Guardrails.** No markdown renderer in the UI — show the raw text. No versioning of skills. No import from any external file format.

---

## Explicitly excluded ideas and why

These came up in the team brainstorm and are deliberately not on the list. They are good candidates for a second or third assignment.

| Idea                                         | Why it's not a starter                                                                                    |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| External data reconciliation (SAE, labs, PK) | Requires ingesting and matching heterogeneous feeds. Integration surface is the entire product.          |
| Clinical data quality checks                 | The rules library *is* the product. Without one, there's nothing to build; with one, it's not a starter. |
| Raw data to SDTM mapping                     | Requires specialist knowledge to even evaluate correctness. Fails criterion 2.                            |
| Central monitoring / outlier detection       | Needs statistics beyond aggregation. Fails criterion 4.                                                   |
| TLF generation                               | Output rendering (PDF/Word) dwarfs the data model. Fails criterion 1 and criterion 5.                     |
| Live clinicaltrials.gov feasibility          | Needs a real external API, rate limits, and caching semantics. Fails criterion 3.                         |
| Benchmarking across registries               | Same reason as above, plus data cleaning is the whole problem.                                            |

A later "intermediary" catalogue can revisit several of these once the starter is done.

---

## How a CE picks an assignment

1. Read this whole document once.
2. Pick one that you would *want to use* as a tool — not one that sounds impressive.
3. If you know the domain (clinical ops), picking from that side is fine; it reduces one layer of confusion.
4. If you don't know the domain, pick from the general-purpose side. Nothing is gained by wrestling with unfamiliar vocabulary during your first full-stack build.
5. Tell the reviewer which one you picked *before* you start phase 1 of the workflow. The reviewer's job is to push back if you've picked something that doesn't fit the envelope — better now than after the brainstorm.
