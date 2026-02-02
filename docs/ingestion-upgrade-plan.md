# Ingestion & Reset Tooling Upgrade Plan

## Executive Summary

This document outlines the changes needed to:
1. Update ingestion to load PascalCase-named CSVs into PascalCase-named collections/edges
2. Add mode-aware reset tooling with safety guardrails
3. Evaluate and recommend import method (arangoimport vs python-arango)

---

## Current State Analysis

### Current Naming Convention
- **CSV files**: snake_case (e.g., `person.csv`, `bank_account.csv`, `has_account.csv`)
- **Collections**: snake_case (e.g., `person`, `bank_account`, `has_account`)
- **Indexes**: Referenced by snake_case collection names

### Target Naming Convention (from PRD Canonical Names)
- **CSV files**: PascalCase (e.g., `Person.csv`, `BankAccount.csv`, `HasAccount.csv`)
- **Collections**: PascalCase (e.g., `Person`, `BankAccount`, `HasAccount`)
- **Indexes**: Must reference PascalCase collection names

### Naming Mapping Table

#### Vertex Collections
| Old (snake_case) | New (PascalCase) | CSV File |
|------------------|------------------|----------|
| `person` | `Person` | `Person.csv` |
| `organization` | `Organization` | `Organization.csv` |
| `watchlist_entity` | `WatchlistEntity` | `WatchlistEntity.csv` |
| `bank_account` | `BankAccount` | `BankAccount.csv` |
| `real_property` | `RealProperty` | `RealProperty.csv` |
| `address` | `Address` | `Address.csv` |
| `digital_location` | `DigitalLocation` | `DigitalLocation.csv` |
| `transaction` | `Transaction` | `Transaction.csv` |
| `real_estate_transaction` | `RealEstateTransaction` | `RealEstateTransaction.csv` |
| `document` | `Document` | `Document.csv` |
| `golden_record` | `GoldenRecord` | `GoldenRecord.csv` |

#### Edge Collections
| Old (snake_case) | New (PascalCase) | CSV File |
|------------------|------------------|----------|
| `has_account` | `HasAccount` | `HasAccount.csv` |
| `transferred_to` | `TransferredTo` | `TransferredTo.csv` |
| `related_to` | `RelatedTo` | `RelatedTo.csv` |
| `associated_with` | `AssociatedWith` | `AssociatedWith.csv` |
| `resides_at` | `ResidesAt` | `ResidesAt.csv` |
| `accessed_from` | `AccessedFrom` | `AccessedFrom.csv` |
| `has_digital_location` | `HasDigitalLocation` | `HasDigitalLocation.csv` |
| `mentioned_in` | `MentionedIn` | `MentionedIn.csv` |
| `registered_sale` | `RegisteredSale` | `RegisteredSale.csv` |
| `buyer_in` | `BuyerIn` | `BuyerIn.csv` |
| `seller_in` | `SellerIn` | `SellerIn.csv` |
| `resolved_to` | `ResolvedTo` | `ResolvedTo.csv` |

---

## Current Script Behavior

### `scripts/ingest.py`
- **Current behavior**:
  - Reads CSV files from `--data-dir` (expects snake_case filenames)
  - Creates collections/edges if missing (snake_case names)
  - Creates indexes on snake_case collection names
  - Uses `python-arango` `import_bulk()` with 2000-doc batches
  - Supports `--force` to truncate existing collections
  - Supports `--validate-only` for schema validation
  - Uses `common.py` for config (already supports MODE=LOCAL|REMOTE)

- **Issues**:
  - Hardcoded snake_case collection names in `VERTEX_COLLECTIONS` and `EDGE_COLLECTIONS`
  - CSV filename matching assumes snake_case
  - Index creation uses snake_case collection names
  - No mode-aware safety checks

### `scripts/reset_db.py`
- **Current behavior**:
  - Truncates whitelisted collections (snake_case names)
  - Requires `--execute --confirm` to actually truncate
  - Blocks non-local URLs unless `--allow-remote` is used
  - Uses `is_local()` URL parsing check

- **Issues**:
  - No explicit `--mode LOCAL|REMOTE` support
  - No `--confirm-remote` flag
  - No database name validation
  - Whitelist uses snake_case names
  - No legacy cleanup option

