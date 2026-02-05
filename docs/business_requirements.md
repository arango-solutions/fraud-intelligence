# Fraud Intelligence - Business Requirements for Graph Analytics

**Project:** Fraud Detection & AML Compliance  
**Bank:** ABC Bank (India)  
**Date:** January 2026  
**Department:** Risk & Compliance  
**Priority:** Critical

> **Note (template / illustrative):** This document is a business-requirements template for a future agentic
> graph-analytics workflow. Any dataset sizes mentioned are **illustrative**; for the current demo dataset,
> use the real counts in `docs/phase1-validation-report.md` and the use-case definitions in `PRD/Fraud Use Cases PRD.md`.

---

## Domain Description

### Industry & Business Context

Mid-sized private sector bank operating across 15 Indian states, serving 2 million+ retail customers and 50,000+ SME/corporate clients. Daily transaction volume: ₹5,000+ Crores. We face escalating sophisticated fraud that traditional rule-based systems cannot detect.

### Graph Structure Overview

Our fraud intelligence graph represents the complex network of customers, accounts, transactions, and relationships in our banking system.

**Vertex Collections (Nodes):**
- **Person** (10,523 customers): Bank customers, beneficial owners, related parties
- **BankAccount** (15,847 accounts): All account types (savings, checking, loan, investment)
- **Organization** (2,156 entities): Corporate customers, including suspected shell companies
- **RealProperty** (4,892 properties): Real estate assets with circle rate data
- **WatchlistEntity** (547 entities): RBI defaulters, ED investigations, FATF sanctions
- **DigitalLocation** (8,456 locations): IP addresses, devices, digital fingerprints
- **GoldenRecord** (8,234 records): Resolved identities post-entity resolution
- **Transaction** (50,000+ transfers): Fund transfer events
- **RealEstateTransaction** (3,127 sales): Property transactions

**Edge Collections (Relationships):**
- **transferredTo** (52,000+ edges): Money flows between accounts (amount, timestamp, type)
- **hasAccount** (18,000+ edges): Account ownership and control
- **resolvedTo** (2,289 edges): Identity resolution links (Person → GoldenRecord)
- **relatedTo** (5,600+ edges): Family and business relationships
- **associatedWith** (3,400+ edges): Corporate directors, partners, UBOs
- **residesAt** (10,500+ edges): Residential addresses
- **accessedFrom** (15,000+ edges): Digital access patterns (account → IP/device)
- **registeredSale** (3,127 edges): Property to transaction links
- **buyerIn/sellerIn** (6,254 edges): Transaction parties

**Named Graph:** `fraud_intelligence_graph`

**Scale & Activity:**
- Total nodes: ~40,000 entities
- Total edges: ~85,000 relationships
- Transaction monitoring: ₹500+ Crores (12 months)
- Fraud scenarios: 50+ confirmed rings
- Watchlist proximity: 89 persons within 2 hops of watchlist entities

---

### Domain-Specific Terminology

**Indian Banking & Regulatory:**
- **Benami Transaction**: Property/account held in nominee name to conceal beneficial owner
- **Circle Rate**: Government-mandated minimum property value (varies by district)
- **CTR**: Cash Transaction Report (₹10 Lakhs+ cash transactions)
- **STR**: Suspicious Transaction Report (filed to FIU-IND within 7 days)
- **FIU-IND**: Financial Intelligence Unit - India (regulatory body)
- **PMLA**: Prevention of Money Laundering Act, 2002
- **FEMA**: Foreign Exchange Management Act (cross-border transactions)
- **PAN**: Permanent Account Number (tax identifier, required for ₹50K+ transactions)
- **UBO**: Ultimate Beneficial Owner (≥25% ownership or control)

**Fraud Patterns:**
- **Circular Trading**: Closed-loop transfers A→B→C→A (money laundering layering stage)
- **Money Mule**: Account holder who transfers illegal funds (often recruited, low awareness)
- **Smurfing/Structuring**: Breaking large amounts into sub-₹10L transactions to evade CTR
- **Hawala**: Informal value transfer system (unregulated, often cross-border)
- **Shell Company**: Corporation with no real operations (layering vehicle)
- **Layering**: Complex transaction chains to obscure fund source

**Risk Classification:**
- **CRITICAL (90-100)**: Confirmed fraud, immediate action required
- **HIGH (70-89)**: Strong indicators, investigation priority
- **MEDIUM (50-69)**: Suspicious patterns, enhanced monitoring
- **LOW (30-49)**: Anomaly detected, track

