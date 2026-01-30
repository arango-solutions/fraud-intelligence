Phase 1 sub‑agent lineup (concrete)
Run these 5 sub-agents in parallel during Phase 1; each produces a specific artifact you can treat as a gate before moving on.
1) PRD compliance agent (requirements gatekeeper)
Scope: Phase 1 checklist in PRD/PRD.md + canonical schema/naming section.
Outputs:
docs/phase1-requirements-checklist.md: decomposed tasks + acceptance criteria (pass/fail)
docs/schema-contract.md: canonical collections/edges/required fields + invariants (one-page)
Review comments on any naming drift (e.g., field names, ontology filename, edge names)
2) Ontology + schema agent (semantic + physical model)
Scope: Turn PRD/Ontology PRD.md + canonical schema into a usable ontology + mapping plan.
Outputs:
ontology/fraud-intelligence.owl (or your chosen path): initial ontology skeleton matching the PRDs
ontology/mapping.md: ontology URI → stored field mapping table (authoritative)
scripts/schema_bootstrap.aql (or .js): creates collections, edge collections, indexes, (optional) ArangoSearch vieligned to PRDs
3) Data generator agent (synthetic data + fraud topology)
Scope: Implement generator per PRD/Data Generator PRD.md and canonical schema.
Outputs:
scripts/generate_data.py: deterministic generator (seedable) producing JSON/CSV for each collection
data/sample/: a small dataset (e.g., 500 nodes) for fast iteration
data/demo/: target-scale dataset (~10k/~50k) optional but supported
docs/data_dictionary.md: every generated field, type, and meaning
4) Ingest/ETL agent (repeatable load into ArangoDB)
Scope: Load generator outputs into ArangoDB reliably and idempotently.
Outputs:
scripts/ingest.py (or scripts/ingest.sh + AQL): imports data, creates indexes/views, validates counts
scripts/reset_db.py (safe dev reset): drops only demo collections (guardrails!)
docs/ingestion_runbook.md: exact commands + required env vars (no secrets committed)
5) QA / invariants agent (tests + scenario assertions)
Scope: Make Phase 1 measurable and prevent drift.
Outputs:
tests/test_generator_invariants.py: asserts fraud shapes exist (cycles, mule hubs, undervalued props)
tests/test_schema_contract.py: asserts required collections/fields exist after ingest
tests/test_basic_queries.aql (or python tests): a few “smoke traversals” that must work
docs/phase1-validation-report.md: what was validated + results
How to use them (cadence)
At start of Phase 1: PRD agent produces checklist + schema contract (this becomes the gate).
Each implementation loop: generator + ingest + ontology agents iterate; QA agent updates assertions.
Before calling Phase 1 “done”: QA report must be green; PRD agent confirms checklist is satisfied.
Definition of done (Phase 1)
Ontology + mapping exists and matches canonical schema names.
Generator produces data that conforms to schema contract and includes required fraud topologies.
Ingest loads data idempotently and creates required indexes/views.
Tests pass and demonstrate at least: cycle present, mule hub present, undervalued property present, and basic traversals work.
If you tell me whethent JSONL vs CSV outputs for the generator and whether you’re running ArangoDB via local Docker or a remote instance, I can tailor the exact file layout and scripts for these agent outputs.
