## Analyst + Executive demo script (5–7 minutes)

This script uses Phase 3 outputs (analytics + risk scoring) and the optional Streamlit MVP app.

### Pre-demo command (REMOTE)

```bash
python scripts/test_phase3.py --remote-only
```

Artifacts:
- `docs/phase3-analytics-report.md`
- `docs/phase3-validation-report.md`

---

## Analyst lens (3–4 minutes)

### What to show

1. Open `docs/phase3-analytics-report.md`
   - Point out the counts for:
     - circular trading edges
     - mule edges + hub count
     - undervalued property sales
     - ER outputs present (`GoldenRecord`, `resolvedTo`)

2. Explain “why these are compelling”
   - Each count corresponds to a fraud hypothesis with graph evidence.
   - This is the fast “sanity dashboard” before deeper investigation.

3. Show risk fields exist and are explainable
   - For key entities (Person/BankAccount/GoldenRecord), show:
     - `riskDirect` (pattern participation / rule triggers)
     - `riskInferred` (guilt-by-association)
     - `riskPath` (taint via transaction flows)
     - `riskScore` (roll-up)
     - `riskReasons` (audit-friendly strings)

---

## Executive lens (2–3 minutes)

### What to show

1. Run the Streamlit MVP (optional but impactful):

```bash
streamlit run apps/phase3_demo_app.py
```

2. Go to the **Executive** tab
   - Show district-level aggregates (avg/max risk + counts).
   - Talk track: “we can summarize hotspots for leadership prioritization.”

3. Close with the business message
   - “Investigator can drill into evidence paths.”
   - “Analyst sees patterns + distribution.”
   - “Executive sees geography/portfolio exposure.”

# Demo Script: Analyst & Executive Lenses (Phase 3)

**Duration:** 5-7 minutes  
**Audience:** Analysts and Executives  
**Prerequisites:** Phase 3 data ingested, risk scores computed

---

## Introduction (30 seconds)

Welcome to the Fraud Intelligence Phase 3 demo. Today we'll explore two lenses:

1. **Analyst Lens** — Deep dive into fraud patterns, risk scoring, and investigative workflows
2. **Executive Lens** — High-level risk aggregation and geographic insights

Both lenses leverage our graph-based risk intelligence system, which computes risk scores using direct evidence, inferred relationships, and path-based propagation.

---

## Part 1: Analyst Lens (3-4 minutes)

### Setup and Validation

**Command to run:**
```bash
python scripts/test_phase3.py --remote-only
```

This command:
- Validates connectivity to the remote ArangoDB instance
- Runs analytics aggregation (`scripts/phase3_analytics.py`)
- Computes risk scores (`scripts/phase3_risk.py`)
- Executes integration tests

**Expected output:** Validation report at `docs/phase3-validation-report.md` showing all checks passing.

### Review Analytics Report

**Open:** `docs/phase3-analytics-report.md`

**Key metrics to highlight:**

1. **Pattern Counts:**
   - Circular trading edges: Shows round-trip money laundering patterns
   - Money mule ring edges: Indicates smurfing/hub-and-spoke structures
   - Mule hubs (≥50 inbound transfers): Identifies aggregation accounts
   - Mule shared devices: Reveals coordinated fraud networks
   - Undervalued property sales: Flags tax evasion and off-ledger transactions

2. **Entity Resolution:**
   - GoldenRecord count: Consolidated identities from Phase 2
   - resolvedTo edges: Links between duplicate Person records and their golden records

**Narrative:** "These counts represent real fraud patterns detected in our graph. The system identifies suspicious transaction structures, not just individual transactions."

### Launch Phase 3 Demo App

**Command to run:**
```bash
streamlit run apps/phase3_demo_app.py
```

**Navigate to:** Analyst tab

### Analyst Dashboard Walkthrough

**1. Pattern Statistics (JSON output)**

The dashboard shows aggregate counts:
- `cycleEdges`: Circular trading patterns
- `muleEdges`: Money mule transactions
- `undervalued`: Property sales below circle rate
- `highRiskPeople`: Persons with riskScore ≥ 80

**Narrative:** "These statistics give analysts a quick health check of fraud activity in the system. Notice how we're counting patterns, not just individual transactions."

**2. Top Mule Hubs Table**

Shows accounts receiving the most inbound mule transfers, sorted by volume.

**Narrative:** "This identifies aggregation points in money laundering networks. Analysts can click through to investigate these hub accounts in the Visualizer, tracing the inbound flow from mule accounts."

### Risk Fields Deep Dive

**Key risk fields to explain:**

- **`riskDirect`**: Risk from direct evidence (e.g., account participates in circular trading, receives mule transfers, property transaction is undervalued)
- **`riskInferred`**: Risk propagated from high-risk neighbors via `relatedTo` or `associatedWith` edges (with decay factors: 0.8 for relatedTo, 0.6 for associatedWith)
- **`riskPath`**: Risk propagated along transaction paths (`transferredTo` edges) from high-risk seed accounts, with exponential decay per hop
- **`riskScore`**: Final risk score = MAX(riskDirect, riskInferred, riskPath)
- **`riskReasons`**: Array of human-readable explanations (e.g., `["mule_hub_inbound>=50"]`, `["circular_trading_cycle_participant"]`, `["undervalued_property"]`)

