# Visualization runbook (Graphs, Themes, Saved Queries & Canvas Actions)

This repo customizes ArangoDB's **Graph Visualizer** with three named graphs, two
themes per data graph (entity-type colors + a switchable risk heatmap), a panel
of saved "hunting" queries, and right-click canvas actions for investigation.

Named graphs:

- **`OntologyGraph`**: ontology-as-data (classes + properties) derived from `ontology/fraud-intelligence.owl`
- **`DataGraph`**: Phase 1 instance data (people, accounts, transfers, properties, etc.)
- **`KnowledgeGraph`**: combination of OntologyGraph + DataGraph (linked via `dataType` edges)

## Prereqs

- ArangoDB running (LOCAL via Docker or REMOTE cluster)
- Phase 1 data ingested (see `docs/ingestion_runbook.md`)
- **Phase 2** (entity resolution) for the alias queries, and **Phase 3** (risk
  scoring) for the risk-dependent queries and the Risk Heatmap theme — see
  "Risk-dependent capabilities" below.

## 1) Create/update named graphs

```bash
python scripts/define_graphs.py --mode LOCAL --with-type-edges    # or --mode REMOTE
```

Notes:
- `--force` truncates and reloads ontology edge collections (`domain`, `range`, `subClassOf`, `type`) before rebuilding.

## 2) Install themes + saved queries + canvas actions

```bash
python scripts/install_graph_themes.py --mode LOCAL    # or --mode REMOTE
```

This single, idempotent installer upserts everything below (themes into
`_graphThemeStore`; saved queries into `_queries`; canvas actions into
`_canvasActions`; all linked to the default viewpoint). It is safe to re-run.

## 3) Themes

Theme files live in `docs/themes/`:

| File | Theme name | Graph(s) | Default? | Purpose |
|---|---|---|---|---|
| `ontology_theme.json` | `Ontology` | OntologyGraph | yes | Ontology class/property colors |
| `datagraph_theme.json` | `Data` | DataGraph | yes | Entity-type colors |
| `knowledgegraph_theme.json` | `Knowledge` | KnowledgeGraph | yes | Entity-type colors |
| `risk_heatmap_theme.json` | `Risk Heatmap` | DataGraph, KnowledgeGraph | no (opt-in) | Colors risk-bearing entities by `riskScore` |

Exactly one theme per graph is `isDefault: true` (the entity-type theme). The
**Risk Heatmap** is installed as `isDefault: false`, so it never auto-applies —
switch to it from the Visualizer **Legend** → theme picker.

### Risk Heatmap color bands (`riskScore`, 0–100 scale)

| Risk | Score | Color |
|---|---|---|
| High | ≥ 70 | red `#e53e3e` |
| Medium | 40–69 | yellow `#ecc94b` |
| Low | < 40 | green `#48bb78` |

Applied to `Person`, `Organization`, `BankAccount`, `RealProperty`,
`RealEstateTransaction`, and `GoldenRecord`. Structural nodes (Address, Device,
Document) stay neutral grey so the risk signal stands out. Rules use the
Visualizer's verified nested attribute-rule schema (see the
`arangodb-visualizer-customizer` skill).

> The risk bands depend on `riskScore` being populated — run **Phase 3 risk
> scoring** first (below), otherwise every node renders green (low).

## 4) Saved queries (Queries panel)

The installer populates the Visualizer **Queries** panel with starting points
that all return graph elements (vertices / edges / paths) so they render on the
canvas. Two families:

- **Use-case queries**: `UC1: Find Victor Tella`, `UC2: Top Fan-In / Fan-Out
  Accounts`, `UC3: Undervalued Property Sales`, `UC4: Highest-Risk Entities`,
  `Account Transfer Chain`.
- **`[I&W]` indications-and-warnings queries** (start from a red-flag *pattern*,
  then expand to the suspect): Circular Transaction Patterns, Shared Device Mule
  Ring, Rapid Inbound Bursts, Round Amount Transfers, Suspect Aliases, Risk
  Propagation, Gateway Accounts, Structuring Chains.

See **[`INDICATIONS_AND_WARNINGS_GUIDE.md`](INDICATIONS_AND_WARNINGS_GUIDE.md)**
for what each query surfaces, tunable bind variables, reliability tiers, and the
full "indication → Victor Tella" demo walkthrough.

## 5) Canvas actions (right-click a node)

Generic, for every collection:
- `Find 2-hop neighbors (default)`
- `[<Type>] Expand Relationships`

Investigation actions:
- **BankAccount**: `Find cycles (AQL)`, `Trace Funding Sources (upstream)`,
  `Trace Downstream Flow`, `Show Owner & Linked Accounts`,
  `Show Co-Accessed Accounts (shared device)`
- **Person**: `Reveal Aliases (Golden Record)`, `Show Accounts & Money Flows`,
  `Show Associate Network`

## 6) Risk-dependent capabilities

These require pipeline phases to have run **on the same database**:

| Capability | Requires |
|---|---|
| `Risk Heatmap` theme, `UC4: Highest-Risk Entities`, `[I&W] Risk Propagation` | **Phase 3** risk scoring (`riskScore` on nodes) |
| `[I&W] Suspect Aliases`, `[Person] Reveal Aliases` | **Phase 2** entity resolution (`GoldenRecord` + `resolvedTo`) |

Run Phase 3 risk scoring:

```bash
python scripts/phase3_risk.py --mode REMOTE     # or via: python scripts/setup_demo.py --from-phase 3
```

> **Gotcha:** if the dataset is regenerated/reloaded, `riskScore` resets to 0 and
> must be recomputed. Re-run Phase 3 afterward, or Risk Propagation/UC4 come up
> empty and the heatmap renders flat.

## 7) Use in the ArangoDB UI

Open the web UI → **Graph Viewer**:

- Pick a graph (`OntologyGraph`, `DataGraph`, or `KnowledgeGraph`).
- The entity-type theme auto-applies; switch to **Risk Heatmap** via the Legend.
- Open the **Queries** panel and run a `UC*` or `[I&W]` query.
- Right-click a node → **Canvas Actions** to expand the investigation.
