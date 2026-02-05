# Fraud Intelligence Domain Description - Indian Banking

**Industry:** Banking & Financial Services  
**Geography:** India  
**Focus:** Fraud Detection, AML Compliance, Risk Intelligence  
**Graph:** fraud_intelligence_graph

> **Note (template / illustrative):** This document is written as a domain prompt/template for a future agentic
> graph-analytics workflow. The **current demo dataset on AMP is smaller** (see `docs/phase1-validation-report.md`
> for real counts) and uses named graphs `OntologyGraph`, `DataGraph`, and `KnowledgeGraph`.

---

## Domain Overview

### Industry & Business Context

Indian banking fraud detection and anti-money laundering (AML) system for a mid-sized private sector bank operating across 15 states. The bank serves 2 million+ retail customers and 50,000+ SME/corporate clients, processing ₹5,000+ Crores in daily transactions.

Our fraud and compliance team faces escalating threats:
- **Circular trading schemes**: Layering operations using 3-6 linked accounts
- **Money mule networks**: Smurfing/structuring to evade CTR thresholds (₹10 Lakhs)
- **Circle rate evasion**: Property transactions undervalued to evade stamp duty
- **Benami transactions**: Hidden beneficial ownership through proxies and nominees
- **Hawala indicators**: Rapid cross-regional transfers with value differentials

Current rule-based systems generate high false positives (60%+) and miss sophisticated schemes. We need graph analytics to detect complex network patterns and resolve hidden identities.

---

## Graph Structure Overview

Our fraud intelligence graph integrates transactional data, identity data, digital forensics, and external intelligence sources to enable network-based fraud detection.

### Vertex Collections (Nodes)

**Core Entities:**
- **Person** (10,523 active): Bank customers, beneficial owners, related parties
- **BankAccount** (15,847 active): Checking, savings, loan, and investment accounts
- **Organization** (2,156 active): Corporate entities including legitimate businesses and suspected shells
- **GoldenRecord** (8,234 records): Consolidated identities post-entity resolution

**Asset & Property:**
- **RealProperty** (4,892 properties): Real estate with circle rate and market value data
- **RealEstateTransaction** (3,127 transactions): Property sales with transaction values

**Risk & Intelligence:**
- **WatchlistEntity** (547 entities): RBI defaulters, ED investigations, FATF sanctions, internal blacklist
- **Document** (1,200+ documents): Title deeds, KYC records, news articles (GraphRAG sources)

**Digital Forensics:**
- **DigitalLocation** (8,456 locations): IP addresses, device IDs, MAC addresses, fingerprints
- **Address** (12,000+ addresses): Physical locations with district, state, pincode, lat/long

**Transactions:**
- **Transaction** (50,000+ transactions): Fund transfers with amounts, timestamps, types

### Edge Collections (Relationships)

**Ownership & Control:**
- **hasAccount** (18,000+ edges): Person/Organization → BankAccount (ownership/control)
- **associatedWith** (3,400+ edges): Person → Organization (directors, partners, UBOs)

**Money Flows:**
- **transferredTo** (52,000+ edges): BankAccount → BankAccount (fund transfers)
  - Attributes: `amount`, `timestamp`, `txnType`, `scenario` (cycle/mule/background)

**Identity Resolution:**
- **resolvedTo** (2,289 edges): Person → GoldenRecord (identity consolidation)
  - Indicates duplicate/proxy identities resolved to canonical record

**Relationships:**
- **relatedTo** (5,600+ edges): Person ↔ Person (family, business partners)
  - Attributes: `relationType` (spouse, sibling, business_partner, etc.)

**Location & Digital:**
- **residesAt** (10,500+ edges): Person → Address (residential address)
- **accessedFrom** (15,000+ edges): BankAccount → DigitalLocation (login/transaction origin)
- **hasDigitalLocation** (8,000+ edges): Person → DigitalLocation (device ownership)

