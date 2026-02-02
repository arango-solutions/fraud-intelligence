# Naming Migration Plan: snake_case → camelCase

## Overview

This document outlines the migration from snake_case to camelCase naming convention for collections, edges, and fields across the fraud-intelligence codebase.

## Naming Convention Mapping

### Vertex Collections (snake_case → camelCase)

| Old (snake_case) | New (camelCase) |
|------------------|-----------------|
| `person` | `person` (no change) |
| `organization` | `organization` (no change) |
| `watchlist_entity` | `watchlistEntity` |
| `bank_account` | `bankAccount` |
| `real_property` | `realProperty` |
| `address` | `address` (no change) |
| `digital_location` | `digitalLocation` |
| `transaction` | `transaction` (no change) |
| `real_estate_transaction` | `realEstateTransaction` |
| `document` | `document` (no change) |
| `golden_record` | `goldenRecord` |

### Edge Collections (snake_case → camelCase)

| Old (snake_case) | New (camelCase) |
|------------------|-----------------|
| `has_account` | `hasAccount` |
| `transferred_to` | `transferredTo` |
| `related_to` | `relatedTo` |
| `associated_with` | `associatedWith` |
| `resides_at` | `residesAt` |
| `accessed_from` | `accessedFrom` |
| `has_digital_location` | `hasDigitalLocation` |
| `mentioned_in` | `mentionedIn` |
| `registered_sale` | `registeredSale` |
| `buyer_in` | `buyerIn` |
| `seller_in` | `sellerIn` |
| `resolved_to` | `resolvedTo` |

### Field Names (snake_case → camelCase)

| Old (snake_case) | New (camelCase) |
|------------------|-----------------|
| `pan_number` | `panNumber` |
| `aadhaar_masked` | `aadhaarMasked` |
| `risk_score` | `riskScore` |
| `risk_direct` | `riskDirect` |
| `risk_inferred` | `riskInferred` |
| `risk_path` | `riskPath` |
| `risk_reasons` | `riskReasons` |
| `account_number` | `accountNumber` |
| `account_type` | `accountType` |
| `avg_monthly_balance` | `avgMonthlyBalance` |
| `survey_number` | `surveyNumber` |
| `circle_rate_value` | `circleRateValue` |
| `market_value` | `marketValue` |
| `ip_address` | `ipAddress` |
| `device_id` | `deviceId` |
| `mac_address` | `macAddress` |
| `transaction_value` | `transactionValue` |
| `txn_type` | `txnType` |
| `access_timestamp` | `accessTimestamp` |
| `access_type` | `accessType` |
| `mention_type` | `mentionType` |
| `relation_type` | `relationType` |
| `listing_reason` | `listingReason` |
| `canonical_name` | `canonicalName` |
| `doc_type` | `docType` |
| `org_type` | `orgType` |
| `payment_method` | `paymentMethod` |

---

## Test Files Requiring Updates

### 1. `tests/test_generator_invariants.py`

**Current Issues:**
- Line 19: CSV filename `"transferred_to"` → `"transferredTo"`
- Line 47: CSV filename `"transferred_to"` → `"transferredTo"`
- Line 60: CSV filename `"accessed_from"` → `"accessedFrom"`
- Line 70: CSV filename `"real_property"` → `"realProperty"`
- Line 71: CSV filename `"registered_sale"` → `"registeredSale"`
- Line 72: CSV filename `"real_estate_transaction"` → `"realEstateTransaction"`
- Line 78: Field `"circle_rate_value"` → `"circleRateValue"`
- Line 92: Field `"transaction_value"` → `"transactionValue"`

**Required Changes:**
- Update all CSV filename references to camelCase
- Update all field name references to camelCase

### 2. `tests/test_schema_contract.py`

**Current Issues:**
- Lines 11-34: `REQUIRED_COLLECTIONS` list contains snake_case names

**Required Changes:**
- Update all collection names in `REQUIRED_COLLECTIONS` to camelCase:
  - `"watchlist_entity"` → `"watchlistEntity"`
  - `"bank_account"` → `"bankAccount"`
  - `"real_property"` → `"realProperty"`
  - `"digital_location"` → `"digitalLocation"`
  - `"real_estate_transaction"` → `"realEstateTransaction"`
  - `"golden_record"` → `"goldenRecord"`
  - `"has_account"` → `"hasAccount"`
  - `"transferred_to"` → `"transferredTo"`
  - `"related_to"` → `"relatedTo"`
  - `"associated_with"` → `"associatedWith"`
  - `"resides_at"` → `"residesAt"`
  - `"accessed_from"` → `"accessedFrom"`
  - `"has_digital_location"` → `"hasDigitalLocation"`
  - `"mentioned_in"` → `"mentionedIn"`
  - `"registered_sale"` → `"registeredSale"`
  - `"buyer_in"` → `"buyerIn"`
  - `"seller_in"` → `"sellerIn"`
  - `"resolved_to"` → `"resolvedTo"`

