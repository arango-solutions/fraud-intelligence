This Product Requirements Document (PRD) defines the **"Antigravity SBI Financial Crime Ontology"**. This ontology will serve as the semantic backbone for the generated data, the knowledge graph schema, and the fraud taxonomy for the State Bank of India (SBI) demo.

It is designed specifically to be ingested by **ArangoRDF** to automatically generate the physical ArangoDB graph schema (Vertex and Edge collections).

---

# PRD: Antigravity SBI Financial Crime Ontology

| Document Details |  |
| --- | --- |
| **Ontology Name** | `sbi-antigravity.owl` |
| **Base URI** | `http://www.semanticweb.org/sbi-antigravity#` |
| **Format** | RDF/XML (OWL 2 DL) |
| **Target Consumer** | ArangoRDF (Schema Generation), GraphRAG (Concept Mapping) |

---

## 1. Executive Summary

The ontology provides a semantic layer that bridges the gap between raw data (transactions, deeds) and high-level fraud concepts (Benami, Hawala). It defines the "Ground Truth" structure for the synthetic data generator and enables the AI agents to reason about "hidden connections" by classifying specific graph patterns as instances of specific fraud types.

## 2. Design Principles for ArangoRDF Compatibility

To ensure seamless translation into ArangoDB via ArangoRDF, the ontology adheres to these rules:

1. **Classes = Collections:** Top-level OWL Classes (e.g., `Person`, `Transaction`) will map to ArangoDB Vertex Collections.
2. **Object Properties = Edge Collections:** Properties connecting two classes (e.g., `transferred_to`) will map to ArangoDB Edge Collections.
3. **Datatype Properties = Document Attributes:** Properties with literal values (e.g., `amount`, `circle_rate`) will map to fields within ArangoDB documents.
4. **Taxonomy = Inferred Types:** The fraud hierarchy allows the AI to classify a node as a generic `RiskEvent` or a specific `HawalaTransaction`.

---

## 3. Core Class Structure (Vertex Collections)

The ontology extends the `sentries_ontology.owl` to include banking and real estate domains.

### 3.1 Legal Entities (The "Who")

* **`LegalEntity`** (Superclass)
* **`Person`**: Individuals (Source: `Faker('en_IN')`).
* *Attributes:* `pan_number`, `aadhaar_masked`, `risk_score`.


* **`Organization`**: Companies, Trusts, Shell Entities.
* *Attributes:* `gstin`, `incorporation_date`, `industry_code`.


* **`WatchlistEntity`**: Entities explicitly listed on regulatory lists (OFAC, RBI).



### 3.2 Financial Instruments (The "How")

* **`FinancialInstrument`**
* **`BankAccount`**: Savings, Current, NRE/NRO accounts.
* *Attributes:* `account_number`, `balance`, `open_date`.


* **`DigitalWallet`**: UPI IDs, E-wallets.



### 3.3 Assets & Geography (The "What" & "Where")

* **`Asset`**
* **`RealProperty`**: Land, Apartments, Commercial Buildings.
* *Attributes:* `survey_number`, `circle_rate_value`, `market_value`, `geo_location`.




* **`Location`**
* **`Address`**: Physical locations.
* *Attributes:* `street`, `district`, `state`, `pincode`.


* **`DigitalLocation`**: Metadata for tracking.
* *Attributes:* `ip_address`, `device_id`, `mac_address`.





### 3.4 Events & Documents (The "When" & "Evidence")

* **`Event`**
* **`Transaction`**: Generic money movement.
* **`RealEstateTransaction`**: Sale/Purchase of property.


* **`Document`**: Unstructured data sources.
* **`TitleDeed`**: Property ownership proof.
* **`KYCRecord`**: Identity proof.
* **`NewsArticle`**: External risk signals.



---

## 4. Fraud Taxonomy (The "Why")

This section defines the hierarchical classification of financial crimes, enabling the Reporting Agent to tag specific sub-graphs with semantic labels.