**Real Estate:**
- **registeredSale** (3,127 edges): RealProperty → RealEstateTransaction
- **buyerIn** (3,127 edges): Person/Organization → RealEstateTransaction
- **sellerIn** (3,127 edges): Person/Organization → RealEstateTransaction

**Evidence & Intelligence:**
- **mentionedIn** (2,500+ edges): Entity → Document (GraphRAG links to source text)

### Named Graph Configuration

**Graph Name:** `fraud_intelligence_graph`

**Vertex Collections:** All entity types listed above  
**Edge Definitions:** All relationship types above

**Special Configuration:**
- Cycle detection enabled on `transferredTo` edges
- PageRank configured for transaction network
- WCC for identity cluster detection

---

## Scale & Activity

### Volume Statistics
- **Total nodes:** ~40,000 entities
- **Total edges:** ~85,000 relationships
- **Transaction volume:** ₹500+ Crores monitored (12 months)
- **Daily transactions:** 2,000-3,000 new transfers
- **Watchlist entities:** 547 high-risk entities
- **Resolved identities:** 8,234 golden records (from 10,523 persons)
- **Fraud scenarios injected:** 50+ known fraud rings for testing

### Fraud Pattern Distribution
- **Circular trading rings:** 8 confirmed cycles (₹12+ Cr total)
- **Money mule networks:** 3 hub-and-spoke patterns (47 mules, ₹45 Cr)
- **Undervalued properties:** 127 circle rate violations (₹85 Cr tax exposure)
- **Benami clusters:** 150+ multi-entity identity groups
- **Watchlist connections:** 89 persons with 1-2 hop watchlist proximity

---

## Domain-Specific Terminology

### Indian Banking & Regulatory

**Entities:**
- **Benami**: Transaction in nominee's name to conceal beneficial owner
- **Shell Company**: Corporation with no real operations (used for layering)
- **Money Mule**: Account holder who transfers illegal funds for criminals
- **UBO**: Ultimate Beneficial Owner (≥25% ownership or control)
- **HNI**: High Net-Worth Individual (priority monitoring)
- **PEP**: Politically Exposed Person (enhanced due diligence required)

**Regulations & Compliance:**
- **PMLA**: Prevention of Money Laundering Act, 2002
- **FEMA**: Foreign Exchange Management Act (cross-border flows)
- **Benami Act**: Benami Transactions (Prohibition) Act, 2016
- **FIU-IND**: Financial Intelligence Unit - India (STR/CTR recipient)
- **RBI**: Reserve Bank of India (banking regulator)
- **ED**: Enforcement Directorate (money laundering enforcement)
- **FATF**: Financial Action Task Force (global AML standards)

**Reporting Requirements:**
- **CTR**: Cash Transaction Report (₹10 Lakhs+ in cash)
- **STR**: Suspicious Transaction Report (filed to FIU-IND within 7 days)
- **PAN**: Permanent Account Number (required for ₹50,000+ transactions)
- **KYC**: Know Your Customer (identity verification)
- **EDD**: Enhanced Due Diligence (for high-risk customers)

**Transaction Thresholds:**
- ₹10 Lakhs (₹1 million): CTR cash reporting threshold
- ₹20 Lakhs (₹2 million): PAN mandatory threshold
- ₹50,000: Initial PAN threshold
- ₹7 Lakhs: Suspicious cash threshold

**Currency:**
- **Lakh**: 100,000 (₹1,00,000)
- **Crore**: 10 million (₹1,00,00,000)
- Example: ₹2.5 Cr = ₹25 Lakhs = ₹2,50,00,000 = $300,000 USD approx

### Fraud Patterns

**Money Laundering Stages:**
- **Placement**: Introducing illegal funds into financial system
- **Layering**: Complex transactions to obscure source (circular trading)
- **Integration**: Funds appear legitimate and re-enter economy

**Specific Schemes:**
- **Circular Trading**: A→B→C→A closed loop transfers (layering)
- **Smurfing/Structuring**: Breaking large amounts into sub-threshold transactions
- **Hawala**: Informal value transfer (unregulated, often cross-border)
- **Trade-Based ML**: Over/under-invoicing to move value
- **Real Estate ML**: Property transactions to convert black money

