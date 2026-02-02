This Product Requirements Document (PRD) defines **Subsystem 4: Risk Intelligence**, the scoring engine responsible for quantifying financial threat levels in the Fraud Intelligence Demo. It aggregates insights from the Schema, Entity Resolution, and Graph Analytics subsystems into concrete, numerical risk scores.

---

# PRD: Subsystem 4 - Risk Intelligence (Scoring & Propagation)

| Document Details |  |
| --- | --- |
| **Subsystem Name** | Risk Intelligence Engine |
| **Parent Project** | Fraud Intelligence Demo |
| **Status** | Draft |
| **Primary Tech Stack** | ArangoDB AQL, NetworkX (prototype), `risk-management` scripts |

---

## 1. Executive Summary

The Risk Intelligence subsystem is the "Quantifier" of the platform. While Subsystem 3 (Analytics) identifies *patterns* (e.g., "This is a ring"), Subsystem 4 calculates the *severity* (e.g., "Risk Score: 95/100").

It implements a **Multi-Layered Risk Model** that calculates risk not just based on who a customer *is* (Direct Risk), but who they *know* (Inferred Risk) and who they *transact with* (Path Risk). This allows banks to detect "Clean Skins"—proxies with perfect KYC records who are secretly acting on behalf of blacklisted entities.

---

## 2. Core Functional Requirements

### 2.1 Direct Risk Calculation (" The Watchlist Hit")

To flag entities that explicitly appear on regulatory bad lists or violate static rules.

* **Input:** `Person` vertices with attributes matching `WatchlistEntity` entries.
* **Logic Source:** `scripts/calculate_direct_risk.py`.
* **Rules:**
1. **Sanction Match:** If `Name` + `DOB` fuzzy matches a `WatchlistEntity` -> Risk = 100.
2. **KYC Failure:** If `kyc_status` == "Failed" -> Risk = 90.
3. **Document Anomaly:** If linked `TitleDeed` / `RealEstateTransaction` indicates `transaction_value` < 50% of `circle_rate_value` -> Risk = 75 (Tax Evasion Flag).



### 2.2 Inferred Risk Propagation ("Guilt by Association")

To calculate risk for customers who have no direct violations but are socially connected to fraudsters.

* **Input:** Graph structure (`related_to` edges).
* **Logic Source:** `scripts/calculate_inferred_risk.py`.
* **Algorithm:** **Risk Diffusion (bounded, decayed)**.
* **Formula (demo default, 1-hop):**

\[
risk\_inferred(u)=\min\Big(100,\max_{(u \leftrightarrow v)\in N(u)}\big(risk\_score(v)\cdot decay(e)\big)\Big)
\]

Where \(decay(e)\) depends on relationship type:
* *Weights:*
* `related_to` (Family): 0.8 decay factor.
* `associated_with` (Business Partner): 0.6 decay factor.
* `shared_address` (Co-location): 0.4 decay factor.




* **Indian Banking Context:** If "Brijesh" (Clean) is the brother of "Rajesh" (Hawala Broker, Risk 90), then:
  * `risk_inferred(Brijesh) = 90 * 0.8 = 72`

### 2.3 Path-Based Risk ("The Infection Vector")

To quantify risk derived from the flow of funds, specifically aimed at Money Laundering (Layering).

* **Input:** Transaction Graph (`transferred_to` edges).
* **Logic Source:** `scripts/calculate_path_risk.py`.
* **Algorithm:** **Shortest Path to Threat**.
* Find the shortest path distance \(d(u,Threat)\) to any node with `risk_score >= 90`.
* **Formula (demo default, exponential decay):**

\[
risk\_path(u)=\min\big(100,\;100\cdot \alpha^{d(u,Threat)}\big)
\]

Where \(\alpha \in (0,1)\) is a decay factor (default \(\alpha=0.5\)).


* **Indian Banking Context:**
* **Step 1:** Mule BankAccount (Risk 100) -> **Step 2:** Layer 1 -> **Step 3:** Layer 2 -> **Step 4:** Target BankAccount.
* Target BankAccount is 3 hops away: `risk_path = 100 * 0.5^3 = 12.5` (low but non-zero "taint").



---

## 3. Architecture & Data Model

### 3.1 Ontology Alignment

The subsystem relies on the risk properties defined in `fraud-intelligence.owl`, with stored-field mappings defined in `PRD/PRD.md` (Canonical schema + naming).

| Concept | ArangoDB Property | Description |
| --- | --- | --- |
| **Total Risk** | `vertex.riskScore` | `MAX(Direct, Inferred, Path)`. The final operational score. |
| **Direct Risk** | `vertex.riskDirect` | Static rule violations. |
| **Inferred Risk** | `vertex.riskInferred` | Network exposure score. |
| **Audit Trail** | `vertex.riskReasons` | JSON array: `["Matched RBI List", "Brother of Defaulter"]`. |

### 3.2 AQL Implementation Strategy

Instead of external Python processing, the demo should leverage ArangoDB's AQL for real-time scoring.

**Example AQL for Inferred Risk:**

```aql
FOR user IN Person
  LET high_risk_neighbors = (
    FOR v, e IN 1..1 ANY user relatedTo, associatedWith
      FILTER v.riskScore > 70
      RETURN { neighbor: v._key, risk: v.riskScore, relation: e.type }
  )
  LET inferred = MAX(
    FOR n IN high_risk_neighbors 
    RETURN n.risk * (n.relation == 'family' ? 0.8 : 0.5)
  )
  UPDATE user WITH { riskInferred: inferred } IN Person

```

---

## 4. Integration Specifications

### 4.1 Input from Subsystem 2 (Entity Resolution)

* **Trigger:** Risk scoring runs *after* Entity Resolution updates the graph.
* **Requirement:** If Entity Resolution merges Node A (Risk 10) and Node B (Risk 90) into a `GoldenRecord`, the `GoldenRecord` **MUST** inherit the maximum risk (90). This prevents "Risk Dilution."

### 4.2 Output to Visualization (Heatmaps)

* **File:** `docs/sentries_risk_heatmap.json`.
* **Requirement:** The subsystem must export a JSON summary for the "Risk Heatmap" view.
* **Structure:**
```json
{
  "district": "Mumbai_South",
  "avg_risk": 78.5,
  "high_risk_count": 142,
  "primary_threat": "Benami_Real_Estate"
}

```





---

## 5. Risk Verification & Auditing

### 5.1 The "Verify" Script

* **Tool:** `scripts/verify_risk.py`.
* **Role:** A sanity check script to ensure risk logic is consistent.
* **Checklist:**
1. Ensure no node has Risk > 100 or < 0.
2. Verify that all nodes with `sanction_match=True` have Risk=100.
3. Verify that risk decays correctly over graph distance (Hop 1 > Hop 2).



---

## 6. Success Metrics for Demo

1. **The "Hidden Threat" Reveal:**
* *Scenario:* User queries a "Clean" customer who is applying for a loan.
* *Result:* System flags High Risk (85/100) solely due to `Inferred Risk` from a `related_to` edge connecting them to a Watchlist entity.


2. **Visual Impact:**
* The Risk Heatmap correctly lights up the geographic "District" where the synthetic data generator injected the fraud ring.


3. **Performance:**
* Scoring update for the 10k node demo dataset completes in **< 500ms** using AQL traversal.