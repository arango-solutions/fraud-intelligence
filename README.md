# Fraud Intelligence Demo

An end-to-end **Fraud Intelligence Demo** targeting Risk & Compliance teams at Indian financial institutions. It demonstrates how an **Agentic AI Graph platform** can autonomously detect, analyze, and explain sophisticated financial crime schemes that defeat conventional rule-based systems.

## The Business Problem

Indian banks and NBFCs face fraud schemes that are deliberately engineered to be invisible in siloed, transactional systems:

- **Circular Trading** — funds loop between shell accounts to fabricate turnover and launder money through layering. No single transaction looks suspicious; only the closed loop reveals the scheme.
- **Money Mule Rings ("Smurfing")** — many low-activity accounts funnel small amounts toward a single aggregator, often sharing a device or IP fingerprint. Classic threshold rules miss it entirely.
- **Real Estate Value Manipulation (Circle Rate Evasion)** — property deals are registered at or below the government-mandated minimum ("circle rate") to hide a cash component, evading stamp duty and laundering value off-ledger.
- **Benami / Proxy Identities** — the same real person appears as multiple customer records under slight name variations or partial KYC. Relationships, accounts, and risk are fragmented across identities, making it impossible to see the true exposure.
- **Guilt by Association** — a seemingly clean customer is materially risky because of who they transact with. Risk propagates through the network from known bad actors (watchlist hits, shell companies, tainted flows) to connected parties.

These schemes share a common trait: **the evidence is in the graph, not in the row**. The platform makes that evidence visible, explainable, and actionable.

## Regulatory Context

Outputs are framed for **PMLA / FEMA / FIU-IND** compliance, including STR-ready recommendations and a full audit trail of every analytical execution.

## What This Demo Shows

This repo contains **PRDs + runnable scripts** for a demo that:

- Ingests unstructured sources (deeds, news articles, watchlists) into a knowledge graph via ontology-driven GraphRAG
- Resolves Benami / proxy identities into `GoldenRecord` entities via entity resolution
- Runs graph analytics (PageRank, WCC, cycle detection) driven by an agentic AI workflow
- Computes and propagates risk scores — direct, inferred ("guilt by association"), and path-based
- Presents results through three stakeholder lenses: **Investigator**, **Analyst**, **Executive**

## Repository contents

- `PRD/PRD.md`: Overall project PRD and phased checklist
- `PRD/Fraud Use Cases PRD.md`: Consolidated fraud scenarios (patterns, signals, AQL starters, demo steps)
- `PRD/Graph Analytics PRD.md`: Subsystem 3 (AQL-native investigations + algorithm-backed analytics + optional agentic workflow)
- `PRD/Identity Intelligence PRD.md`: Entity resolution ("Golden Record") requirements
- `PRD/Risk Intelligence PRD.md`: Risk scoring and propagation requirements
- `PRD/Ontology PRD.md`: Ontology + semantic ingestion requirements
- `PRD/Data Generator PRD.md`: Synthetic Indian Banking context data generation requirements
- `PRD/Visualization & User Experience PRD.md`: UI/UX "three lenses" requirements
- `scripts/`: Phase 1–3 runners and implementation scripts
- `docs/`: runbooks + validation reports + themes

## Status

- **Current**: Phase 1–3 are implemented and validated on REMOTE (AMP).
- **Next**: Optional Subsystem 3 "Graph Analytics AI Platform" / agentic workflow integration (see `GRAPH_ANALYTICS_SETUP_GUIDE.md`).

## Quick start (REMOTE)

1. **Phase 1 (data + ingest + graphs/themes)**:

```bash
python scripts/test_phase1.py --remote-only --install-visualizer
```

2. **Phase 2 (entity resolution)**:

```bash
python scripts/test_phase2.py --remote-only
```

3. **Phase 3 (analytics + risk + reports)**:

```bash
python scripts/test_phase3.py --remote-only
```

4. **(Optional) Phase 3 MVP app ("three lenses")**:

```bash
streamlit run apps/phase3_demo_app.py
```

## Running AI-Powered Fraud Detection 🚀

**NEW**: The agentic-graph-analytics is now configured for Indian banking fraud intelligence with automatic tracking!

### Quick Start (AI Analytics)

```bash
# Run AI-powered fraud detection (catalog tracking enabled by default)
python run_fraud_analysis.py
```

**Reports will be generated in:** `fraud_analysis_output/`

**What you'll get:**
- Circular trading detection (₹ Crores/Lakhs)
- Money mule network identification
- Circle rate evasion flagging
- Benami identity resolution
- Risk classifications (CRITICAL/HIGH/MEDIUM/LOW)
- STR-ready recommendations with PMLA/FEMA references
- **NEW:** Full execution tracking in analytics catalog for compliance/audit

### Analytics Catalog (NEW)

The workflow now automatically tracks all executions for compliance and historical analysis:

- **Monthly Epochs:** Analyses grouped by month (e.g., "fraud-detection-2026-02")
- **Full Lineage:** Requirements → Use Cases → Templates → Executions → Results
- **Historical Trends:** Compare fraud patterns across months
- **Compliance Ready:** Complete audit trail for PMLA/FEMA/FIU-IND reviews

**See:** `CATALOG_USAGE_GUIDE.md` for detailed catalog features and queries

**Disable catalog (optional):**
```bash
FRAUD_ANALYSIS_ENABLE_CATALOG=false python run_fraud_analysis.py
```

### Documentation

**Start here:** `DOCUMENTATION_INDEX.md` - Master guide to all documentation

**Essential docs:**
- `HOW_TO_RUN_GRAPH_ANALYTICS.md` - **READ THIS FIRST** - Complete instructions
- `PRE_FLIGHT_CHECKLIST.md` - Verify setup before running
- `QUICK_START.md` - Quick reference and examples
- `ARCHITECTURE.md` - How everything fits together

### Pre-Requisites

1. Install the platform:
   ```bash
   pip install -e ~/code/agentic-graph-analytics
   ```

2. Ensure `.env` has your credentials:
   - ArangoDB connection (either naming scheme is fine):
     - `ARANGO_URL` (or `ARANGO_ENDPOINT`)
     - `ARANGO_DATABASE`
     - `ARANGO_USERNAME` (or `ARANGO_USER`)
     - `ARANGO_PASSWORD`
   - LLM API keys (OPENROUTER_API_KEY or OPENAI_API_KEY)

3. Verify connection:
   ```bash
   python -c "from graph_analytics_ai import db_connection; db_connection.test_connection()"
   ```

### Key Point

**There is NO web UI for running graph analytics.** You run Python scripts locally. See `HOW_TO_RUN_GRAPH_ANALYTICS.md` for detailed explanation.

---

## Notes

- `.env` is required for REMOTE connectivity and must not be committed (see `.env.example`).
- `GRAPH_ANALYTICS_SETUP_GUIDE.md` is a forward-looking template for optional platform integration; do not paste real secrets into docs.