**Network Patterns:**
- **Hub-and-Spoke**: Many mules → single aggregator account
- **Cycle/Loop**: Closed transaction paths (layering signature)
- **Star Topology**: One account → many recipients (distribution)
- **Chain**: Sequential transfers A→B→C→D (distance from source)

**Indian-Specific:**
- **Circle Rate**: Government minimum property value (varies by location)
- **Benami**: Property/accounts in nominee names
- **Hawala Corridor**: Common routes (Delhi-Mumbai, Gujarat-UAE)
- **Shell Director**: Person on paper only (name loaned for fee)

---

## Data Characteristics

### Transaction Data (12 months)
- **Volume:** 52,000+ transfers totaling ₹500+ Crores
- **Types:** NEFT, RTGS, IMPS, UPI, cheque
- **Attributes:** amount, timestamp, txnType, counterparty
- **Scenario tags:** cycle/mule/background (for pattern identification)

### Identity Data
- **Names:** Indian names with phonetic variations (Rajesh/Rajsh, Kumar/Kumarr)
- **PAN numbers:** Format ABCDE1234F (alphanumeric)
- **Aadhaar**: 12-digit biometric ID (masked for privacy)
- **Phone:** Indian format +91-XXXXXXXXXX
- **Email:** Mix of gmail, yahoo, outlook, corporate domains

### Real Estate Data
- **Circle rates:** Government-mandated minimum values by district
- **Market values:** Estimated current market price
- **Transaction values:** Recorded sale prices (often manipulated)
- **Locations:** Mumbai, Delhi, Bangalore, Pune, Ahmedabad (high-value markets)
- **Property types:** Residential, commercial, agricultural

### Digital Forensics
- **IP addresses:** IPv4 format, includes residential and commercial IPs
- **Devices:** Mobile, desktop, tablet
- **Access patterns:** Login timestamps, transaction timestamps
- **Shared indicators:** Multiple accounts from same IP/device (mule signature)

### Watchlist Sources
- **RBI Defaulters**: Wilful defaulters, fraud accounts
- **ED Investigations**: Money laundering cases
- **FATF Sanctions**: International terrorism financing, sanctions
- **Internal Blacklist**: Suspected fraudsters, closed accounts

---

## Business Context & Goals

### Current Pain Points

1. **High False Positive Rate (60%)**
   - Rule-based systems flag legitimate business activity
   - Investigation teams overwhelmed with alerts
   - Resource waste and alert fatigue

2. **Missed Sophisticated Schemes**
   - Multi-hop networks bypass single-transaction rules
   - Identity fragmentation hides beneficial owners
   - Cross-product fraud (credit + real estate) not detected

3. **Slow Investigation Cycles**
   - Manual graph traversal takes days
   - No automated relationship mapping
   - Limited entity resolution capability

4. **Regulatory Pressure**
   - RBI increasing compliance requirements
   - FIU-IND demanding faster STR filing
   - PMLA penalties for non-compliance

### Strategic Objectives

Using graph analytics and AI, we aim to:

1. **Reduce false positives by 70%** through network context
2. **Detect multi-hop schemes** (up to 6 degrees of separation)
3. **Automate entity resolution** (95%+ accuracy for duplicates)
4. **Generate investigative leads** in seconds, not days
5. **Prioritize by risk** (focus on high-confidence, high-exposure cases)
6. **Support regulatory compliance** (audit trails, STR evidence)

### Success Metrics

**Detection:**
- Detect 90%+ of injected fraud patterns
- <5% false positive rate
- Identify all circular trading rings
- Find all money mule hubs

**Performance:**
- Analysis complete in <2 minutes for demo
- Real-time risk scoring (<1 second per entity)
- Support 100K+ nodes at scale

