This Product Requirements Document (PRD) outlines the comprehensive plan for implementing the **Fraud Intelligence Demo** using ArangoDB and graph analytics.

This plan integrates the **Agentic Workflow**, **Entity Resolution**, and **Risk Intelligence** capabilities discussed in our conversation.

---

# Product Requirements Document (PRD): Fraud Intelligence Demo

| Document Details |  |
| --- | --- |
| **Project Name** | Fraud Intelligence Demo |
| **Version** | 1.0 (Draft) |
| **Target Audience** | Indian Bank Risk & Compliance Executives |
| **Core Objective** | Demonstrate how an Agentic AI Graph platform can autonomously detect, analyze, and predict sophisticated financial fraud (Circular Trading, Benami, Hawala). |

---

## 1. Executive Summary

The demo will showcase a "Future State" of fraud detection for banking. Moving beyond static rules, it will demonstrate an **Autonomous AI Agent** that ingests unstructured data (news, deeds), resolves hidden identities (Entity Resolution), analyzes network patterns (Graph Algorithms), and propagates risk scores (Risk Intelligence) to flag complex schemes like "Circular Real Estate Trading" and "Money Mule Rings."

---

## 2. System Architecture & Subsystems

The solution will be composed of five integrated subsystems.

### 2.1 Subsystem 1: Knowledge Ingestion (GraphRAG & Semantics)

* **Role:** Convert unstructured text into structured graph data.
* **Requirement:** Must process PDF/Text documents (e.g., Property Deeds, Regulatory Watchlists).
* **Semantic Driver:** **YES, Semantic Approach is Required.**
* **Recommendation:** Adopt the **Arango-RDF** approach used in `risk-management`.
* **Why:** Fraud concepts like "Associate," "Shell Company," and "Ultimate Beneficial Owner" need a strict ontology to map diverse terms from documents into a unified graph structure. This allows the AI to infer that a "cousin" listed in a deed is a "Related Party."



### 2.2 Subsystem 2: Identity Intelligence (Entity Resolution)

* **Role:** Collapse "Benami" (proxy) accounts into single identities.
* **Requirement:** Detect customers with:
* Phonetic name variations (e.g., "Brijesh Kumar" vs "Vrijesh Kumar").
* Shared non-obvious attributes (Phone, Email, IP Address).


* **Tech Stack:** `arango-entity-resolution` library using Hybrid Blocking (Text + Vector).

### 2.3 Subsystem 3: Analytics Engine (Graph Analytics AI Platform)

* **Role:** The "Brain" that orchestrates analysis.
* **Requirement:** **Agentic Workflow**.
* **Inputs:** Natural language questions (e.g., "Find circular payments in the Mumbai Real Estate sector").
* **Actions:** Autonomous selection of algorithms (PageRank, WCC, Cycle Detection).
* **Outputs:** Intelligence Reports with confidence scores.



### 2.4 Subsystem 4: Risk Intelligence (Scoring & Propagation)

* **Role:** Quantify and predict threat levels.
* **Requirement:** Calculate three distinct risk metrics:
* **Direct Risk:** Based on list hits (e.g., name matches a watchlist).
* **Inferred Risk:** "Guilt by association" (connected to a fraudster).
* **Path Risk:** Risk derived from transaction flows (Money Mule -> BankAccount -> You).

### 2.5 Subsystem 5: Visualization & User Experience (UX)

* **Role:** Tell the demo story for three personas (Investigator, Analyst, Executive).
* **Requirement:** Must provide the **three “Lenses”** experience, including evidence paths and “Before/After” Entity Resolution.
* **Reference:** See **Section 4** and `PRD/Visualization & User Experience PRD.md`.

### 2.6 Canonical schema + naming (source of truth)

All PRDs under `PRD/` are expansions of this document and must use the naming below. If a PRD uses an alias (e.g., “Customer”), it must map to the canonical name here.

#### 2.6.1 Naming conventions

