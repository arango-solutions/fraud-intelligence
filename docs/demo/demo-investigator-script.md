## Investigator demo script (Use Case 1: Circular trading via AQL)

### Goal (what you prove)

From a single suspicious identity (Victor Tella), you can use **AQL traversal** to find a **directed transaction cycle** starting from one of their accounts — without relying on precomputed algorithms.

### Pre-demo checklist

- Run (REMOTE):

```bash
python scripts/test_phase1.py --remote-only --install-visualizer
python scripts/test_phase2.py --remote-only
python scripts/test_phase3.py --remote-only
```

- In Visualizer, use **KnowledgeGraph** (preferred) or **DataGraph**.
- Confirm canvas action exists: **`[BankAccount] Find cycles (AQL)`**.

---

## Step-by-step (Visualizer click path)

### 1) Open the right graph

1. Open ArangoDB Web UI → **Graphs** → Visualizer.
2. Select graph: **KnowledgeGraph**.

### 2) Find Victor Tella (synthetic alias)

1. In “Search & add nodes to canvas”, search: `Victor Tella`
2. Choose the **Person** record that corresponds to the synthetic alias (it will typically have a `dup_...` key and/or `isSyntheticDuplicate=true`).

> If needed, confirm via AQL in the Query UI (no secrets):
>
> ```aql
> WITH Person
> FOR x IN Person
>   FILTER x.name == @name
>   FILTER x.isSyntheticDuplicate == true
>   SORT x._key ASC
>   LIMIT 1
>   RETURN x
> ```
>
> Bind vars: `{ "name": "Victor Tella" }`

### 3) Expand Victor Tella to reach their BankAccount

1. Select the Person node on canvas.
2. Run the canvas action: **`[Person] Expand Relationships`**.
3. You should see one or more `BankAccount` nodes connected via `hasAccount`.

### 4) Detect a circular trading path from the account (AQL traversal)

1. Right-click the `BankAccount` node.
2. Run the canvas action: **`[BankAccount] Find cycles (AQL)`**.
3. The result should return a path that starts and ends at the selected `BankAccount` with `transferredTo` edges.

### What to say (talk track)

- “We start from a suspicious identity and pivot to controlled accounts.”
- “AQL can natively traverse outbound transfers and prove there is a closed loop.”
- “This is the core signature of circular trading / layering.”

---

## Expected result

- At least one returned path (`p`) where:
  - vertices include the starting `BankAccount` twice (start and end)
  - edges are `transferredTo`
  - cycle length is typically 3–6 edges for the demo

---

## Troubleshooting

- **Canvas action returns empty**:
  - The selected account is not part of a directed cycle within `maxDepth` (default 6).
  - Try the other Victor Tella alias’s account or increase `maxDepth`/`limit` in the action’s bindVariables (installed defaults: `maxDepth=6`, `limit=5`).
- **Action not visible**:
  - Re-run: `python scripts/install_graph_themes.py --mode REMOTE`
  - Ensure you are on **DataGraph** or **KnowledgeGraph** (action is installed for both).
- **Performance**:
  - Keep `limit` small (≤ 10) for live demos.

# Demo Script: Use Case 1 — Circular Trading Detection (Investigator Flow)

This document provides a step-by-step script for demonstrating **Use Case 1: Circular Trading ("Round Trip" Transfers)** using ArangoDB's Graph Visualizer. This demo showcases AQL-native cycle detection from a single suspicious account, demonstrating how investigators can discover fraud patterns interactively without precomputed algorithms.

---

## Overview

**Use Case 1** demonstrates how a suspicious `Person` entity (Victor Tella, a synthetic alias) can be traced through relationships to reveal circular trading patterns. The workflow shows:

1. Starting from a high-risk `Person` entity
2. Expanding relationships to discover connected `BankAccount` entities
3. Using an AQL-native canvas action to detect directed cycles in transfer flows
4. Visualizing the complete fraud ring structure

**Key Message:** "From a single suspicious account, AQL can traverse outward and prove a closed transaction loop exists (cycle detection without precomputed algorithms)."

---

## Prerequisites

- ArangoDB instance running (LOCAL via Docker or AMP REMOTE)
- Phase 1 data ingested (see `docs/ingestion_runbook.md`)
- Phase 2 Entity Resolution completed (see `docs/phase2-runbook.md`)
- Named graphs defined (`OntologyGraph`, `DataGraph`, `KnowledgeGraph`)
- Graph themes and canvas actions installed (see `docs/visualization_runbook.md`)

**Note:** Ensure the canvas action `[BankAccount] Find cycles (AQL)` is installed for the target graph. This action is automatically installed by `scripts/install_graph_themes.py`.

---

## Step-by-Step Visualizer Workflow