### 3. `tests/test_basic_queries.aql`

**Current Issues:**
- Line 4: `WITH` clause uses snake_case collection names
- Line 7: Edge collection `has_account` → `hasAccount`
- Line 9: Edge collection `transferred_to` → `transferredTo`
- Line 16: Edge collection `buyer_in` → `buyerIn`
- Line 17: Edge collection `related_to` → `relatedTo`

**Required Changes:**
- Update `WITH` clause: `WITH person, bankAccount, realEstateTransaction, hasAccount, transferredTo, buyerIn, relatedTo`
- Update all edge collection references in traversal patterns

### 4. `scripts/test_phase1.py`

**Current Issues:**
- Line 29: References `test_basic_queries.aql` (file itself needs updating, but this reference is fine)
- The script reads and executes AQL queries, so it will automatically use updated queries once `test_basic_queries.aql` is fixed

**Required Changes:**
- No direct changes needed (indirectly affected by AQL file updates)

---

## Documentation Files Requiring Updates

### 1. `PRD/PRD.md`

**Current Issues:**
- Line 78-79: States "lower snake_case in ArangoDB"
- Line 100-112: Edge collection names shown in snake_case

**Required Changes:**
- Update section 2.6.1 to state: "Collections & edge collections: camelCase in ArangoDB"
- Update section 2.6.3 table to show camelCase edge collection names
- Update section 2.6.4 to show camelCase field names

### 2. `docs/schema-contract.md`

**Current Issues:**
- Line 4: States "snake_case in ArangoDB"
- Lines 10-22: Collection names in snake_case
- Lines 12-22: Field names in snake_case
- Lines 32-45: Edge collection names in snake_case

**Required Changes:**
- Update line 4: "Physical naming: collections and fields are **camelCase** in ArangoDB"
- Update all collection names in tables to camelCase
- Update all field names in tables to camelCase
- Update all edge collection names to camelCase

### 3. `docs/data_dictionary.md`

**Current Issues:**
- Lines 15-59: CSV filenames and field names in snake_case
- Lines 65-76: Edge CSV filenames and field names in snake_case

**Required Changes:**
- Update all CSV filename references (e.g., `person.csv` stays same, `bank_account.csv` → `bankAccount.csv`)
- Update all field name references to camelCase
- Update all edge CSV filename references to camelCase

### 4. `docs/ingestion_runbook.md`

**Current Issues:**
- References to scripts that will need to output camelCase CSV filenames

**Required Changes:**
- Update any explicit CSV filename references if present
- Add note about camelCase naming convention

### 5. `ontology/mapping.md`

**Current Issues:**
- Line 3: States "stored ArangoDB fields (snake_case)"
- Lines 14-26: Collection mappings show snake_case
- Lines 30-43: Edge collection mappings show snake_case
- Lines 47-59: Field mappings show snake_case

**Required Changes:**
- Update line 3: "stored ArangoDB fields (camelCase)"
- Update line 12: "Collections are camelCase:"
- Update all mapping tables to show camelCase on the right side

---

## Integration AQL Checks

Three AQL integration checks to verify patterns exist after ingest:

### 1. Cycle Detection (Circular Trading)

**Pattern:** Detect directed cycles in `transferredTo` edges indicating circular money movement.

```aql
WITH bankAccount, transferredTo
FOR account IN bankAccount
  FOR v, e, p IN 2..10 OUTBOUND account transferredTo
    FILTER p.vertices[*]._id ANY == account._id
    LIMIT 1
    RETURN {
      cycle: p.vertices[*]._key,
      edges: p.edges[*].amount,
      totalAmount: SUM(p.edges[*].amount)
    }
```

**Optimized version (using edge index):**
```aql
WITH bankAccount, transferredTo
FOR e IN transferredTo
  COLLECT fromAccount = e._from INTO transfers
  FOR cycle IN 1..1
    LET path = (
      FOR v, e2, p IN 2..10 OUTBOUND DOCUMENT(fromAccount) transferredTo
        FILTER p.vertices[*]._id ANY == DOCUMENT(fromAccount)._id
        LIMIT 1
        RETURN p
    )
    FILTER LENGTH(path) > 0
    RETURN {
      account: fromAccount,
      cycle: path[0].vertices[*]._key,
      totalAmount: SUM(path[0].edges[*].amount)
    }
```

### 2. Mule Hub + Shared Device

**Pattern:** Find accounts that receive many transfers (hub) and share a digital location with multiple source accounts.

