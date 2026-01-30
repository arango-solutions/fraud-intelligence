This is an expanded and detailed update for **Sections 3 and 4** of the Data Generator PRD. It incorporates the specific "Indian Context" requirements, the `arango-entity-resolution` codebase capabilities, and the "Three Lenses" visualization strategy.

---

## 3. Data Strategy & Requirements

### 3.1 Data Source Decision: **Custom "Antigravity" Data Generator**

**Decision:** We will build a custom generator extending the `arango-entity-resolution` demo script.
**Rationale:** Public datasets (Kaggle/synthetic-fraud) lack the specific structural complexity required to demonstrate *graph* algorithms (e.g., closed loops for circular trading) and the cultural context required for the SBI demo (e.g., Indian naming conventions, "Circle Rate" vs. "Market Value").

### 3.2 Detailed Data Specifications

The generator must produce a cohesive "Digital Twin" of a regional banking ecosystem (e.g., "Mumbai Metro Region").

#### **A. Entity Specifications (Vertex Collections)**

1. **`Person` (Customer)**
* **Source Logic:** Use `Faker('en_IN')` to generate culturally accurate names (e.g., "Amitabh", "Priya", "Rajesh") rather than US-centric names found in the base script.
* **Key Attributes:**
* `name`: Full name.
* `pan_number`: Regex `[A-Z]{5}[0-9]{4}[A-Z]{1}` (Critical for Entity Resolution).
* `aadhaar_masked`: `XXXX-XXXX-1234`.
* `risk_score`: Initial seed score (0-100).


* **Benami Logic:** Generate 3 variations for 5% of customers to test Entity Resolution:
* *Variation 1:* "Rajesh Kumar" (Complete profile).
* *Variation 2:* "R. Kumar" (Missing PAN, same phone).
* *Variation 3:* "Rajesh K." (Different address, same email).




2. **`BankAccount` (Financial Instrument)**
* **Types:** `Savings`, `Current`, `NRE` (Non-Resident External - for Hawala scenarios).
* **Attributes:** `account_number`, `balance`, `avg_monthly_balance`.


3. **`RealProperty` (The Fraud Asset)**
* **Attributes:**
* `survey_number`: Unique land ID.
* `district`: e.g., "Mumbai_South", "Thane_West".
* `circle_rate_value`: The government-mandated minimum value (e.g., ₹50,000/sqft).
* `market_value`: The actual generated transaction price.
* **Fraud Trigger:** For 2% of properties, generate `market_value` == `circle_rate_value` (undervalued) while linking to a "Cash Payment" side-channel.




4. **`WatchlistEntity` (Risk Seeds)**
* **Source:** Synthetic list simulating RBI/OFAC defaulters.
* **Attributes:** `name`, `listing_reason` ("Wilful Defaulter", "Shell Company Director").



#### **B. Topology & Relationship Specifications (Edge Collections)**

The generator must inject specific graph shapes into the random background noise ("Cruft").

1. **Background Noise (Normal Behavior)**
* **Pattern:** Random, star-shaped, or small tree structures.
* **Volume:** 90-95% of total graph.
* **Logic:** `Person` -> `has_account` -> `BankAccount` -> `transferred_to` -> `UtilityCompany` / `Retailer`.


2. **Fraud Scenario 1: Circular Trading (The "Round Trip")**
* **Pattern:** Closed Loop (Cycle).
* **Logic:** `Entity A` -> `Entity B` -> `Entity C` -> `Entity D` -> `Entity A`.
* **Constraint:** The sum of transfers in the loop must be > ₹1 Crore.
* **Algorithm Target:** Strongly Connected Components (SCC) & Cycle Detection.


3. **Fraud Scenario 2: Money Mule Ring (The "Smurf")**
* **Pattern:** Hub-and-Spoke (Inverted).
* **Logic:** * 50 small `Mule BankAccounts` (low balance) receive small credits.
* All 50 transfer to 1 central `Aggregator BankAccount` within 24 hours.


* **Shared Attribute:** All 50 Mules share the same `device_id` or `ip_address` edge.
* **Algorithm Target:** Weakly Connected Components (WCC) on Device edges.



#### **C. Unstructured Data Generation (GraphRAG Support)**

The generator must create text artifacts that "explain" the graph anomalies.

* **Property Deeds (PDF/Text):**
* *Template:* "Sale Deed for Property {survey_number} sold to {buyer_name} for ₹{amount}."
* *Fraud Injection:* If the property is involved in a Circular Fraud, the text should mention "Cash component paid separately" or match the low `circle_rate_value`.


* **News Articles:**
* *Template:* "Market rumors suggest {company_name} is involved in {fraud_type}."
* *Linkage:* The `{company_name}` must match a node in the graph, enabling the AI to connect external news to internal transactional risk.



### 3.3 Volume Requirements

* **Scale:** Small enough for instant demo response, large enough to be visually impressive.
* **Nodes:** ~10,000 (8k Persons, 1.5k BankAccounts, 500 RealProperties).
* **Edges:** ~50,000 (Transactions + Relationships).


* **Cruft Ratio:** 1 Fraud Case : 50 Normal Cases. This ensures the demo shows the platform *filtering* noise, not just showing a graph made entirely of fraud.

---

## 4. Visualization & User Experience (UX) Requirements

The demo interface (likely a Streamlit or React app wrapping the platform) must present the data through three distinct "Lenses," telling a progressive story of discovery.

### 4.1 Lens 1: The "Investigator" View (Graph Explorer)

* **Target User:** Fraud Analyst digging into a specific case.
* **Visualization Requirement:** **Network Graph (Force-Directed Layout)**.
* **Key Features:**
* **Entity Resolution Toggle:** A switch to toggle between "Raw Data" (messy, disconnected) and "Resolved Data" (collapsed Golden Records).
* *Demo Moment:* Toggling "On" reveals that 5 seemingly small accounts actually belong to one person ("Benami").


* **GraphRAG Explainer Sidebar:** When a node is clicked, display the *source evidence*.
* *Visual:* Highlight the path `Buyer` -> `Seller` and show the generated "Property Deed" text alongside it.





### 4.2 Lens 2: The "Analyst" View (Interactive Reports)

* **Target User:** Data Scientist validating the model.
* **Visualization Requirement:** **Interactive Charts (Plotly)** embedded in HTML reports.
* **Specific Charts:**
* **PageRank Distribution (Bar Chart):** Show the top 10 influencers. The "Hawala Broker" should be an outlier with a huge score despite low declared income.
* **Community Size Histogram (Log Scale):** Show the distribution of component sizes from WCC. The "Mule Rings" will appear as distinct anomalies (clusters of 50-100 nodes) compared to the typical family size (3-5 nodes).



### 4.3 Lens 3: The "Executive" View (Risk Heatmap)

* **Target User:** CRO/Risk Head monitoring systemic threat.
* **Visualization Requirement:** **Geospatial Map (Deck.gl / Leaflet)**.
* **Data Support:** The generator *must* populate `lat`/`long` attributes for `Address` nodes, clustered in specific districts (e.g., "Andheri East").
* **Visual Logic:**
* aggregate `risk_score` by District.
* Color code regions: Green (Low Risk) to Red (High Risk).
* *Demo Moment:* The map shows a "Hotspot" in one specific district where the generator injected the "Circular Real Estate" ring, identifying a systemic geographical vulnerability.