* **`FinancialCrime`**
* **`MoneyLaundering`**
* **`Smurfing`**: High-frequency low-value credits followed by aggregation.
* **`Placement`**: Cash deposits into the system.
* **`Layering`**: Complex web of transfers to hide origin.


* **`TaxEvasion`**
* **`UndervaluedTransaction`**: Transaction `amount` < `circle_rate_value` * tolerance.
* **`BenamiTransaction`**: Property held by a proxy (`Person`) for a beneficial owner.


* **`InformalValueTransfer`**
* **`Hawala`**: Transfer without physical money movement (net settlement).


* **`InsiderThreat`**
* **`CollusiveApproval`**: Loan approved by an employee related to the borrower.





---

## 5. Object Properties (Edge Definitions)

These define the valid relationships in the graph. `ArangoRDF` will convert these into Edge Collections.

| Property URI | Domain (From) | Range (To) | Description |
| --- | --- | --- | --- |
| **`has_account`** | `LegalEntity` | `BankAccount` | Ownership of funds. |
| **`transferred_to`** | `BankAccount` | `BankAccount` | Money movement (edges carry `amount`, `timestamp`). |
| **`related_to`** | `Person` | `Person` | Familial/Social ties (Symmetric). |
| **`associated_with`** | `Person` | `Organization` | Directors, Partners, UBOs. |
| **`resides_at`** | `Person` | `Address` | Home address. |
| **`accessed_from`** | `BankAccount` | `DigitalLocation` | Login/Transaction IP or Device. |
| **`registered_sale`** | `RealProperty` | `RealEstateTransaction` | Link property to the sale event. |
| **`buyer_in`** | `LegalEntity` | `RealEstateTransaction` | Party buying. |
| **`seller_in`** | `LegalEntity` | `RealEstateTransaction` | Party selling. |
| **`mentioned_in`** | `LegalEntity` | `Document` | GraphRAG link between graph & text. |

---

## 6. Datatype Properties (Attributes)

Attributes specific to the SBI/Indian context needed for the demo algorithms.

| Property URI | Domain | Type | Notes |
| --- | --- | --- | --- |
| **`riskScore`** | `Entity` | `xsd:decimal` | 0-100 aggregated risk. |
| **`inferredRisk`** | `Entity` | `xsd:decimal` | Risk derived from neighbors. |
| **`circleRate`** | `RealProperty` | `xsd:decimal` | Gov minimum value per sq ft. |
| **`marketValue`** | `RealProperty` | `xsd:decimal` | Actual estimated value. |
| **`transactionType`** | `Transaction` | `xsd:string` | NEFT, RTGS, UPI, IMPS. |
| **`isBenamiSuspect`** | `RealProperty` | `xsd:boolean` | Flag for investigation. |

---

## 7. Implementation Strategy

### 7.1 Integration with Data Generator

The data generator ("Antigravity Data Fabric") must produce CSV/JSON files that align with these class names.

* *Generator:* Creates `customers.csv` -> *Ontology:* Maps to `sbi:Person`.
* *Generator:* Creates `deeds.json` -> *Ontology:* Maps to `sbi:TitleDeed`.

### 7.2 Integration with Graph Analytics

The Agentic Workflow will use this ontology to select algorithms:

* *Query:* "Find **BenamiTransactions**"
* *Agent Logic:* Look up `BenamiTransaction` in ontology -> See it involves `RealProperty`, `buyer_in`, and `related_to` edges -> Select **PageRank** (to find controller) or **WCC** (to find the hidden family ring).

### 7.3 Success Criteria

1. **Valid Import:** `arango-rdf` CLI tool successfully imports the `.owl` file and creates the collection structure in ArangoDB without errors.
2. **Queryability:** An AQL query can successfully traverse `Person -> related_to -> Person -> buyer_in -> RealEstateTransaction` using the generated edge definitions.
3. **Classification:** The demo successfully labels a node as `FraudTypology/Hawala` based on the ontological definition.