**Currency:**
- **Lakh**: ₹1,00,000 (100 thousand)
- **Crore**: ₹1,00,00,000 (10 million)
- Example: ₹2.5 Cr = 250 Lakhs = approximately $300,000 USD

---

### Business Context & Goals

We're experiencing 40% YoY growth in transaction volume but also seeing:
- 35% increase in fraud attempts
- 60% false positive rate in current rule-based detection
- 2-3 week investigation cycles (too slow)
- ₹100+ Cr annual fraud losses

Current rule-based systems miss sophisticated multi-hop schemes and generate overwhelming false positives. We need AI-powered graph analytics to:
1. **Detect network-based fraud** that spans multiple entities
2. **Resolve hidden identities** (Benami/proxy accounts)
3. **Prioritize investigations** by risk and exposure
4. **Generate STR-ready reports** with regulatory compliance

**Strategic Goal:** Reduce fraud losses by 70% (₹70+ Cr annually) and investigation time by 70% while maintaining <5% false positive rate.

### Data Characteristics

**Transaction Data (12 months):**
- Volume: 52,000+ transfers
- Total monitored: ₹500+ Crores
- Types: NEFT, RTGS, IMPS, UPI, cheque
- Attributes: amount, timestamp, txnType, counterparties

**Identity Data:**
- Indian names with phonetic variations (Rajesh/Rajsh, Brijesh/Vrijesh)
- PAN format: ABCDE1234F (5 letters, 4 numbers, 1 letter)
- Phone: +91-XXXXXXXXXX
- Email: Mix of personal and corporate domains

**Real Estate Data:**
- Circle rates from state govt price registries
- Market values from valuation agencies
- Transaction values from sale deeds
- Locations: Mumbai, Delhi, Bangalore, Pune (high-value markets)

**Digital Forensics:**
- IP addresses (residential and commercial)
- Device IDs and fingerprints
- Access timestamps and patterns
- Shared indicators (mule signature)

**Watchlist Data:**
- RBI wilful defaulters list
- ED money laundering investigations
- FATF sanctions and terrorism financing
- Internal bank blacklist

---

## Executive Summary

ABC Bank's fraud and compliance team needs graph analytics to detect sophisticated fraud schemes that traditional systems miss. We require autonomous AI analysis that understands Indian banking context, regulatory requirements, and can generate investigation-ready reports in minutes.

---

## Business Objectives

### OBJ-001: Detect and Disrupt Circular Trading Schemes

**Priority:** Critical  
**Regulatory:** PMLA Section 3 (Money Laundering Offense)

**Goal:** Identify all closed-loop money transfer patterns indicative of layering operations.

**Success Criteria:**
- Detect all cycles of length 3-6 accounts
- Calculate total amount cycled per ring
- Identify timing patterns (velocity indicators)
- Generate STR-ready documentation
- Provide account freeze recommendations

**Expected Business Value:**
- Prevent ₹10-15 Cr annual layering activity
- Ensure PMLA compliance (avoid ₹2 Cr+ penalties)
- Reduce investigation time from 2 weeks to 1 day

**Technical Requirements:**
- Cycle detection on transferredTo edges
- Temporal analysis (transaction timing)
- Amount pattern analysis
- Hub account identification

---

### OBJ-002: Identify and Neutralize Money Mule Networks

**Priority:** Critical  
**Regulatory:** PMLA (Structuring/Smurfing Detection)

**Goal:** Find hub-and-spoke patterns where many accounts rapidly funnel funds to central aggregators to evade CTR reporting (₹10 Lakhs threshold).

**Success Criteria:**
- Identify hub accounts with 20+ inbound mule transfers
- Map complete mule network topology
- Detect shared digital footprints (IP/device) across mules
- Calculate total structured volume per network
- Generate investigation priority list

**Expected Business Value:**
- Disrupt 80% of smurfing operations
- Improve CTR compliance by 90%
- Prevent ₹20+ Cr in structured transactions
- Reduce FIU-IND audit findings

**Technical Requirements:**
- WCC for network component detection
- PageRank for hub identification
- Digital forensics integration (shared IP/device)
- Degree centrality analysis

---

### OBJ-003: Flag Circle Rate Evasion in Property Transactions

**Priority:** High  
**Regulatory:** Income Tax Act, Benami Act

**Goal:** Identify real estate transactions recorded at or below government circle rate, indicating tax evasion and money laundering through property.