**Business Impact:**
- ₹50+ Cr annual fraud prevention
- 70% reduction in investigation time
- 60% reduction in false positive alerts
- 95%+ compliance with FIU-IND reporting

---

## Analysis Requirements

### REQ-001: Detect Circular Trading Rings

**Type:** Cycle Detection  
**Priority:** Critical  
**Description:** Identify closed-loop money transfers indicative of layering schemes.

**Technical Approach:**
- Cycle detection on `transferredTo` edges
- Filter for cycles length 3-6 accounts
- Analyze timing (transactions within hours/days)
- Calculate total amount cycled

**Outputs Required:**
- List of all detected cycles
- Account IDs involved in each ring
- Total amount per cycle
- Temporal patterns (velocity)
- Risk classification

**Business Value:** Prevent ₹10-15 Cr annual layering activity, ensure PMLA compliance

---

### REQ-002: Identify Money Mule Networks

**Type:** Network Analysis (WCC + PageRank)  
**Priority:** Critical  
**Description:** Find hub-and-spoke patterns where many accounts rapidly funnel funds to central aggregator.

**Technical Approach:**
- WCC to find connected components
- PageRank to identify hub accounts (high centrality)
- Degree analysis for mule-to-hub ratio
- Digital forensics for shared IP/device

**Outputs Required:**
- Hub account IDs with inbound mule count
- List of mule accounts
- Total volume aggregated
- Shared digital footprint evidence
- Timing analysis

**Business Value:** Disrupt 80% of smurfing operations, improve CTR compliance

---

### REQ-003: Flag Circle Rate Evasion

**Type:** Property Analysis  
**Priority:** High  
**Description:** Identify real estate transactions recorded at/below government circle rate, indicating tax evasion and money laundering.

**Technical Approach:**
- Query RealProperty + RealEstateTransaction
- Filter where `transactionValue ≤ circleRateValue`
- Calculate delta to marketValue
- Cross-reference buyers/sellers with high-risk entities

**Outputs Required:**
- List of undervalued properties
- Circle rate vs transaction value comparison
- Estimated tax evasion amount
- Buyer/seller risk profiles
- Geographic concentration

**Business Value:** Detect ₹50+ Cr black money conversion, refer to Income Tax Department

---

### REQ-004: Resolve Benami Identities

**Type:** Entity Resolution + WCC  
**Priority:** High  
**Description:** Consolidate duplicate and proxy Person records to reveal hidden beneficial ownership.

**Technical Approach:**
- Entity resolution with phonetic name matching
- Shared attribute detection (PAN, phone, email, address)
- Create GoldenRecord for each resolved identity
- WCC on resolvedTo relationships

**Outputs Required:**
- GoldenRecord entities with consolidated data
- Person → GoldenRecord mappings
- Account holdings per GoldenRecord
- Hidden relationship revelations
- Risk score consolidation

**Business Value:** 40% improvement in KYC accuracy, detect hidden control structures

---

### REQ-005: Calculate Risk Propagation

**Type:** Risk Scoring & Graph Propagation  
**Priority:** High  
**Description:** Propagate risk scores from known bad actors (watchlists) to connected entities via "guilt by association."

**Technical Approach:**
- Seed risk from WatchlistEntity nodes
- Propagate via relatedTo, associatedWith, transferredTo edges
- Calculate direct, inferred, and path risk components
- Generate risk reasons for audit trail

**Outputs Required:**
- Risk scores (0-100) for all entities
- Risk component breakdown (direct/inferred/path)
- Risk reasons (human-readable explanations)
- Risk propagation paths
- Prioritized investigation list

**Business Value:** 60% reduction in false positives, focus on high-risk entities

---

## Domain-Specific Data Fields

### Person Attributes
```
_key: Unique identifier
name: Full name (may have variations)
panNumber: Indian tax ID (ABCDE1234F format)
phoneNumber: +91-XXXXXXXXXX
email: Contact email
dateOfBirth: YYYY-MM-DD
riskScore: 0-100 (composite)
riskDirect: 0-100 (watchlist/rules)
riskInferred: 0-100 (network proximity)
riskReasons: ["Watchlist match", "Connected to high-risk entity", ...]
```

