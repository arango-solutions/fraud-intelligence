# Fraud Intelligence Demo

Design docs for a **Fraud Intelligence Demo** built around **ArangoDB + Graph Analytics + agentic workflows**.

## What this is

This repo currently contains **Product Requirements Documents (PRDs)** describing a demo that:

- Ingests unstructured sources (e.g., deeds/news/watchlists) into a graph (“GraphRAG” + ontology)
- Resolves proxy / duplicate identities (“Benami”) via entity resolution
- Runs graph analytics (e.g., PageRank/WCC/cycle detection) in an agentic workflow
- Computes and propagates risk scores (direct / inferred / path risk)
- Presents results through three stakeholder “lenses”: Investigator, Analyst, Executive

## Repository contents

- `PRD/PRD.md`: Overall project PRD and phased checklist
- `PRD/Identity Intelligence PRD.md`: Entity resolution (“Golden Record”) requirements
- `PRD/Risk Intelligence PRD.md`: Risk scoring and propagation requirements
- `PRD/Ontology PRD.md`: Ontology + semantic ingestion requirements
- `PRD/Data Generator PRD.md`: Synthetic Indian Banking context data generation requirements
- `PRD/Visualization & User Experience PRD.md`: UI/UX “three lenses” requirements

## Status

- **Current**: Documentation / requirements definition
- **Next**: Implement generator, schema/ontology, ingestion pipeline, risk scoring, and a demo UI

## Suggested next steps (implementation order)

1. **Data generator**: create a synthetic dataset with injected fraud topologies (circular trading, mule rings)
2. **Ontology + ingestion**: map unstructured text into the graph with consistent semantics
3. **Identity resolution**: configure blocking/similarity/clustering and publish Golden Records
4. **Risk intelligence**: implement seed risk, propagation, and reportable risk factors
5. **Visualization**: build the “three lenses” UI and integrate explainability (evidence paths + citations)

## Notes

- This repo does not yet include runnable code or environment setup.
- As implementation lands, add: `docs/`, `src/`, `scripts/`, and a “Getting Started” section with prerequisites.

