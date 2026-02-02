# Concrete Edit Plan Summary

## Overview

Update `scripts/generate_data.py` to output CSV files with:
1. **Filenames:** PascalCase for vertices, camelCase for edges (matching collection names exactly)
2. **Column headers:** camelCase for all non-system fields (keeping `_key`, `_from`, `_to` unchanged)

## Files Requiring Changes

### Primary File
- **`scripts/generate_data.py`** - Main generation script

### Dependent Files (Will Break)
- **`scripts/ingest.py`** - CSV import script (expects snake_case filenames matching collection names)
- **`tests/test_generator_invariants.py`** - Test file (reads CSVs using snake_case names)

### Auto-Updated Files
- **`data/sample/metadata.json`** - Will be regenerated with new filenames when `generate_data.py` runs

## Exact Changes Required

### 1. `scripts/generate_data.py`

#### Add Helper Functions (after imports, before `main()`)
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

#### Update All Data Row Dictionaries
Every dictionary key that is snake_case must be converted to camelCase (except system fields).

**Example transformation:**
```python
# Before:
{
    "_key": key("person", args.seed, i),
    "pan_number": gen_pan(rng),
    "risk_score": 0,
}

# After:
{
    "_key": key("person", args.seed, i),
    "panNumber": gen_pan(rng),
    "riskScore": 0,
}
```

**Affected sections:** All data generation blocks (address_rows, digital_rows, person_rows, org_rows, watchlist_rows, bank_account_rows, has_account_rows, related_rows, accessed_from_rows, transferred_to_rows, property_rows, real_estate_tx_rows, registered_sale_rows, buyer_in_rows, seller_in_rows, document_rows, mentioned_in_rows, transaction_rows, golden_rows, resolved_to_rows, has_digital_location_rows, resides_at_rows, associated_with_rows)

#### Update Outputs List (lines 558-594)
```python
# Before:
("address.csv", ["_key", "street", "city", "district", "state", "pincode", "lat", "long"], address_rows),

# After:
("Address.csv", ["_key", "street", "city", "district", "state", "pincode", "lat", "long"], address_rows),
```

**For edges:**
```python
# Before:
("has_account.csv", ["_from", "_to", "ownership_type"], has_account_rows),

# After:
("hasAccount.csv", ["_from", "_to", "ownershipType"], has_account_rows),
```

**Complete outputs list transformation:**
- Filenames: Use `snake_to_pascal()` for vertices, `snake_to_camel()` for edges
- Field lists: Apply `field_to_camel()` to each field name

### 2. `scripts/ingest.py`

#### Add Mapping Functions
```python
def collection_to_csv_filename(collection_name: str) -> str:
    """Convert collection name to CSV filename."""
    if collection_name in VERTEX_COLLECTIONS:
        parts = collection_name.split('_')
        return ''.join(word.capitalize() for word in parts) + '.csv'
    else:  # edge collection
        parts = collection_name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:]) + '.csv'

def camel_to_snake(field: str) -> str:
    """Convert camelCase to snake_case."""
    if field.startswith('_'):
        return field  # System fields unchanged
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', field)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
```

#### Update CSV Lookup (line 214-222)
```python
# Before:
csv_files = {p.name: p for p in data_dir.glob("*.csv")}
expected = [f"{name}.csv" for name in VERTEX_COLLECTIONS + EDGE_COLLECTIONS]
missing = [f for f in expected if f not in csv_files]
if missing:
    raise SystemExit(f"Missing CSV files in {data_dir}: {missing}")

total_inserted = 0
for name in VERTEX_COLLECTIONS + EDGE_COLLECTIONS:
    inserted = import_collection(db, name, csv_files[f"{name}.csv"], force=args.force)

# After:
csv_files = {p.name: p for p in data_dir.glob("*.csv")}
expected = [collection_to_csv_filename(name) for name in VERTEX_COLLECTIONS + EDGE_COLLECTIONS]
missing = [f for f in expected if f not in csv_files]
if missing:
    raise SystemExit(f"Missing CSV files in {data_dir}: {missing}")

total_inserted = 0
for name in VERTEX_COLLECTIONS + EDGE_COLLECTIONS:
    csv_filename = collection_to_csv_filename(name)
    inserted = import_collection(db, name, csv_files[csv_filename], force=args.force)
```