* **Vertex collections (Classes):** PascalCase (e.g., `Person`, `BankAccount`) matching OWL Class names.
* **Edge collections (ObjectProperties):** camelCase (e.g., `hasAccount`, `transferredTo`) matching OWL ObjectProperty names.
* **Document fields (DatatypeProperties):** camelCase (e.g., `riskScore`, `circleRateValue`) matching OWL DatatypeProperty names.
* **Arango system fields:** `_key`, `_from`, `_to` remain unchanged.

#### 2.6.2 Canonical vertex collections (entities)

| Canonical name | Aliases used in PRDs | Description / notes |
| --- | --- | --- |
| `Person` | Customer, user | Bank customer / individual identity. |
| `Organization` | Company, Shell Company | Legal entity (incl. shell/legit). |
| `WatchlistEntity` | Watchlist | Regulatory/sanctions/defaulter list entry (seed risk). |
| `BankAccount` | Account | Bank account / instrument. |
| `RealProperty` | Property | Real estate asset (has circle/market value). |
| `Address` | Location | Physical address (may include `district`, `state`, `pincode`, plus optional `lat`, `long`). |
| `DigitalLocation` | Device, IP, fingerprint | Digital footprint (may include `ipAddress`, `deviceId`, `macAddress`). Can be modeled as vertices to support ER blocking/traversal. |
| `Transaction` | Transfer | Generic money movement event. |
| `RealEstateTransaction` | Sale | Property sale/purchase event. |
| `Document` | Evidence, Deed, Article | Unstructured source record; specialized types include `TitleDeed`, `NewsArticle`, `KYCRecord`. |
| `GoldenRecord` | Canonical Identity | Resolved identity produced by Entity Resolution. |

#### 2.6.3 Canonical edge collections (relationships)

| Edge collection | From → To | Purpose |
| --- | --- | --- |
| `hasAccount` | `Person/Organization` → `BankAccount` | Ownership / control of funds. |
| `transferredTo` | `BankAccount` → `BankAccount` | Money movement (edge carries `amount`, `timestamp`, `txnType`). |
| `relatedTo` | `Person` ↔ `Person` | Familial/social ties (edge may carry `relationType`). |
| `associatedWith` | `Person` → `Organization` | Directors/partners/UBOs. |
| `residesAt` | `Person` → `Address` | Home address. |
| `accessedFrom` | `BankAccount` → `DigitalLocation` | Login/transaction IP/device. |
| `hasDigitalLocation` | `Person` → `DigitalLocation` | Optional direct link for ER blocking (shared device/IP). |
| `mentionedIn` | `Person/Organization/RealProperty/BankAccount` → `Document` | GraphRAG link between graph + evidence text. |
| `registeredSale` | `RealProperty` → `RealEstateTransaction` | Link property to a sale event. |
| `buyerIn` | `Person/Organization` → `RealEstateTransaction` | Buying party. |
| `sellerIn` | `Person/Organization` → `RealEstateTransaction` | Selling party. |
| `resolvedTo` | `Person` → `GoldenRecord` | Identity resolution link (many persons → one golden record). |

#### 2.6.4 Canonical risk fields (stored in ArangoDB)

| Canonical field | Type | Meaning |
| --- | --- | --- |
| `riskScore` | number (0-100) | Final operational risk score. |
| `riskDirect` | number (0-100) | Direct risk from watchlists/static rules. |
| `riskInferred` | number (0-100) | Risk derived from neighbors/associations. |
| `riskPath` | number (0-100) | Risk derived from fund flow distance / taint. |
| `riskReasons` | array[string] | Human-readable explanations for audit/UI. |

#### 2.6.5 Canonical “circle rate” fields (real estate)

* `circleRateValue`: government minimum value reference (per unit or total, but must be consistent across the dataset)
* `marketValue`: estimated/actual market value
* `transactionValue`: value recorded on the `RealEstateTransaction` (sale price)

---

## 3. Data Strategy & Requirements

