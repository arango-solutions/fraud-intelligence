# Visualization runbook (Graphs + Themes)

This repo supports three **named graphs** for ArangoDB's Graph Viewer, plus tailored themes:

- **`OntologyGraph`**: ontology-as-data (classes + properties) derived from `ontology/fraud-intelligence.owl`
- **`DataGraph`**: Phase 1 instance data (transactions, properties, accounts, etc.)
- **`KnowledgeGraph`**: combination of OntologyGraph + DataGraph (optionally linked via `type` edges)

## Prereqs

- ArangoDB running (LOCAL via Docker or AMP REMOTE)
- Phase 1 data ingested (see `docs/ingestion_runbook.md`)

## 1) Create/update named graphs

LOCAL (recommended first):

```bash
python scripts/define_graphs.py --mode LOCAL --with-type-edges
```

REMOTE (AMP):

```bash
python scripts/define_graphs.py --mode REMOTE --with-type-edges
```

Notes:
- `--force` truncates and reloads ontology edge collections (`domain`, `range`, `subClassOf`, `type`) before rebuilding.

## 2) Install themes + default viewpoint/actions

LOCAL:

```bash
python scripts/install_graph_themes.py --mode LOCAL
```

REMOTE:

```bash
python scripts/install_graph_themes.py --mode REMOTE
```

Themes live in:

- `docs/themes/ontology_theme.json`
- `docs/themes/datagraph_theme.json`
- `docs/themes/knowledgegraph_theme.json`

## 3) Use in ArangoDB UI

Open the ArangoDB web UI and go to the **Graph Viewer**.

- Pick a graph (`OntologyGraph`, `DataGraph`, or `KnowledgeGraph`)
- Choose the default theme (Ontology/Data/Knowledge)
- Use the installed canvas action “Expand Relationships” from the node context menu

