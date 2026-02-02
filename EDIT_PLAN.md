# Edit Plan: Update CSV Filenames and Headers to Match Collection Naming

## Current State Analysis

### Current Filenames (snake_case)
**Vertices:**
- `address.csv` → `Address.csv`
- `digital_location.csv` → `DigitalLocation.csv`
- `person.csv` → `Person.csv`
- `organization.csv` → `Organization.csv`
- `watchlist_entity.csv` → `WatchlistEntity.csv`
- `bank_account.csv` → `BankAccount.csv`
- `real_property.csv` → `RealProperty.csv`
- `real_estate_transaction.csv` → `RealEstateTransaction.csv`
- `document.csv` → `Document.csv`
- `transaction.csv` → `Transaction.csv`
- `golden_record.csv` → `GoldenRecord.csv`

**Edges:**
- `has_account.csv` → `hasAccount.csv`
- `transferred_to.csv` → `transferredTo.csv`
- `related_to.csv` → `relatedTo.csv`
- `associated_with.csv` → `associatedWith.csv`
- `resides_at.csv` → `residesAt.csv`
- `accessed_from.csv` → `accessedFrom.csv`
- `has_digital_location.csv` → `hasDigitalLocation.csv`
- `mentioned_in.csv` → `mentionedIn.csv`
- `registered_sale.csv` → `registeredSale.csv`
- `buyer_in.csv` → `buyerIn.csv`
- `seller_in.csv` → `sellerIn.csv`
- `resolved_to.csv` → `resolvedTo.csv`

### Current Column Headers (snake_case, except system fields)
All non-system fields (`_key`, `_from`, `_to` remain unchanged) need conversion to camelCase.

**Example conversions:**
- `street` → `street` (no change, single word)
- `pan_number` → `panNumber`
- `aadhaar_masked` → `aadhaarMasked`
- `risk_score` → `riskScore`
- `risk_direct` → `riskDirect`
- `risk_inferred` → `riskInferred`
- `risk_path` → `riskPath`
- `risk_reasons` → `riskReasons`
- `account_number` → `accountNumber`
- `account_type` → `accountType`
- `avg_monthly_balance` → `avgMonthlyBalance`
- `survey_number` → `surveyNumber`
- `circle_rate_value` → `circleRateValue`
- `market_value` → `marketValue`
- `transaction_value` → `transactionValue`
- `payment_method` → `paymentMethod`
- `doc_type` → `docType`
- `txn_type` → `txnType`
- `canonical_name` → `canonicalName`
- `ownership_type` → `ownershipType`
- `relation_type` → `relationType`
- `access_timestamp` → `accessTimestamp`
- `access_type` → `accessType`
- `mention_type` → `mentionType`
- `listing_reason` → `listingReason`
- `org_type` → `orgType`
- `ip_address` → `ipAddress`
- `device_id` → `deviceId`
- `mac_address` → `macAddress`

**System fields (unchanged):**
- `_key` → `_key`
- `_from` → `_from`
- `_to` → `_to`

**Timestamp fields:**
- `timestamp` → `timestamp` (no change, single word)

## Required Changes

### 1. `scripts/generate_data.py`

#### Add helper functions:
```python
def snake_to_pascal(s: str) -> str:
    """Convert snake_case to PascalCase."""
    parts = s.split('_')
    return ''.join(word.capitalize() for word in parts)

def snake_to_camel(s: str) -> str:
    """Convert snake_case to camelCase."""
    parts = s.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def field_to_camel(field: str) -> str:
    """Convert field name to camelCase, preserving system fields."""
    if field.startswith('_'):
        return field  # _key, _from, _to unchanged
    return snake_to_camel(field)
```

#### Update data row dictionaries:
All dictionary keys in the data generation sections need to be converted to camelCase (except system fields).

**Sections to update:**
- Address rows (lines ~157-174)
- Digital location rows (lines ~182-202)
- Person rows (lines ~207-243)
- Organization rows (lines ~248-258)
- Watchlist rows (lines ~263-276)
- Bank account rows (lines ~281-293)
- Has account edges (lines ~303-312)
- Related to edges (lines ~317-327)
- Accessed from edges (lines ~332-345)
- Transferred to edges (lines ~350-410)
- Real property rows (lines ~415-443)
- Real estate transaction rows (lines ~448-457)
- Registered sale edges (lines ~458-463)
- Buyer/seller edges (lines ~464-467)
- Document rows (lines ~472-491)
- Mentioned in edges (lines ~492-510)
- Transaction rows (lines ~513-522)
- Resides at edges (lines ~530-533)
- Has digital location edges (lines ~535-543)
- Associated with edges (lines ~545-553)