### 3.1 Data Source Decision: **Custom Data Generator**

Open datasets (like Kaggle fraud data) lack the specific "Indian Context" and structural complexity (circular loops, circle rate data) required for this impactful demo.

* **Requirement:** Build a custom generator using the `arango-entity-resolution/demo/scripts/data_generator.py` as a base.
* **Data Specifications:**
* **Entities:** `Person`, `BankAccount`, `RealProperty`, `Organization` (Shell/Legit).
* **Attributes:** Names, PAN formats, Addresses (Indian format), "Circle Rate" vs "Market Value" for properties.
* **Topology:**
* *Normal:* Random, disconnected or star-shaped.
* *Fraud (Circular):* Closed loops (A->B->C->A) involving large sums.
* *Fraud (Mule):* Hub-and-spoke (Many small -> One Aggregator).





### 3.2 Volume Requirements

* **Demo Scale:** ~10,000 Nodes / ~50,000 Edges. Small enough for snappy real-time demos, complex enough to show "finding a needle in a haystack."

---

## 4. Visualization & User Experience (UX)

The demo must tell a story through three distinct "Lenses":

### 4.1 The "Investigator" View (Graph Explorer)

* **Goal:** Visual confirmation of fraud.
* **Feature:** **GraphRAG Explainer**.
* Clicking a flagged node displays the "Evidence Path" and cites the source document (e.g., "Flagged due to link with Watchlist ID #123 found in 'ED_Report_2025.pdf'").


* **Feature:** **Entity Resolution Toggle**. Show the graph "Before" (messy, disconnected) and "After" (consolidated, revealing the fraud ring).

### 4.2 The "Analyst" View (Interactive Reports)

* **Goal:** Technical validation.
* **Feature:** **Plotly Charts** embedded in HTML reports.
* *Chart 1:* Distribution of "Influence Scores" (PageRank) identifying Mule Hubs.
* *Chart 2:* Component Size histogram (WCC) showing isolated fraud communities.



### 4.3 The "Executive" View (Risk Heatmap)

* **Goal:** Strategic oversight.
* **Feature:** Geospatial/Risk Heatmap.
* Overlay risk scores on a map of India.
* Visual alert: "High concentration of undervalued property transactions detected in [Specific District]."



---

## 5. Functional Requirements Checklist

### Phase 1: Data & Schema (Setup)

* [ ] **Ontology Design:** Create/adapt `fraud-intelligence.owl` to include `RealEstateTransaction`, `UndervaluedTransaction`, and `BenamiTransaction` (plus real-estate fields like `circle_rate_value`).
* [ ] **Generator Update:** Modify `data_generator.py` to produce "Circular Loops" and "Undervalued Asset" patterns.
* [ ] **Ingestion Pipeline:** Script to load generated data into ArangoDB.

### Phase 2: Intelligence Layer (Implementation)

* [ ] **ER Configuration:** Tune `arango-entity-resolution` config to catch phonetic Indian name matches.
* [ ] **Risk Logic:** Implement `calculate_inferred_risk.py` logic to propagate risk from "Watchlist" nodes to "Neighbors."
* [ ] **Agent Configuration:** Configure `graph-analytics-ai` agents with descriptions of the new schema elements.

### Phase 3: Demo Interface (Visualization)

* [ ] **AQL Queries:** Write Geo+Vector+Text queries (e.g., "Find properties < 50% circle rate within 5km of high-risk node").
* [ ] **Report Template:** Create a custom Report Template in the AI platform that focuses on "AML & Regulatory Compliance."

---

## 6. Success Metrics for Demo

1. **Speed:** The "Agentic Workflow" must generate a report from a text prompt in **< 2 minutes** (using Parallel execution).
2. **Clarity:** The "Before vs. After" ER visualization must elicit a "Wow" moment (visual simplification of complexity).
3. **Relevance:** The Report must specifically mention "Circle Rates" and "Benami Transactions" automatically, proving the AI understands the context.