**Success Criteria:**
- Find all properties where transactionValue ≤ circleRateValue
- Calculate estimated stamp duty evasion
- Identify repeat offenders (serial evaders)
- Cross-reference buyers/sellers with high-risk entities
- Generate Income Tax Department referral reports

**Expected Business Value:**
- Detect ₹50+ Cr black money conversion
- Identify 100+ suspicious property transactions
- Support cross-agency collaboration (IT Department, ED)
- Prevent reputation damage

**Technical Requirements:**
- Real estate data analysis (RealProperty, RealEstateTransaction)
- Value comparison logic
- Geographic clustering
- Risk entity cross-reference

---

### OBJ-004: Resolve Benami Identities and Hidden Ownership

**Priority:** High  
**Regulatory:** Benami Transactions (Prohibition) Act, 2016

**Goal:** Consolidate duplicate and proxy Person records to reveal hidden beneficial ownership structures and improve KYC accuracy.

**Success Criteria:**
- Resolve 80%+ of duplicate Person records
- Create GoldenRecord for each beneficial owner
- Map hidden account control (accounts per GoldenRecord)
- Identify Benami networks (multiple proxies for one owner)
- Update consolidated risk scores

**Expected Business Value:**
- 40% improvement in KYC data quality
- Reveal hidden relationships (₹25+ Cr controlled by proxies)
- Support Benami Act compliance investigations
- Improve EDD effectiveness

**Technical Requirements:**
- Entity resolution with Indian name phonetics
- Shared attribute detection (PAN, phone, address)
- GoldenRecord creation and persistence
- WCC on identity clusters
- Risk score consolidation

---

### OBJ-005: Calculate and Propagate Network Risk Scores

**Priority:** High  
**Regulatory:** RBI KYC Norms (Risk-Based Approach)

**Goal:** Propagate risk from known bad actors (watchlist entities) to connected entities via "guilt by association," generating prioritized investigation lists.

**Success Criteria:**
- Calculate risk scores (0-100) for all entities
- Break down into components: direct, inferred, path risk
- Generate human-readable risk reasons (audit trail)
- Prioritize investigations by risk × exposure
- Update risk scores as new intelligence arrives

**Expected Business Value:**
- 60% reduction in false positive alerts
- Focus investigation resources on high-risk (top 5%)
- Improve EDD targeting (review high-risk only)
- Demonstrate risk-based approach to RBI auditors

**Technical Requirements:**
- Risk seed initialization from WatchlistEntity
- Graph-based risk propagation (bounded, decayed)
- Risk component calculation (direct/inferred/path)
- Risk reason generation for explainability

---

## Analytical Requirements

### REQ-001: Network Component Detection (WCC)

**Type:** Clustering / Community Detection  
**Description:** Identify all connected components in the fraud graph to detect coordinated networks.

**Technical Approach:**
- Weakly Connected Components (WCC) on full fraud graph
- Separate analysis on transaction subgraph (BankAccount + transferredTo)
- Separate analysis on identity subgraph (Person + resolvedTo)

**Outputs Required:**
- Component IDs with member counts
- Component size distribution
- Large components (money mule candidates, size >20)
- Medium components (Benami clusters, size 3-8)
- Singletons (isolated high-risk actors)

**Fraud Intelligence Interpretation:**
- Large components → Money mule networks
- Medium components → Benami identity groups
- Singletons → Sophisticated actors or false positives

---

### REQ-002: Transaction Hub Identification (PageRank)

**Type:** Centrality Analysis  
**Description:** Find accounts that are critical nodes in money flow networks (aggregators, distributors, bridges).

**Technical Approach:**
- PageRank on BankAccount vertices with transferredTo edges
- Edge weight consideration: amount, frequency
- Identify top 10 hub accounts
- Analyze concentration (% controlled by top 5)

**Outputs Required:**
- PageRank scores for all accounts
- Top 10 ranked accounts
- Concentration metrics (top 5 control %)
- Hub account characteristics
- Inbound/outbound degree distribution

**Fraud Intelligence Interpretation:**
- High PageRank account → Money mule hub or layering aggregator
- Extreme concentration → Coordinated fraud operation
- Normal distribution → Legitimate business activity

---

### REQ-003: Circular Trading Detection (Cycle Detection)

**Type:** Path Analysis / Cycle Detection  
**Description:** Find closed transaction loops that indicate layering schemes.

**Technical Approach:**
- Cycle detection on transferredTo edges
- Focus on cycles length 3-6 accounts
- Temporal analysis (time window of cycle completion)
- Amount analysis (consistent or escalating)