#### Update outputs list (lines ~558-594):
- Filenames: Convert using `snake_to_pascal()` for vertices, `snake_to_camel()` for edges
- Field names: Convert all non-system fields using `field_to_camel()`

### 2. Dependent Files That Will Break

#### `scripts/ingest.py`
**Current behavior:** Expects CSV filenames matching collection names exactly (snake_case).
- Line 215: `expected = [f"{name}.csv" for name in VERTEX_COLLECTIONS + EDGE_COLLECTIONS]`
- Line 222: `csv_files[f"{name}.csv"]`

**Required changes:**
- Add mapping functions to convert collection names to CSV filenames
- Update CSV lookup logic to use new filenames
- Update `convert_row()` to handle camelCase field names (or add field name mapping)

**Field name mapping:** `ingest.py` uses field names directly from CSV headers. Since CSV headers will be camelCase but ArangoDB collections use snake_case, we need to:
- Option A: Map camelCase CSV headers back to snake_case when importing
- Option B: Update ArangoDB collections to use camelCase (not recommended, breaks existing schema)

**Recommendation:** Option A - add reverse mapping in `ingest.py` to convert camelCase CSV headers to snake_case for database storage.

#### `tests/test_generator_invariants.py`
**Current behavior:** Reads CSVs using `f"{name}.csv"` where `name` is snake_case.
- Line 12: `path = _data_dir() / f"{name}.csv"`
- Line 19: `_read_csv("transferred_to")`
- Line 47: `_read_csv("transferred_to")`
- Line 60: `_read_csv("accessed_from")`
- Line 70: `_read_csv("real_property")`
- Line 71: `_read_csv("registered_sale")`
- Line 72: `_read_csv("real_estate_transaction")`

**Required changes:**
- Add helper function to convert collection name to CSV filename
- Update all `_read_csv()` calls to use new filenames
- Update field name access in tests (e.g., `e["scenario"]` → `e["scenario"]` stays same, but `p["circle_rate_value"]` → `p["circleRateValue"]`)

#### `data/sample/metadata.json`
**Current behavior:** Contains counts keyed by old CSV filenames.
- Will be auto-updated when `generate_data.py` runs with new filenames
- No manual changes needed (file is generated)

## Edge Cases

1. **Timestamp fields:** `timestamp` is already camelCase (single word), no change needed
2. **Single-word fields:** `name`, `city`, `state`, `district`, `balance`, `amount`, `role`, `title`, `content` remain unchanged
3. **System fields:** `_key`, `_from`, `_to` must remain unchanged
4. **Deterministic output:** All changes must preserve seeded random generation - only field names change, not values
5. **Field name mapping in ingest:** Need bidirectional mapping: CSV camelCase ↔ DB snake_case

## Implementation Order

1. **Phase 1:** Update `scripts/generate_data.py`
   - Add conversion helper functions
   - Update all data row dictionaries to use camelCase keys
   - Update outputs list with new filenames and headers
   - Test generation produces correct filenames and headers

2. **Phase 2:** Update `scripts/ingest.py`
   - Add filename mapping (collection name → CSV filename)
   - Add field name mapping (camelCase CSV → snake_case DB)
   - Update CSV lookup logic
   - Update `convert_row()` to map field names

3. **Phase 3:** Update `tests/test_generator_invariants.py`
   - Add filename mapping helper
   - Update all `_read_csv()` calls
   - Update field name access in assertions

4. **Phase 4:** Regenerate sample data
   - Run `scripts/generate_data.py` to produce new CSVs
   - Verify metadata.json updates correctly

## Testing Checklist

- [ ] Generated CSV filenames match target naming (PascalCase vertices, camelCase edges)
- [ ] CSV headers are camelCase (except system fields)
- [ ] Deterministic output preserved (same seed produces same data values)
- [ ] `ingest.py` can read and import new CSVs correctly
- [ ] Field names are correctly mapped (camelCase CSV → snake_case DB)
- [ ] All tests in `test_generator_invariants.py` pass with new filenames/headers
- [ ] No secrets are printed (existing constraint maintained)