### Step 1: Open Graph Visualizer

1. Open the ArangoDB web UI
2. Navigate to **Graph Viewer**
3. Select the graph: **`KnowledgeGraph`** (preferred) or **`DataGraph`**
   - **KnowledgeGraph** is recommended as it combines instance data with ontology relationships
   - **DataGraph** will also work but may not include ontology edges

### Step 2: Find Victor Tella (Synthetic Alias)

1. In the Graph Visualizer search bar, search for: **`Victor Tella`**
2. Alternatively, use the AQL query panel to locate the Person:
   ```aql
   FOR p IN Person
     FILTER p.name == "Victor Tella"
     FILTER p.isSyntheticDuplicate == true
     SORT p._key ASC
     LIMIT 1
     RETURN p
   ```
3. Select the `Person` node that appears (should have `isSyntheticDuplicate: true`)

**Expected Result:** A `Person` node labeled "Victor Tella" appears in the canvas. This is a synthetic duplicate created for demo purposes, representing a suspicious identity with multiple aliases.

### Step 3: Expand Relationships to Reach BankAccount

1. **Right-click** the `Person` node (Victor Tella)
2. From the context menu, select the default canvas action: **"Find 2-hop neighbors (default)"** or **"Expand Relationships"**
   - This action traverses `hasAccount` and other relationship edges
3. Look for `BankAccount` nodes connected via `hasAccount` edges
4. If multiple accounts appear, select one that is part of a cycle (typically `BankAccount/acct_42_000000` or `BankAccount/acct_42_000001` based on the demo data setup)

**Expected Result:** The canvas expands to show:
- The `Person` node (Victor Tella)
- One or more `BankAccount` nodes connected via `hasAccount` edges
- Potentially other related entities (Address, Organization, etc.)

**Note:** The demo data setup ensures that Victor Tella's two aliases are linked to specific accounts (`acct_42_000000` and `acct_42_000001`) that participate in directed cycles.

### Step 4: Run Cycle Detection Action

1. **Right-click** the selected `BankAccount` node
2. From the context menu, locate and select: **`[BankAccount] Find cycles (AQL)`**
   - This canvas action executes an AQL traversal to find directed cycles starting from the selected account

**What the Action Does:**
- Takes the selected `BankAccount` node(s) as input (`@nodes`)
- Traverses `transferredTo` edges outward (3 to `@maxDepth` hops, default `maxDepth: 6`)
- Returns paths where the traversal returns to the starting account (cycle detection)
- Uses `OPTIONS { uniqueVertices: "none", uniqueEdges: "path" }` to allow revisiting vertices but not edges
- Limits results to `@limit` paths (default `limit: 5`)

**Expected Result:** The canvas updates to show:
- One or more **directed cycle paths** starting and ending at the selected `BankAccount`
- Multiple `BankAccount` nodes connected via `transferredTo` edges forming a closed loop
- The complete fraud ring structure visible as a circular path

**Visual Interpretation:**
- The cycle represents funds moving in a loop: Account A → Account B → Account C → ... → Account A
- This pattern indicates "layering" behavior used to inflate turnover and launder funds
- Each edge (`transferredTo`) shows transfer amounts, timestamps, and transaction types

### Step 5: Interpret Results

**What to Explain:**
- "From a single suspicious account, AQL can traverse outward and prove a closed transaction loop exists (cycle detection without precomputed algorithms)."
- The cycle demonstrates **circular trading** behavior where accounts repeatedly move funds in a loop
- This pattern is suspicious because:
  - It inflates turnover artificially
  - It represents "layering" behavior in money laundering
  - Tight timing windows and repeated amounts suggest coordinated fraud

**Key Evidence Points:**
- The cycle returns to the starting account (proving a closed loop)
- Multiple accounts are involved (fraud ring)
- Transfer edges show amounts, timestamps, and transaction types

---

## Expected Results

### Successful Cycle Detection

When the cycle detection action succeeds, you should see:

1. **Visual Result:**
   - A closed loop of `BankAccount` nodes connected by `transferredTo` edges
   - The starting account appears at both the beginning and end of the cycle
   - Typically 3-6 accounts involved in the cycle

2. **Path Details:**
   - Each path returned represents one complete cycle
   - Paths may vary in length (number of hops)
   - Multiple cycles may exist from the same starting account

3. **Edge Attributes:**
   - `transferredTo` edges show:
     - `amount`: Transfer amount
     - `timestamp`: When the transfer occurred
     - `txnType`: Transaction type
     - `scenario`: May include `"cycle"` tag (for demo data, not required for detection)

### Example Cycle Structure