**Outputs Required:**
- List of all detected cycles
- Account IDs per cycle
- Total amount cycled
- Cycle completion time
- Transaction timestamps

**Fraud Intelligence Interpretation:**
- Any cycle → Strong layering indicator (CRITICAL risk)
- Fast cycles (<24 hours) → Coordinated, deliberate
- Consistent amounts → Automated system

---

### REQ-004: Identity Cluster Analysis (WCC on Identity Graph)

**Type:** Entity Resolution Analysis  
**Description:** Analyze consolidated identities to find Benami networks and hidden ownership.

**Technical Approach:**
- WCC on Person + GoldenRecord via resolvedTo edges
- Identify GoldenRecords with 3+ inbound persons
- Calculate total holdings per GoldenRecord
- Map account control per consolidated identity

**Outputs Required:**
- GoldenRecord IDs with person counts
- Total accounts controlled per GoldenRecord
- Total asset value per GoldenRecord
- Clusters suggesting Benami operations
- Risk score consolidation

**Fraud Intelligence Interpretation:**
- GoldenRecord with 3+ persons → Benami network
- High asset concentration → Hidden beneficial owner
- Shared attributes → Proxy identity scheme

---

### REQ-005: Geographic Fraud Hotspot Analysis

**Type:** Geospatial Analysis  
**Description:** Identify geographic concentration of fraud patterns and undervalued property transactions.

**Technical Approach:**
- Aggregate fraud indicators by district/state
- Circle rate evasion concentration analysis
- Watchlist entity geographic distribution
- High-risk property market identification

**Outputs Required:**
- Fraud concentration by geography
- High-risk districts/states
- Circle rate violation hotspots
- Property market risk rankings

**Fraud Intelligence Interpretation:**
- Geographic clustering → Organized fraud operations
- Circle rate hotspots → Systemic tax evasion
- Specific markets → Money laundering hubs

---

## Constraints & Considerations

### Performance Requirements
- **Demo Performance:** All analyses must complete in <2 minutes
- **Real-Time Scoring:** Risk calculation <1 second per entity
- **Scale Target:** Support 100K+ nodes for future deployment
- **Concurrent Users:** Support 10 investigators simultaneously

### Regulatory Compliance
- **STR Filing:** Generate STR-ready reports within 7 days of detection
- **Audit Trail:** Complete decision trail for every risk assessment
- **Data Privacy:** PAN/Aadhaar handling per UIDAI and RBI norms
- **Retention:** Fraud intelligence data 10 years (PMLA requirement)

### Accuracy Requirements
- **Fraud Detection:** 90%+ detection of known fraud rings (low false negatives)
- **False Positives:** <5% false positive rate (reduce alert fatigue)
- **Entity Resolution:** 95%+ accuracy for duplicate detection
- **Risk Scoring:** Confidence ≥70% for HIGH/CRITICAL classifications

### Business Context
- **Investigation Capacity:** Team of 12 can review 50 cases/month
- **Cost of Investigation:** ₹50,000 per case average
- **Cost of Missed Fraud:** ₹1-5 Cr per scheme average
- **Regulatory Penalty:** ₹2-10 Cr for non-compliance

---

## Success Metrics

### Technical Success
1. Detect all 8 confirmed circular trading rings (100% recall)
2. Identify all 3 money mule networks (100% recall)
3. Flag all 127 undervalued properties (<1% false negatives)
4. Resolve 85%+ duplicate identities (F1 score ≥0.90)
5. Calculate risk scores for all 10,523 persons
6. Complete full analysis in <2 minutes

### Business Success
1. Generate actionable intelligence reports with:
   - Specific account/entity IDs to investigate
   - Transaction amounts in ₹ Crores/Lakhs
   - Risk classifications (CRITICAL/HIGH/MEDIUM/LOW)
   - Regulatory filing recommendations (STR/CTR)
   - Immediate action items (freeze/investigate/refer)

2. Reports must reference:
   - Indian regulations (PMLA, FEMA, Benami Act)
   - FIU-IND reporting requirements
   - Circle rate fraud specific to Indian context
   - Confidence scores ≥70% for action items

3. Demonstrate:
   - 70% reduction in investigation time
   - 60% reduction in false positive rate
   - Clear prioritization (risk × exposure)

### Regulatory Success
1. STR documentation meets FIU-IND format requirements
2. Audit trail for all risk decisions
3. PAN verification for high-risk entities
4. Watchlist screening compliance
5. Demonstrate risk-based approach to RBI auditors

