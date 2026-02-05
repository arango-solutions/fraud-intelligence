# Fraud Intelligence Demo

An end-to-end **Fraud Intelligence Demo** built around **ArangoDB + graph analytics + agentic workflows**.

## What this is

This repo contains **PRDs + runnable scripts** for a demo that:

- Ingests unstructured sources (e.g., deeds/news/watchlists) into a graph (“GraphRAG” + ontology)
- Resolves proxy / duplicate identities (“Benami”) via entity resolution
- Runs graph analytics (e.g., PageRank/WCC/cycle detection) in an agentic workflow
- Computes and propagates risk scores (direct / inferred / path risk)
- Presents results through three stakeholder “lenses”: Investigator, Analyst, Executive

## Repository contents

- `PRD/PRD.md`: Overall project PRD and phased checklist
- `PRD/Fraud Use Cases PRD.md`: Consolidated fraud scenarios (patterns, signals, AQL starters, demo steps)
- `PRD/Graph Analytics PRD.md`: Subsystem 3 (AQL-native investigations + algorithm-backed analytics + optional agentic workflow)
- `PRD/Identity Intelligence PRD.md`: Entity resolution (“Golden Record”) requirements
- `PRD/Risk Intelligence PRD.md`: Risk scoring and propagation requirements
- `PRD/Ontology PRD.md`: Ontology + semantic ingestion requirements
- `PRD/Data Generator PRD.md`: Synthetic Indian Banking context data generation requirements
- `PRD/Visualization & User Experience PRD.md`: UI/UX “three lenses” requirements
- `scripts/`: Phase 1–3 runners and implementation scripts
- `docs/`: runbooks + validation reports + themes

## Status

- **Current**: Phase 1–3 are implemented and validated on REMOTE (AMP).
- **Next**: Optional Subsystem 3 “Graph Analytics AI Platform” / agentic workflow integration (see `GRAPH_ANALYTICS_SETUP_GUIDE.md`).

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

4. **(Optional) Phase 3 MVP app (“three lenses”)**:

```bash
streamlit run apps/phase3_demo_app.py
```

## Notes

- `.env` is required for REMOTE connectivity and must not be committed (see `.env.example`).
- `GRAPH_ANALYTICS_SETUP_GUIDE.md` is a forward-looking template for optional platform integration; do not paste real secrets into docs.