### BankAccount Attributes
```
_key: Account number
accountType: SAVINGS/CHECKING/LOAN/INVESTMENT
balance: Current balance (₹)
openDate: Account opening date
status: ACTIVE/CLOSED/FROZEN/FLAGGED
riskScore: 0-100
transactionVolume: Total ₹ volume (12 months)
```

### transferredTo Edge Attributes
```
amount: Transfer amount (₹)
timestamp: Transaction datetime
txnType: NEFT/RTGS/IMPS/UPI/CHEQUE
scenario: cycle/mule/background (pattern tag)
```

### RealProperty Attributes
```
_key: Property ID
address: Full property address
district: Administrative district
state: Indian state
circleRateValue: Govt minimum value (₹)
marketValue: Estimated market price (₹)
propertyType: RESIDENTIAL/COMMERCIAL/AGRICULTURAL
```

### RealEstateTransaction Attributes
```
_key: Transaction ID
transactionDate: Sale date
transactionValue: Recorded sale price (₹)
paymentMethod: BANK_TRANSFER/MIXED/CASH (Mixed = suspicious)
stampDutyPaid: Amount paid (₹)
```

### GoldenRecord Attributes
```
_key: Canonical identity ID
consolidatedName: Primary name
consolidatedPAN: Primary PAN
personCount: Number of Person records resolved
accounts: Array of account IDs controlled
totalHoldings: Aggregated assets (₹)
riskScore: Consolidated risk (0-100)
```

---

## Indian Banking Context

### Regulatory Framework

**Key Regulations:**
- **PMLA 2002**: Mandates STR filing, CTR reporting, KYC norms
- **FEMA 1999**: Governs foreign exchange (Hawala detection)
- **Benami Act 2016**: Prohibits property in nominee names
- **PML Rules 2005**: Defines suspicious transaction criteria
- **RBI Master Directions**: KYC norms, CDD procedures

**Reporting Obligations:**
- STR to FIU-IND within 7 days of suspicion
- CTR for cash transactions ≥₹10 Lakhs
- Cross-border transfer reporting (≥₹5 Lakhs)
- PAN mandatory for transactions ≥₹50,000

### Fraud Landscape - Indian Context

**Common Schemes:**
1. **Loan Fraud**: Fake documents, straw borrowers, circular guarantees
2. **Real Estate ML**: Undervalued deeds, Benami properties
3. **Shell Companies**: Created for layering, dissolved after use
4. **Hawala Networks**: Cross-border value transfer (often Dubai/Singapore)
5. **Account Takeover**: Compromised credentials, social engineering

**Risk Factors:**
- Multiple accounts with same PAN (against RBI norms)
- Cash-intensive businesses (restaurants, retail)
- Rapid account opening and closure
- Transactions just below reporting thresholds
- Property transactions in cash-heavy segments

**Geography-Specific:**
- **Mumbai/Delhi**: High-value real estate, corporate fraud
- **Gujarat**: Hawala corridors, trade-based ML
- **NCR**: Property fraud, Benami transactions
- **Tier-2 cities**: Loan fraud, fake documentation

---

## Analysis Use Cases

### Use Case 1: Autonomous Fraud Detection

**Scenario:** Bank receives tip about potential money mule network  
**Question:** "Identify all money mule networks in the transaction graph"

**Expected AI Workflow:**
1. Schema analysis identifies relevant collections (BankAccount, transferredTo, DigitalLocation)
2. Selects appropriate algorithms (WCC for networks, PageRank for hubs)
3. Generates GAE templates with fraud-specific configurations
4. Executes analyses
5. Generates intelligence report with:
   - Detected mule networks (component IDs)
   - Hub account identifications (high PageRank)
   - Shared digital footprint evidence
   - Total volumes per network
   - Risk classifications and STR recommendations