---

## Import Method Evaluation

### arangoimport (Command-line Tool)
**Pros:**
- Purpose-built for bulk file imports
- Native ArangoDB tool, potentially faster for very large datasets
- Supports CSV directly
- Can disable indexes during import for better performance

**Cons:**
- Requires subprocess execution from Python
- Less control over data transformation (numeric/JSON field conversion)
- Requires CSV files to be in specific format
- Harder to integrate with existing Python error handling
- Current code already handles type conversion (numeric, JSON fields)

### python-arango import_bulk() (Current Method)
**Pros:**
- Already integrated and working
- Full control over data transformation
- Better error handling and reporting
- Supports batch processing (2000 docs/batch)
- Can easily add validation/transformation logic

**Cons:**
- May be slower for very large datasets (>1M docs)
- Requires Python driver overhead

### Recommendation: **Keep python-arango import_bulk()**
**Rationale:**
1. Current implementation already handles complex type conversions (numeric fields, JSON parsing)
2. Batch size (2000) is reasonable for Phase 1 datasets
3. Better integration with existing error handling
4. Performance is adequate for Phase 1 scale (~10k-50k docs)
5. Can optimize later if needed (increase batch size, parallel batches)

**Future optimization**: If datasets grow beyond 100k docs, consider:
- Increasing batch size to 5000-10000
- Parallel batch imports using ThreadPoolExecutor
- Or migrate to arangoimport with pre-processing script

---

## Required Changes

### Phase 1 Whititelist (Canonical List)
```python
PHASE1_VERTEX_COLLECTIONS = [
    "Person",
    "Organization",
    "WatchlistEntity",
    "BankAccount",
    "RealProperty",
    "Address",
    "DigitalLocation",
    "Transaction",
    "RealEstateTransaction",
    "Document",
    "GoldenRecord",
]

PHASE1_EDGE_COLLECTIONS = [
    "HasAccount",
    "TransferredTo",
    "RelatedTo",
    "AssociatedWith",
    "ResidesAt",
    "AccessedFrom",
    "HasDigitalLocation",
    "MentionedIn",
    "RegisteredSale",
    "BuyerIn",
    "SellerIn",
    "ResolvedTo",
]
```

### Legacy Collections (for cleanup)
```python
LEGACY_SNAKE_CASE_COLLECTIONS = [
    # All old snake_case names for optional cleanup
    "person", "organization", "watchlist_entity", "bank_account",
    "real_property", "address", "digital_location", "transaction",
    "real_estate_transaction", "document", "golden_record",
    "has_account", "transferred_to", "related_to", "associated_with",
    "resides_at", "accessed_from", "has_digital_location",
    "mentioned_in", "registered_sale", "buyer_in", "seller_in",
    "resolved_to",
]
```

---

## File-Level Change List

### 1. `scripts/ingest.py`
**Changes:**
- Update `VERTEX_COLLECTIONS` and `EDGE_COLLECTIONS` to PascalCase
- Update CSV filename expectations to PascalCase
- Update `ensure_schema()` to create PascalCase collections and indexes
- Update `NUMERIC_FIELDS` and `JSON_FIELDS` keys to PascalCase
- Keep existing `import_bulk()` logic (no change to import method)

**Index updates:**
- `db.collection("Person")` instead of `db.collection("person")`
- `db.collection("BankAccount")` instead of `db.collection("bank_account")`
- `db.collection("RealProperty")` instead of `db.collection("real_property")`
- `db.collection("Address")` instead of `db.collection("address")`
- `db.collection("TransferredTo")` instead of `db.collection("transferred_to")`

### 2. `scripts/reset_db.py`
**Changes:**
- Add `--mode LOCAL|REMOTE` argument (default: infer from config)
- Add `--confirm-remote` flag (required when mode=REMOTE)
- Add database name validation (must be "fraud-intelligence" for REMOTE)
- Update `WHITELIST` to PascalCase Phase 1 collections only
- Add `--cleanup-legacy` flag (optional, removes snake_case collections)
- Update collection lookup to use PascalCase names

**Safety checks:**
- If `--mode REMOTE` and `--confirm-remote` not set → error
- If `--mode REMOTE` and `db_name != "fraud-intelligence"` → error
- Only operate on whitelisted Phase 1 collections
- Dry-run by default (require `--execute --confirm`)

