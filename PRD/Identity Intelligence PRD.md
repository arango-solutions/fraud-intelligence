This Product Requirements Document (PRD) details the specifications for **Subsystem 2: Identity Intelligence**, designed to detect "Benami" (proxy) accounts and consolidate duplicate identities using the `arango-entity-resolution` library and ArangoDB’s Graph Analytics Engine (GAE).

---

# PRD: Subsystem 2 - Identity Intelligence (Entity Resolution)

| Document Details |  |
| --- | --- |
| **Subsystem Name** | Identity Intelligence & Resolution Engine |
| **Parent Project** | SBI "Antigravity" Fraud Defense Demo |
| **Status** | Draft |
| **Primary Tech Stack** | `arango-entity-resolution`, ArangoDB GAE (WCC) |

---

## 1. Executive Summary

The Identity Intelligence subsystem serves as the "Clean-Up" layer of the fraud detection pipeline. Its primary goal is to defeat **Identity Fragmentation**—a tactic where fraudsters disperse activity across multiple accounts with slight name variations (e.g., "Rajesh Kumar" vs. "R. Kumar") or use "Mule" accounts that share hidden attributes (devices, addresses).

This system will ingest raw customer data, identify non-obvious links, and collapse these disparate nodes into a single **"Golden Record" (Canonical Identity)**.

---

## 2. Core Functional Requirements

### 2.1 Phonetic & Fuzzy Name Matching ("The Benami Filter")

To catch "Benami" holders who use name variations to evade "One Person, One Account" rules.

* **Requirement:** The system must identify candidates based on phonetic similarity, not just exact string matching.
* **Target Variations:**
* Phonetic: "Brijesh" ↔ "Vrijesh" (Common in Hindi/regional transliteration).
* Abbreviation: "S. K. Gupta" ↔ "Sunil Kumar Gupta".
* Reordering: "Ahmed Khan" ↔ "Khan Ahmed".


* **Technical Implementation:**
* **Tool:** ArangoSearch (via `arango-entity-resolution` Blocking Services).
* **Strategy:** Use `BM25BlockingStrategy` configured with a custom ArangoSearch Analyzer.
* **Configuration:**
* **Analyzer:** `text_en` with `soundex` or `metaphone` stemming enabled to handle Indian name Anglicization.





### 2.2 Multi-Attribute Linkage ("The Mule Catcher")

To detect rings of accounts that appear unrelated by name but share backend infrastructure.

* **Requirement:** Link entities that share **non-obvious** attributes.
* **Critical Attributes:**
* `device_id` / `mac_address` (Digital fingerprint).
* `phone_number` (Often shared among family mule rings).
* `email_address` (Fuzzy match on username part).


* **Technical Implementation:**
* **Strategy:** `GraphTraversalBlockingStrategy`.
* **Logic:** Traverse `(Person)-[has_digital_location]->(DigitalLocation)<-[has_digital_location]-(Person)` to find candidates who share a device ID / fingerprint.



### 2.3 Semantic Similarity ("The Alias Detector")

To find identities that are contextually similar based on unstructured data.

* **Requirement:** Match entities based on vector embeddings of their full profile (Name + Address + Risk Notes).
* **Technical Implementation:**
* **Tool:** `VectorBlockingStrategy`.
* **Process:** Generate embeddings for `Person` nodes. Perform Approximate Nearest Neighbor (ANN) search to find profiles that cluster together in vector space, catching aliases that avoid rule-based detection.



---

## 3. Architecture & Components

The subsystem will implement the pipeline pattern defined in `arango-entity-resolution/src/entity_resolution/core/configurable_pipeline.py`.

### 3.1 Component 1: The Blocking Service (Candidate Generation)

* **Role:** Quickly reduce the search space from millions of pairs to likely matches.
* **Configuration:**
* **Primary Blocker:** `HybridBlockingStrategy` combining:
1. **Attribute Block:** Exact match on `pan_number` (High confidence).
2. **Phonetic Block:** ArangoSearch on `name` (Medium confidence).
3. **Vector Block:** Embedding similarity > 0.9 (Discovery mode).





### 3.2 Component 2: The Similarity Service (Pairwise Scoring)

* **Role:** Compare candidate pairs in detail to calculate a final `match_probability` (0.0 - 1.0).
* **Algorithm:** `WeightedFieldSimilarity`.
* **Weights Strategy (Indian Banking Context):**
* `pan_number`: 0.95 (Near certain match).
* `phone_number`: 0.60 (Could be family).
* `name` (Jaro-Winkler): 0.40 (High variance expected).
* `address`: 0.50 (Often non-standardized in India).


* **Threshold:** Pairs with score > 0.85 are flagged as "Matches".

### 3.3 Component 3: Entity Clustering (Graph Analytics Engine)

* **Role:** Take the pairwise matches and resolve them into distinct entity clusters.
* **Requirement:** This **MUST** use ArangoDB's **Weakly Connected Components (WCC)** algorithm for scale.
* **Implementation:**
1. Create a temporary graph `MatchGraph` where edges represent high-confidence matches.
2. Execute **WCC** via `GAEOrchestrator` (from `graph-analytics-ai-platform`).
3. Each resulting "Component" is a unique real-world identity.



### 3.4 Component 4: Golden Record Publication

* **Role:** Create a new node representing the resolved identity.
* **Action:**
* Create a `GoldenRecord` vertex.
* Link original `Person` nodes to `GoldenRecord` via `resolved_to` edges.
* Aggregate risk scores: `GoldenRecord.risk_score = MAX(Person.risk_score)`.



---

## 4. Integration Specifications

### 4.1 Interface with Subsystem 3 (Analytics Engine)

* **Input:** Raw `Person` + `BankAccount` data (plus `transferred_to` edges / transaction events).
* **Output:** A "Resolved Graph" where transactions are essentially re-routed to the `GoldenRecord`.
* **Benefit:** The "Circular Trading" detection algorithms (Subsystem 3) will run on the `GoldenRecord` nodes, making them immune to fraudsters splitting money across 5 aliases.

### 4.2 Configuration File (`er_config.yaml`)

We will use a specialized configuration for the demo:

```yaml
entity_resolution:
  blocking:
    strategies:
      - type: "hybrid"
        components:
          - type: "bm25"
            fields: ["name"]
            analyzer: "text_en_soundex" # Custom analyzer for phonetic
          - type: "graph_traversal"
            graph: "banking_graph"
            path: "HAS_PHONE, INBOUND HAS_PHONE" # Shared phone lookup
  similarity:
    method: "weighted"
    threshold: 0.85
    weights:
      name: 0.3
      address: 0.2
      pan_number: 0.5
  clustering:
    method: "wcc" # Uses Graph Analytics Engine

```

---

## 5. Success Metrics for Demo

1. **The "Ah-ha" Visualization:**
* Show a "Before" graph with 3 disconnected nodes: "R. Kumar", "Rajesh K.", "Rajesh Kumar".
* Show the "After" graph where they collapse into one node, revealing a hidden connection to a Blacklisted entity.


2. **Performance:**
* Entity Resolution on the demo dataset (10k nodes) must complete in **< 10 seconds** using the WCC algorithm.


3. **Accuracy:**
* Must successfully link "Amitabh Bachchan" and "A. Bachchan" if they share an address.
* Must **NOT** link "Amitabh Bachchan" and "Abhishek Bachchan" (different people, same address) unless they share financial identifiers (PAN).