---

### Use Case 2: Circle Rate Fraud Investigation

**Scenario:** Compliance team needs to audit property transactions  
**Question:** "Find undervalued property transactions that may indicate money laundering"

**Expected AI Workflow:**
1. Analyzes real estate schema (RealProperty, RealEstateTransaction, registeredSale)
2. Generates query templates for circle rate comparisons
3. Identifies properties where transactionValue ≤ circleRateValue
4. Cross-references with high-risk entities
5. Generates report with:
   - List of suspicious properties
   - Estimated tax evasion exposure
   - Buyer/seller risk profiles
   - Geographic concentration analysis
   - Income Tax referral recommendations

---

### Use Case 3: Identity Resolution & Benami Detection

**Scenario:** Suspected beneficial owner using multiple identities  
**Question:** "Resolve duplicate identities and identify Benami networks"

**Expected AI Workflow:**
1. Recognizes need for entity resolution
2. Analyzes GoldenRecord and resolvedTo relationships
3. Runs WCC on identity clusters
4. Identifies clusters with 3+ resolved identities
5. Generates report with:
   - Consolidated beneficial owners
   - Hidden account control structures
   - Total holdings per GoldenRecord
   - Benami Act violation indicators
   - KYC update requirements

---

## Data Quality & Constraints

### Data Quality
- **Completeness:** 95%+ of transactions have amounts and timestamps
- **Accuracy:** PAN validation 98%, address standardization 90%
- **Timeliness:** Transaction data <24 hours delay
- **Entity resolution:** 85% of duplicates resolved

### Performance Constraints
- **Demo requirement:** Analysis must complete in <2 minutes
- **Real-time scoring:** Risk score calculation <1 second per entity
- **Scale target:** Support 100K nodes, 500K edges (future)

### Privacy & Security
- PII encryption at rest
- Aadhaar numbers masked (per UIDAI regulations)
- Audit logging for all risk score access
- Role-based access control

---

## Success Criteria

### Technical Success
- All fraud patterns detected with ≥80% accuracy
- Entity resolution accuracy ≥95%
- Analysis completes in <2 minutes
- Risk scores calculated for all entities

### Business Success
- Generate actionable STR-ready reports
- Insights reference Indian regulations appropriately
- Risk classifications enable prioritization
- Reduce investigation time by 70%

### Regulatory Success
- Audit trail for all risk decisions
- STR documentation generation
- Compliance with FIU-IND format
- PAN/Aadhaar handling per regulations

---

## Integration Points

### With graph-analytics-ai Platform

**Input:** This domain description + business requirements  
**Processing:** Agentic workflow with `industry="fraud_intelligence"`  
**Output:** Fraud intelligence reports with Indian banking context

### With Existing Systems

**Upstream:**
- Core banking system (transaction feeds)
- KYC system (customer data)
- Watchlist services (RBI, ED, FATF)

**Downstream:**
- Case management system (investigations)
- FIU-IND reporting portal (STR filing)
- Risk dashboard (executive view)

---

## Demo Narrative

**Opening:** "India loses ₹100,000+ Crores annually to banking fraud. Traditional rule-based systems catch simple cases but miss sophisticated schemes involving multiple entities and complex transaction chains."

**Problem:** "Bank ABC detected circular trading patterns manually, taking 2-3 weeks per investigation. By then, funds had moved offshore."

**Solution:** "Using AI-powered graph analytics, we can now detect fraud rings in minutes, not weeks. The system autonomously analyzes transaction networks, resolves hidden identities, and generates regulatory-ready reports."

**Demo:** Show autonomous fraud detection finding circular trading, mule networks, and Benami schemes with Indian regulatory context.

**Impact:** "70% reduction in investigation time, 60% reduction in false positives, ₹50+ Cr annual fraud prevention."

---

**Document Status:** Ready for AI consumption  
**Next Step:** Create business requirements document with specific objectives  
**Platform Ready:** ✅ Industry=fraud_intelligence configured