```aql
WITH bankAccount, transferredTo, digitalLocation, accessedFrom
FOR hub IN bankAccount
  LET incoming = (
    FOR e IN transferredTo
      FILTER e._to == hub._id
      RETURN e
  )
  FILTER LENGTH(incoming) >= 50
  LET sourceAccounts = incoming[*]._from
  LET sharedDevices = (
    FOR src IN sourceAccounts
      FOR e IN accessedFrom
        FILTER e._from == src
        RETURN DISTINCT e._to
  )
  FOR device IN sharedDevices
    LET deviceUsers = (
      FOR e IN accessedFrom
        FILTER e._to == device
        FILTER e._from IN sourceAccounts
        RETURN DISTINCT e._from
    )
    FILTER LENGTH(deviceUsers) == LENGTH(sourceAccounts)
    RETURN {
      hub: hub._key,
      hubIncomingCount: LENGTH(incoming),
      sharedDevice: device,
      muleAccounts: LENGTH(sourceAccounts)
    }
```

**Optimized version:**
```aql
WITH bankAccount, transferredTo, digitalLocation, accessedFrom
// Find hub accounts (receiving >= 50 transfers)
FOR e IN transferredTo
  COLLECT hubId = e._to INTO transfers
  FILTER LENGTH(transfers) >= 50
  LET muleAccounts = transfers[*].e._from
  // Find shared digital locations
  FOR muleAccount IN muleAccounts
    FOR accessEdge IN accessedFrom
      FILTER accessEdge._from == muleAccount
      COLLECT deviceId = accessEdge._to INTO deviceUsers
      FILTER LENGTH(deviceUsers) == LENGTH(muleAccounts)
      RETURN {
        hub: hubId,
        hubIncomingCount: LENGTH(transfers),
        sharedDevice: deviceId,
        muleAccounts: LENGTH(muleAccounts)
      }
```

### 3. Undervalued Property Transaction

**Pattern:** Find real estate transactions where `transactionValue` is significantly below `circleRateValue`.

```aql
WITH realProperty, realEstateTransaction, registeredSale
FOR prop IN realProperty
  FOR saleEdge IN registeredSale
    FILTER saleEdge._from == prop._id
    LET tx = DOCUMENT(realEstateTransaction, saleEdge._to)
    FILTER tx != null
    FILTER tx.transactionValue <= prop.circleRateValue
    RETURN {
      property: prop._key,
      surveyNumber: prop.surveyNumber,
      circleRateValue: prop.circleRateValue,
      marketValue: prop.marketValue,
      transactionValue: tx.transactionValue,
      undervalueAmount: prop.circleRateValue - tx.transactionValue,
      undervaluePercent: ((prop.circleRateValue - tx.transactionValue) / prop.circleRateValue) * 100
    }
```

**Optimized version (edge-index first):**
```aql
WITH realProperty, realEstateTransaction, registeredSale
FOR saleEdge IN registeredSale
  LET prop = DOCUMENT(realProperty, saleEdge._from)
  LET tx = DOCUMENT(realEstateTransaction, saleEdge._to)
  FILTER prop != null AND tx != null
  FILTER tx.transactionValue <= prop.circleRateValue
  RETURN {
    property: prop._key,
    surveyNumber: prop.surveyNumber,
    circleRateValue: prop.circleRateValue,
    marketValue: prop.marketValue,
    transactionValue: tx.transactionValue,
    undervalueAmount: prop.circleRateValue - tx.transactionValue,
    undervaluePercent: ((prop.circleRateValue - tx.transactionValue) / prop.circleRateValue) * 100
  }
```

---

## Summary of Required Edits

### Test Files
1. **tests/test_generator_invariants.py**: Update CSV filenames and field names (8 locations)
2. **tests/test_schema_contract.py**: Update REQUIRED_COLLECTIONS list (18 collection names)
3. **tests/test_basic_queries.aql**: Update WITH clause and edge references (5 locations)
4. **scripts/test_phase1.py**: No direct changes (indirectly affected)

### Documentation Files
1. **PRD/PRD.md**: Update naming convention statement and tables (3 sections)
2. **docs/schema-contract.md**: Update all collection/field/edge names (entire document)
3. **docs/data_dictionary.md**: Update CSV filenames and field names (entire document)
4. **docs/ingestion_runbook.md**: Add note about camelCase (minor update)
5. **ontology/mapping.md**: Update all mapping tables to camelCase (entire document)

### Integration Checks
- Three AQL queries provided above (cycle, mule hub+device, undervalued property)
- All queries use camelCase naming convention
- Optimized versions provided following edge-index patterns

---

## Next Steps

1. Update all test files with camelCase names
2. Update all documentation files
3. Create integration test file with the three AQL checks
4. Update ingestion scripts to output camelCase CSV filenames
5. Update generator scripts to use camelCase field names
6. Run full test suite to verify changes