---

## Deliverables

### 1. Fraud Detection Intelligence Reports

For each detected fraud pattern:
- **Pattern Type:** Circular trading, mule network, circle rate evasion, Benami cluster
- **Entity IDs:** Specific accounts, persons, properties involved
- **Financial Exposure:** Total ₹ amount, tax evasion estimate
- **Risk Classification:** CRITICAL/HIGH/MEDIUM/LOW
- **Regulatory Action:** STR/CTR filing requirements
- **Investigation Steps:** Immediate, short-term, long-term actions
- **Confidence Score:** Based on evidence strength and data quality

### 2. Investigation Priority List

Ranked by: `risk_score × financial_exposure × confidence`

Include:
- Account/entity IDs
- Fraud pattern type
- Estimated exposure (₹)
- Risk classification
- Recommended action
- Investigation assignments

### 3. STR-Ready Documentation

For CRITICAL and HIGH risk findings:
- Complete narrative of suspicious activity
- Transaction details (amounts, dates, parties)
- Supporting evidence (digital forensics, patterns)
- Network analysis (connections to watchlist)
- Regulatory classification
- FIU-IND submission format

### 4. Interactive HTML Reports

Executive-friendly reports with:
- Fraud pattern visualizations (charts)
- Risk score distributions
- Geographic heatmaps
- Investigation checklists
- Regulatory compliance summary

---

## Demo Scenario

### Opening Statement
"Indian banking loses ₹100,000+ Crores annually to fraud. Traditional systems catch simple cases but miss sophisticated multi-entity schemes."

### Problem Statement
"ABC Bank manually investigated a circular trading ring, taking 3 weeks. By then, ₹4.8 Cr had moved offshore through shell companies. False positive rate: 60%."

### Solution Demonstration
"Our AI-powered graph analytics platform autonomously detects fraud in minutes, not weeks. Watch as it identifies circular trading, money mule networks, and Benami schemes with Indian regulatory context."

**Demo Steps:**
1. Show the fraud intelligence graph (40K nodes)
2. Run autonomous agentic workflow (`industry="fraud_intelligence"`)
3. Show AI analyzing schema, generating use cases
4. Display fraud detection reports with:
   - Circular trading: ₹12.4 Cr in 8 detected rings
   - Money mule hubs: 47 mules aggregating ₹45 Cr
   - Circle rate violations: 127 properties, ₹85 Cr tax evasion
   - Benami clusters: 150+ resolved identity groups
5. Show regulatory compliance (STR recommendations, PMLA references)
6. Display performance: <2 minutes total execution

### Expected Reaction
"Wow - it found patterns we couldn't see and generated STR documentation automatically. This changes everything."

### Business Impact Statement
"70% reduction in investigation time, 60% fewer false positives, ₹50+ Cr annual fraud prevention. ROI: 15x in year one."

---

## Stakeholders

- **Primary Owner:** VP Risk & Compliance
- **Technical Owner:** Chief Risk Officer
- **End Users:** 
  - Fraud investigators (12 person team)
  - Compliance officers (STR filing)
  - Risk managers (portfolio oversight)
- **Approval Required:** 
  - Chief Risk Officer
  - Head of Compliance
  - RBI inspection preparedness

---

## Timeline

- **Phase 1:** Setup and testing (1 week)
- **Phase 2:** Demo development and validation (2 weeks)
- **Phase 3:** Stakeholder demos (1 week)
- **Phase 4:** Production planning (ongoing)

---

## Notes for AI Platform

When the **graph-analytics-ai** platform processes this document with `industry="fraud_intelligence"`, it should:

✓ Use ₹ Crores/Lakhs in all amounts  
✓ Reference PMLA, FEMA, Benami Act, FIU-IND  
✓ Detect circular trading, mule networks, circle rate fraud, Benami clusters  
✓ Generate risk classifications (CRITICAL/HIGH/MEDIUM/LOW)  
✓ Provide STR filing recommendations  
✓ Include immediate action items (freeze accounts, file STR, investigate)  
✓ Reference Indian banking thresholds (₹10L CTR, ₹20L PAN)  
✓ Use fraud-specific terminology (layering, smurfing, Benami, Hawala)  
✓ Generate high-confidence insights (≥70%) for regulatory actions  

---

**Document Status:** Ready for AI consumption  
**Platform Configuration:** `industry="fraud_intelligence"`  
**Next Step:** Run `AgenticWorkflowRunner` with this document as input