```
BankAccount/acct_42_000000
  └─[transferredTo]─→ BankAccount/acct_42_000001
      └─[transferredTo]─→ BankAccount/acct_42_000002
          └─[transferredTo]─→ ... (more accounts)
              └─[transferredTo]─→ BankAccount/acct_42_000000 (returns to start)
```

---

## Troubleshooting

### Issue: Empty Results (No Cycles Found)

**Possible Causes:**

1. **Account Not in Cycle**
   - **Solution:** Try a different `BankAccount` node. Not all accounts participate in cycles.
   - **Check:** Verify the account has outbound `transferredTo` edges using the AQL query panel:
     ```aql
     FOR e IN transferredTo
       FILTER e._from == "BankAccount/acct_42_000000"
       RETURN e
     ```

2. **maxDepth Too Restrictive**
   - **Solution:** The default `maxDepth: 6` may be too small if cycles are longer. However, modifying canvas action parameters requires editing the stored action (not recommended during demo). Instead, try accounts known to be in shorter cycles (3-4 hops).

3. **limit Too Restrictive**
   - **Solution:** The default `limit: 5` may hide additional cycles. Again, modifying requires editing the stored action. For demo purposes, 5 cycles should be sufficient.

4. **No transferredTo Edges**
   - **Solution:** Verify the account has transfer relationships:
     ```aql
     FOR e IN transferredTo
       FILTER e._from == "BankAccount/YOUR_ACCOUNT_ID"
       RETURN COUNT()
     ```
   - If no edges exist, the account is not part of any transfer network.

5. **Wrong Graph Selected**
   - **Solution:** Ensure you're using `KnowledgeGraph` or `DataGraph`. `OntologyGraph` does not contain instance data.

6. **Data Not Ingested**
   - **Solution:** Verify Phase 1 data ingestion completed successfully. Check that `transferredTo` edges exist in the database.

### Issue: Action Not Available in Context Menu

**Possible Causes:**

1. **Canvas Action Not Installed**
   - **Solution:** Run the theme installation script:
     ```bash
     python scripts/install_graph_themes.py --mode LOCAL  # or --mode REMOTE
     ```

2. **Wrong Node Type Selected**
   - **Solution:** Ensure you're right-clicking a `BankAccount` node, not a `Person` or other entity type.

3. **Wrong Graph Context**
   - **Solution:** The action is graph-specific. Ensure you're using `KnowledgeGraph` or `DataGraph` (not `OntologyGraph`).

### Issue: Too Many Results (Performance)

**Possible Causes:**

1. **Account in Multiple Cycles**
   - **Solution:** This is expected. The `limit: 5` parameter should cap results. If performance is slow, the dataset may be very large—consider using a smaller test dataset for demos.

---

## Overall Investigator Flow Context

This demo script focuses on **Use Case 1** within the broader investigator workflow. The complete investigator journey typically includes:

1. **Initial Suspicion** → Start from a high-risk `Person`, `WatchlistEntity`, or flagged `BankAccount`
2. **Relationship Expansion** → Use canvas actions to explore connections (accounts, properties, organizations)
3. **Pattern Detection** → Apply specialized actions like cycle detection, risk scoring, or entity resolution
4. **Evidence Gathering** → Collect paths, amounts, timestamps, and related entities
5. **Risk Assessment** → Review `riskScore`, `riskReasons`, and `riskPath` fields
6. **Reporting** → Document findings with visual evidence paths

**Integration with Other Use Cases:**
- **Use Case 2:** Money Mule Rings (hub-and-spoke detection)
- **Use Case 3:** Undervalued Property Transactions
- **Use Case 4:** Benami/Proxy Identities (Entity Resolution)
- **Use Case 5:** Risk Intelligence (guilt by association)

Each use case can be demonstrated using similar Visualizer workflows with appropriate canvas actions.

---

## Notes

- **No Secrets:** This script does not include any database credentials, connection strings, or `.env` file contents. All connection details should be managed via environment variables or secure configuration.
- **Graph Preference:** `KnowledgeGraph` is preferred because it combines instance data with ontology relationships, providing richer context for investigations.
- **Demo Data:** Victor Tella and associated accounts are synthetic data created specifically for demonstration purposes. In production, investigators would start from real flagged entities.
- **AQL-Native:** This demo emphasizes that cycle detection is performed using native AQL traversal, not precomputed algorithm outputs. This allows real-time, interactive investigation.

---

## References

- **Use Case Definition:** `PRD/Fraud Use Cases PRD.md` (Use Case 1)
- **Graph Analytics PRD:** `PRD/Graph Analytics PRD.md` (GA-001)
- **Visualization Setup:** `docs/visualization_runbook.md`
- **Canvas Actions:** `scripts/install_graph_themes.py`
- **Integration Tests:** `tests/test_fraud_patterns_integration.py`
