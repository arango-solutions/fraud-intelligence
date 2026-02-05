This PRD defines **Subsystem 3: Graph Analytics Engine** for the Fraud Intelligence Demo. It is an expansion of `PRD/PRD.md`.

---

## PRD: Subsystem 3 — Graph Analytics (Algorithms + Agentic Workflow)

### Purpose

Demonstrate that ArangoDB can:

- Answer fraud-investigation questions with **native AQL traversal and graph queries** (interactive investigator workflow)
- Run **graph algorithms** (e.g., WCC, PageRank, SCC / cycle detection) to find patterns at scale
- (Optional) Use an **agentic workflow** (“graph-analytics-ai” / ArangoAI suite) to orchestrate analyses and generate narrative reports

This subsystem is the “analytics brain” that turns the Phase 1/2 graph into actionable fraud intelligence.

---

## Scope (what this PRD covers)

### In-scope

- Algorithm-backed detection of core fraud patterns:
  - **Circular trading** (cycles / SCCs on `transferredTo`)
  - **Money mule rings** (WCC + hub detection such as PageRank/degree on `transferredTo`, corroborated by `DigitalLocation`)
  - **Undervalued property** (AQL rule + optional clustering by district)
  - **Benami / proxy identities** (ER clusters + GoldenRecord rollups)
- Report outputs suitable for demo:
  - “Top findings”, “evidence paths”, and “recommended next actions”
- Operational demo runner(s) that are **safe** and **repeatable**

### Out-of-scope (for now)

- Full production-grade case management system
- Long-running streaming ingestion
- Advanced ML model training

---

## System inputs

- **Primary named graph for investigations**: `KnowledgeGraph`
  - Combines instance data (Phase 1), ontology (ArangoRDF PGT), and ER edges (Phase 2)
- **Collections and key edges**
  - `BankAccount` + `transferredTo` (money flow)
  - `Person` + `hasAccount` (ownership/control)
  - `DigitalLocation` + `accessedFrom`/`hasDigitalLocation` (digital forensics)
  - `RealProperty` + `registeredSale` + `RealEstateTransaction` (real estate)
  - `GoldenRecord` + `resolvedTo` (ER output)

---

## Functional requirements

### GA-001: AQL-native cycle discovery from a single suspicious account

**Goal:** In the investigator lens, prove a circular trading loop exists starting from a selected `BankAccount`, without any precomputed algorithm output.

**Implementation shape:**
- A Visualizer canvas action “Find cycles (AQL)” that:
  - takes `@nodes` (selected `BankAccount` ids)
  - runs a traversal and returns paths where the traversal returns to start

**Success criteria:**
- From a demo-seeded suspicious `Person` → `BankAccount`, the cycle action returns at least one cycle path.

### GA-002: Cycle discovery at scale (algorithm-backed)

**Goal:** Demonstrate algorithmic discovery of circular trading rings across the full transaction network.

**Approach options:**
- SCC (Strongly Connected Components) on `transferredTo`
- Dedicated cycle enumeration heuristics (bounded lengths) for demo readability

**Success criteria:**
- Produce a report listing N detected rings, total amount cycled (aggregate), and top entities involved.

### GA-003: Money mule networks (WCC + hub detection)

**Goal:** Detect hub-and-spoke networks where many sources funnel funds into a hub quickly.

**Approach:**
- WCC on `BankAccount` + `transferredTo` (or filtered time window)
- Hub detection via:
  - inbound degree
  - PageRank (optional)
- Corroboration via `DigitalLocation` (shared device/IP)

**Success criteria:**
- Identify top hub(s) and list mule sources.
- Show shared device/IP evidence.

### GA-004: Undervalued property (AQL rule + rollup)

**Goal:** Flag property sales where `transactionValue <= circleRateValue`, and roll up by district.

**Success criteria:**
- Output a ranked list by district and sample cases for investigation.

### GA-005: Benami / proxy identities (ER + analytics narrative)

**Goal:** Show “before vs after” with `resolvedTo` and `GoldenRecord`, and summarize clusters that matter.

**Success criteria:**
- Report includes at least one GoldenRecord with ≥2 inbound Persons and the accounts controlled.

---

## Non-functional requirements

- **Security**: never store secrets in docs; `.env` is local-only and must remain in `.gitignore`.
- **Repeatability**: demo runs should be safe to rerun; any cleanup must be scoped and explicit.
- **Performance**: demo workflows should complete in minutes; interactive AQL queries should be bounded (`LIMIT`).

---

## Deliverables (for the demo)

- A “Graph Analytics” demo runner that can be pointed at a cluster (non-AMP or AMP) via `.env`.
- A demo script/runbook describing:
  1) investigator flow (AQL-native cycle)
  2) algorithm-backed discovery (SCC/WCC/PageRank)
  3) generated narrative report and KPI summary

References:
- `PRD/Fraud Use Cases PRD.md` (canonical scenario definitions)
- `docs/domain_description.md` and `docs/business_requirements.md` (optional agentic inputs)

