# PRD delta note (Subsystem 3 terminology alignment)

## Scope reviewed

- `GRAPH_ANALYTICS_SETUP_GUIDE.md`
- `PRD/Graph Analytics PRD.md`
- `PRD/PRD.md`
- `PRD/Fraud Use Cases PRD.md`

## What is aligned

- **Named graphs** in the implementation and demo flow: `OntologyGraph`, `DataGraph`, `KnowledgeGraph`.
- **Use Case 1**: cycle detection is **AQL-native** from a selected `BankAccount` via the Visualizer canvas action.
- **Subsystem 3 tracking**: `PRD/Graph Analytics PRD.md` exists and is linked from `PRD/PRD.md`.
- **Terminology**: “AQL-native cycle detection” vs “algorithm-backed detection at scale” are both represented (the former for demos; the latter as roadmap / platform integration).

## Minor watch-outs (clarity only; no content loss)

- **Graph name example vs implementation**:
  - Some “future integration” docs use an illustrative name like `fraud_intelligence_graph`.
  - The live demo uses `KnowledgeGraph` / `DataGraph` / `OntologyGraph`.
  - Recommendation: add a one-line note wherever `fraud_intelligence_graph` appears that it is an example mapping to the real named graphs in this repo.

- **Cycle detection wording**:
  - “SCC” (Strongly Connected Components) is correct language for directed graphs at scale.
  - The demo uses “cycle detection” language for accessibility; both are compatible.