### 3. `scripts/schema_bootstrap.js` (Optional)
**Changes:**
- Update collection names to PascalCase
- Update index references to PascalCase collection names

**Note**: This file may be less critical if `ingest.py` handles schema creation.

### 4. `scripts/generate_data.py` (Future)
**Changes:**
- Update CSV output filenames to PascalCase
- Update `_from`/`_to` references in edge CSVs to use PascalCase collection names

**Note**: This is a separate task; ingestion should work with renamed CSVs regardless.

---

## Implementation Approach

### Step 1: Update `scripts/ingest.py`
1. Create PascalCase collection name constants
2. Update CSV filename matching logic
3. Update schema creation (collections + indexes)
4. Update field mapping dictionaries (NUMERIC_FIELDS, JSON_FIELDS)
5. Test with sample PascalCase CSVs

### Step 2: Update `scripts/reset_db.py`
1. Add `--mode` argument with LOCAL|REMOTE options
2. Add `--confirm-remote` flag
3. Add database name validation
4. Update whitelist to PascalCase
5. Add `--cleanup-legacy` option
6. Update safety checks

### Step 3: Testing
1. Test LOCAL mode (should work as before)
2. Test REMOTE mode (should require `--confirm-remote`)
3. Test database name validation
4. Test legacy cleanup (optional)

---

## Safety Guardrails Summary

### For `reset_db.py`:
1. **Mode enforcement**: `--mode REMOTE` requires `--confirm-remote`
2. **Database name check**: REMOTE mode only works with `fraud-intelligence` database
3. **Whitelist-only**: Only Phase 1 collections can be truncated
4. **Dry-run default**: Requires `--execute --confirm` to actually truncate
5. **Legacy cleanup**: Optional, requires explicit `--cleanup-legacy` flag

### For `ingest.py`:
1. **Existing safeguards**: `--force` required to overwrite existing data
2. **Validation mode**: `--validate-only` for safe schema checks
3. **Config-aware**: Already uses `common.py` for mode-aware config

---

## Migration Path

### Option A: Clean Migration (Recommended)
1. Update `ingest.py` to support PascalCase
2. Update `reset_db.py` with safeguards
3. Regenerate CSVs with PascalCase names (separate task)
4. Run ingestion with new CSVs
5. Optionally cleanup legacy collections

### Option B: Backward Compatibility
- Support both naming conventions temporarily
- Detect CSV naming and use appropriate collection names
- **Not recommended**: Adds complexity, harder to maintain

---

## Testing Checklist

- [ ] `ingest.py` creates PascalCase collections
- [ ] `ingest.py` creates indexes on PascalCase collections
- [ ] `ingest.py` loads PascalCase CSV files correctly
- [ ] `reset_db.py --mode LOCAL` works (dry-run and execute)
- [ ] `reset_db.py --mode REMOTE` requires `--confirm-remote`
- [ ] `reset_db.py --mode REMOTE` rejects non-"fraud-intelligence" DB
- [ ] `reset_db.py` only truncates whitelisted collections
- [ ] `reset_db.py --cleanup-legacy` removes snake_case collections (optional)
- [ ] Type conversions (numeric, JSON) still work correctly
- [ ] Edge `_from`/`_to` references use PascalCase collection names

---

## Open Questions

1. **Edge `_from`/`_to` format**: Do CSVs use `Person/key123` or `person/key123`?
   - **Answer**: Should be `Person/key123` (collection name matches new naming)
   - **Action**: Verify CSV generation produces correct format

2. **Legacy cleanup**: Should this be automatic or opt-in?
   - **Recommendation**: Opt-in via `--cleanup-legacy` flag

3. **Schema bootstrap**: Should `schema_bootstrap.js` be updated or deprecated?
   - **Recommendation**: Update for consistency, but `ingest.py` is primary

---

## Next Steps

1. Implement changes to `ingest.py` and `reset_db.py`
2. Update `schema_bootstrap.js` (optional)
3. Test with sample PascalCase CSVs
4. Document migration steps for users
5. Update `generate_data.py` to produce PascalCase CSVs (separate task)