**Narrative:** "Our risk model uses three complementary signals. Direct risk comes from known fraud patterns. Inferred risk captures 'guilt by association' — if you're connected to a high-risk entity, you inherit some risk. Path risk propagates along transaction flows, so accounts downstream from known bad actors get flagged. The final riskScore takes the maximum, ensuring we don't miss any signal."

**Example to show:** "Notice how a Person might have `riskDirect: 0` but `riskInferred: 64` because they're associated with a high-risk Organization. This is how we catch seemingly clean customers who are actually risky."

### Analyst Workflow

**Narrative:** "From this dashboard, analysts can:
1. Identify high-risk entities (sort by riskScore)
2. Drill into specific patterns (mule hubs, circular trading)
3. Copy entity `_id` values and open them in ArangoDB Visualizer for graph exploration
4. Review `riskReasons` to understand why an entity is flagged"

**Transition:** "Now let's shift to the executive view — same data, different lens."

---

## Part 2: Executive Lens (2-3 minutes)

### Navigate to Executive Tab

**In the Streamlit app:** Click "Executive" tab

### Executive Dashboard

**What it shows:** Aggregate risk by district (geographic aggregation)

**Query explanation:**
- Aggregates Person risk scores by their residential district (via `residesAt` → `Address.district`)
- Computes: average risk, maximum risk, and count per district
- Sorted by average risk (descending)
- Top 25 districts displayed

**Metrics to highlight:**

1. **`district`**: Geographic region
2. **`avgRisk`**: Average risk score across all persons in that district
3. **`maxRisk`**: Highest individual risk score in the district
4. **`count`**: Number of persons in the district

**Narrative:** "Executives need to understand risk at scale. This view aggregates individual risk scores by geography, revealing hotspots. A district with high average risk might indicate:
- Concentrated fraud networks
- Weak KYC enforcement in that region
- Targeted fraud campaigns

Notice how we're using the same underlying risk scores (`riskScore` field) but presenting them in an aggregated, actionable format."

### Executive Insights

**Key talking points:**

1. **Risk Concentration:** "Districts with high `avgRisk` and high `count` represent significant exposure. These are priority areas for compliance teams."

2. **Maximum Risk:** "Even if average risk is moderate, a high `maxRisk` indicates at least one very risky individual in that district — worth investigating."

3. **Actionable Intelligence:** "This view helps executives:
   - Allocate compliance resources geographically
   - Identify regions needing enhanced due diligence
   - Track risk trends over time (if run periodically)"

**Example narrative:** "If District X shows `avgRisk: 75` with `count: 150`, that's 150 people with an average risk score of 75 — a significant concentration. The executive can then drill down: 'Show me the top 10 highest-risk individuals in District X' using the Analyst lens."

---

## Conclusion (30 seconds)

**Summary points:**

1. **Analyst Lens:** Pattern detection, risk scoring with three signals (direct, inferred, path), and investigative workflows
2. **Executive Lens:** Geographic risk aggregation for strategic decision-making
3. **Unified Data Model:** Both lenses use the same underlying graph and risk scores — different views, same truth

**Next steps:**
- For deeper investigation: Use ArangoDB Visualizer with KnowledgeGraph theme
- For custom analytics: Run `scripts/phase3_analytics.py` and extend queries
- For risk tuning: Adjust decay factors and thresholds in `scripts/phase3_risk.py`

**Closing:** "This demonstrates how graph-based risk intelligence scales from individual investigation to executive dashboards, all powered by the same fraud detection patterns and risk algorithms."

---

## Appendix: Quick Reference

### Commands

```bash
# Run full Phase 3 validation
python scripts/test_phase3.py --remote-only

# Generate analytics report only
python scripts/phase3_analytics.py --mode REMOTE

# Compute risk scores only
python scripts/phase3_risk.py --mode REMOTE

# Launch demo app
streamlit run apps/phase3_demo_app.py
```

### Key Files

- **Analytics Report:** `docs/phase3-analytics-report.md`
- **Validation Report:** `docs/phase3-validation-report.md`
- **Demo App:** `apps/phase3_demo_app.py`
- **Risk Script:** `scripts/phase3_risk.py`
- **Analytics Script:** `scripts/phase3_analytics.py`

### Risk Field Reference

| Field | Description | Example Values |
|-------|-------------|----------------|
| `riskDirect` | Direct evidence risk (0-100) | 95 (mule hub), 85 (cycle participant), 70 (undervalued property) |
| `riskInferred` | Neighbor-propagated risk (0-100) | 64 (connected to high-risk org), 48 (associated with risky person) |
| `riskPath` | Transaction-path risk (0-100) | 50 (2 hops from seed), 25 (3 hops from seed) |
| `riskScore` | Final score = MAX(direct, inferred, path) | 95, 64, 50 |
| `riskReasons` | Array of explanation strings | `["mule_hub_inbound>=50"]`, `["circular_trading_cycle_participant"]` |

### Fraud Patterns Detected

1. **Circular Trading:** Round-trip transfers (`transferredTo.scenario == "cycle"`)
2. **Money Mule Rings:** Hub-and-spoke structures (`transferredTo.scenario == "mule"`)
3. **Undervalued Properties:** Sales at or below circle rate (`transactionValue <= circleRateValue`)
4. **Entity Resolution:** Duplicate identity consolidation (`resolvedTo` → `GoldenRecord`)