#### Update `convert_row()` Function (line 103-118)
```python
# Before:
def convert_row(collection: str, row: Dict[str, str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in row.items():
        if v == "":
            continue
        if k in NUMERIC_FIELDS.get(collection, set()):
            out[k] = to_number(v)
            continue
        # ... rest of function

# After:
def convert_row(collection: str, row: Dict[str, str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in row.items():
        if v == "":
            continue
        # Map camelCase CSV field to snake_case DB field
        db_field = camel_to_snake(k)
        if db_field in NUMERIC_FIELDS.get(collection, set()):
            out[db_field] = to_number(v)
            continue
        if db_field in JSON_FIELDS.get(collection, set()):
            try:
                out[db_field] = json.loads(v)
            except Exception:
                out[db_field] = v
            continue
        out[db_field] = v
    return out
```

### 3. `tests/test_generator_invariants.py`

#### Add Helper Function
```python
def collection_to_csv_filename(name: str) -> str:
    """Convert collection name to CSV filename."""
    # Same implementation as in ingest.py
    VERTEX_COLLECTIONS = ["person", "organization", "watchlist_entity", "bank_account", 
                          "real_property", "address", "digital_location", "transaction",
                          "real_estate_transaction", "document", "golden_record"]
    if name in VERTEX_COLLECTIONS:
        parts = name.split('_')
        return ''.join(word.capitalize() for word in parts) + '.csv'
    else:
        parts = name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:]) + '.csv'
```

#### Update `_read_csv()` Function (line 11-15)
```python
# Before:
def _read_csv(name: str):
    path = _data_dir() / f"{name}.csv"
    assert path.exists(), f"missing {path}"
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# After:
def _read_csv(name: str):
    filename = collection_to_csv_filename(name)
    path = _data_dir() / filename
    assert path.exists(), f"missing {path}"
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
```

#### Update Field Access in Tests
All field accesses in test assertions need to use camelCase:

```python
# Before (line 23):
if e.get("scenario") == "cycle":

# After (unchanged - "scenario" is already camelCase):
if e.get("scenario") == "cycle":

# Before (line 91):
circle = float(p["circle_rate_value"])

# After:
circle = float(p["circleRateValue"])

# Before (line 92):
txn_val = float(tx["transaction_value"])

# After:
txn_val = float(tx["transactionValue"])
```

## Edge Cases Handled

1. **System fields:** `_key`, `_from`, `_to` remain unchanged in both filenames and headers
2. **Single-word fields:** Fields like `name`, `city`, `state`, `balance`, `amount`, `timestamp`, `role`, `title`, `content`, `scenario`, `confidence` remain unchanged (already camelCase)
3. **Deterministic output:** Only field names change, not data values - seeded generation remains deterministic
4. **Field name mapping:** Bidirectional mapping needed: CSV camelCase ↔ DB snake_case in `ingest.py`
5. **Metadata.json:** Auto-updates when `generate_data.py` runs (no manual changes needed)

## Testing Requirements

After changes:
1. Run `scripts/generate_data.py --output data/test --seed 42 --size sample --force`
2. Verify CSV filenames match target naming (PascalCase/camelCase)
3. Verify CSV headers are camelCase (except system fields)
4. Verify same seed produces same data values (deterministic)
5. Run `scripts/ingest.py --data-dir data/test --validate-only` (should find all CSVs)
6. Run `pytest tests/test_generator_invariants.py` (should pass with updated field names)
7. Verify no secrets are printed (existing constraint)

## Implementation Notes

- **Order matters:** Update `generate_data.py` first, then dependent files
- **Field mapping:** Critical to map camelCase CSV → snake_case DB in `ingest.py` to maintain database schema compatibility
- **Backward compatibility:** Old CSV files will not work with updated `ingest.py` - regeneration required
- **Test data:** `data/sample/` directory will need regeneration after changes
