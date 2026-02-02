This Product Requirements Document (PRD) defines the **"Fraud Intelligence Ontology"**. This ontology will serve as the semantic backbone for the generated data, the knowledge graph schema, and the fraud taxonomy for the fraud intelligence demo.

It is designed specifically to be ingested by **ArangoRDF** to automatically generate the physical ArangoDB graph schema (Vertex and Edge collections).

---

# PRD: Fraud Intelligence Ontology

| Document Details |  |
| --- | --- |
| **Ontology Name** | `fraud-intelligence.owl` |
| **Base URI** | `http://www.semanticweb.org/fraud-intelligence#` |
| **Format** | RDF/XML (OWL 2 DL) |
| **Target Consumer** | ArangoRDF (Schema Generation), GraphRAG (Concept Mapping) |

---

## 1. Executive Summary

The ontology provides a semantic layer that bridges the gap between raw data (transactions, deeds) and high-level fraud concepts (Benami, Hawala). It defines the "Ground Truth" structure for the synthetic data generator and enables the AI agents to reason about "hidden connections" by classifying specific graph patterns as instances of specific fraud types.

## 2. Design Principles for ArangoRDF Compatibility

To ensure seamless translation into ArangoDB via ArangoRDF, the ontology adheres to these rules:

1. **Classes = Collections:** Top-level OWL Classes (e.g., `Person`, `Transaction`) will map to ArangoDB Vertex Collections.
2. **Object Properties = Edge Collections:** Properties connecting two classes (e.g., `transferredTo`) will map to ArangoDB Edge Collections.
3. **Datatype Properties = Document Attributes:** Properties with literal values (e.g., `amount`, `circleRateValue`) will map to fields within ArangoDB documents.
4. **Taxonomy = Inferred Types:** The fraud hierarchy allows the AI to classify a node as a generic `RiskEvent` or a specific `HawalaTransaction`.

**Naming note:** For Phase 1, **ArangoDB storage names match ontology naming** (PascalCase Classes, camelCase Object/Datatype properties), as defined in `PRD/PRD.md` (Canonical schema + naming).

---

## 3. Core Class Structure (Vertex Collections)

The ontology extends the `sentries_ontology.owl` to include banking and real estate domains.

### 3.1 Legal Entities (The "Who")

* **`LegalEntity`** (Superclass)
* **`Person`**: Individuals (Source: `Faker('en_IN')`).
* *Attributes:* `panNumber`, `aadhaarMasked`, `riskScore`.


* **`Organization`**: Companies, Trusts, Shell Entities.
* *Attributes:* `gstin`, `incorporation_date`, `industry_code`.


* **`WatchlistEntity`**: Entities explicitly listed on regulatory lists (OFAC, RBI).



### 3.2 Financial Instruments (The "How")

* **`FinancialInstrument`**
* **`BankAccount`**: Savings, Current, NRE/NRO accounts.
* *Attributes:* `accountNumber`, `balance`, `openDate`.


* **`DigitalWallet`**: UPI IDs, E-wallets.



### 3.3 Assets & Geography (The "What" & "Where")

* **`Asset`**
* **`RealProperty`**: Land, Apartments, Commercial Buildings.
* *Attributes:* `surveyNumber`, `circleRateValue`, `marketValue`, `geoLocation`.




* **`Location`**
* **`Address`**: Physical locations.
* *Attributes:* `street`, `district`, `state`, `pincode`.


* **`DigitalLocation`**: Metadata for tracking.
* *Attributes:* `ipAddress`, `deviceId`, `macAddress`.





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
* **`UndervaluedTransaction`**: Transaction `amount` < `circleRateValue` * tolerance.
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
| **`hasAccount`** | `LegalEntity` | `BankAccount` | Ownership of funds. |
| **`transferredTo`** | `BankAccount` | `BankAccount` | Money movement (edges carry `amount`, `timestamp`). |
| **`relatedTo`** | `Person` | `Person` | Familial/Social ties (Symmetric). |
| **`associatedWith`** | `Person` | `Organization` | Directors, Partners, UBOs. |
| **`residesAt`** | `Person` | `Address` | Home address. |
| **`accessedFrom`** | `BankAccount` | `DigitalLocation` | Login/Transaction IP or Device. |
| **`hasDigitalLocation`** | `Person` | `DigitalLocation` | Optional direct link for ER blocking (shared device/IP). |
| **`registeredSale`** | `RealProperty` | `RealEstateTransaction` | Link property to the sale event. |
| **`buyerIn`** | `LegalEntity` | `RealEstateTransaction` | Party buying. |
| **`sellerIn`** | `LegalEntity` | `RealEstateTransaction` | Party selling. |
| **`mentionedIn`** | `LegalEntity` | `Document` | GraphRAG link between graph & text. |
| **`resolvedTo`** | `Person` | `GoldenRecord` | Entity Resolution link from raw identity to canonical identity. |

---

## 6. Datatype Properties (Attributes)

Attributes specific to the Indian context needed for the demo algorithms.

| Property URI | Domain | Type | Notes |
| --- | --- | --- | --- |
| **`riskScore`** | `Entity` | `xsd:decimal` | 0-100 aggregated risk. |
| **`riskInferred`** | `Entity` | `xsd:decimal` | Risk derived from neighbors. |
| **`circleRateValue`** | `RealProperty` | `xsd:decimal` | Gov minimum value per sq ft. |
| **`marketValue`** | `RealProperty` | `xsd:decimal` | Actual estimated value. |
| **`txnType`** | `Transaction` | `xsd:string` | NEFT, RTGS, UPI, IMPS. |
| **`isBenamiSuspect`** | `RealProperty` | `xsd:boolean` | Flag for investigation. |

**Phase 1 storage mapping:** the physical fields match the ontology property names (camelCase).

---

## 7. Implementation Strategy

### 7.1 Integration with Data Generator

The data generator ("Fraud Intelligence Data Fabric") must produce CSV/JSON files that align with these class names.

* *Generator:* Creates `persons.csv` (or `customers.csv`) -> *Ontology:* Maps to `fi:Person`.
* *Generator:* Creates `deeds.json` -> *Ontology:* Maps to `fi:TitleDeed`.

### 7.2 Integration with Graph Analytics

The Agentic Workflow will use this ontology to select algorithms:

* *Query:* "Find **BenamiTransactions**"
* *Agent Logic:* Look up `BenamiTransaction` in ontology -> See it involves `RealProperty`, `buyer_in`, and `related_to` edges -> Select **PageRank** (to find controller) or **WCC** (to find the hidden family ring).

### 7.3 Success Criteria

1. **Valid Import:** `arango-rdf` CLI tool successfully imports the `.owl` file and creates the collection structure in ArangoDB without errors.
2. **Queryability:** An AQL query can successfully traverse `Person -> related_to -> Person -> buyer_in -> RealEstateTransaction` using the generated edge definitions.
3. **Classification:** The demo successfully labels a node as `FraudTypology/Hawala` based on the ontological definition.