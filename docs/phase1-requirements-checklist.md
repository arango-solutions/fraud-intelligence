# Phase 1 Requirements Checklist: Data & Schema

**Phase:** Data & Schema (Setup)  
**Definition of Done:** Ontology + mapping exists, generator produces conformant data, ingest loads idempotently, tests pass with required fraud topologies.

---

## 1) Ontology & schema

- [ ] **Ontology skeleton exists** at `ontology/fraud-intelligence.owl`
  - **Acceptance criteria**
    - RDF/XML (OWL 2 DL)
    - Base URI: `http://www.semanticweb.org/fraud-intelligence#`
    - Includes core classes and relationships described in `PRD/Ontology PRD.md`

- [ ] **Ontology ↔ storage mapping exists** at `ontology/mapping.md`
  - **Acceptance criteria**
    - Explicit mapping for camelCase ontology properties → snake_case stored fields
    - Documents how conceptual classes map to physical collections

- [ ] **Physical schema bootstrap exists** at `scripts/schema_bootstrap.js`
  - **Acceptance criteria**
    - Creates collections + edge collections in ArangoDB (idempotent)
    - Creates required indexes for Phase 1

---

## 2) Data generator (CSV)

- [ ] **Generator script exists** at `scripts/generate_data.py`
  - **Acceptance criteria**
    - Deterministic and seedable
    - Emits **CSV** (one file per collection/edge collection) to a target directory

- [ ] **Sample dataset exists** at `data/sample/`
  - **Acceptance criteria**
    - Contains the CSVs needed for ingestion
    - Includes at least: one cycle, one mule hub-and-spoke, and one undervalued property case

- [ ] **Data dictionary exists** at `docs/data_dictionary.md`
  - **Acceptance criteria**
    - Documents every generated field, type, and meaning

---

## 3) Ingest / ETL

- [ ] **Ingest script exists** at `scripts/ingest.py`
  - **Acceptance criteria**
    - Reads `ARANGO_URL`, `ARANGO_USERNAME`, `ARANGO_PASSWORD`, `ARANGO_DB`
    - Creates database (if permitted) and schema (idempotent)
    - Imports CSVs idempotently (skip if already populated unless `--force`)
    - Validates row counts and basic referential integrity

- [ ] **Reset script exists** at `scripts/reset_db.py`
  - **Acceptance criteria**
    - Guardrails: dry-run by default; refuses non-local targets unless explicitly allowed
    - Drops/truncates only whitelisted demo collections

- [ ] **Ingestion runbook exists** at `docs/ingestion_runbook.md`
  - **Acceptance criteria**
    - Step-by-step commands for local Docker and remote DB usage

---

## 4) QA / invariants

- [ ] **Generator invariants test** at `tests/test_generator_invariants.py`
  - **Acceptance criteria**
    - Detects: cycle present, mule hub present, undervalued property present

- [ ] **Schema contract test** at `tests/test_schema_contract.py`
  - **Acceptance criteria**
    - When ArangoDB is available, asserts required collections exist after ingest

- [ ] **Basic query smoke tests** at `tests/test_basic_queries.aql`
  - **Acceptance criteria**
    - Contains a few “smoke traversals” that should return non-empty results after ingest

- [ ] **Validation report** at `docs/phase1-validation-report.md`
  - **Acceptance criteria**
    - Records what ran and pass/fail status

