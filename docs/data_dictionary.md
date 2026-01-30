# Data dictionary (Phase 1)

This dictionary documents the CSV outputs produced by `scripts/generate_data.py`.

## Conventions

- CSV encoding: UTF-8
- Header row present
- ArangoDB import:
  - Vertex docs use `_key`
  - Edge docs use `_from`/`_to` in the form `{collection}/{_key}`

## Vertex collections

### `person.csv`

- `_key` (string): document key (e.g., `person_42_000001`)
- `name` (string)
- `pan_number` (string, optional): `[A-Z]{5}[0-9]{4}[A-Z]{1}`
- `aadhaar_masked` (string)
- `risk_score` (number 0-100)
- `risk_direct` (number 0-100, optional)
- `risk_inferred` (number 0-100, optional)
- `risk_path` (number 0-100, optional)
- `risk_reasons` (string, optional): JSON array string

### `bank_account.csv`

- `_key` (string)
- `account_number` (string)
- `account_type` (string): `Savings|Current|NRE`
- `balance` (number)
- `avg_monthly_balance` (number)
- `risk_score` (number 0-100)

### `real_property.csv`

- `_key` (string)
- `survey_number` (string)
- `district` (string)
- `state` (string)
- `pincode` (string)
- `circle_rate_value` (number)
- `market_value` (number)
- `risk_score` (number 0-100)
- `risk_reasons` (string, optional): JSON array string

### Other vertex CSVs

The generator also produces:

- `organization.csv`
- `watchlist_entity.csv`
- `address.csv`
- `digital_location.csv`
- `transaction.csv`
- `real_estate_transaction.csv`
- `document.csv`
- `golden_record.csv` (placeholder)

## Edge collections

The generator produces one CSV per edge collection:

- `has_account.csv` (`_from`, `_to`)
- `transferred_to.csv` (`_from`, `_to`, `amount`, `timestamp`, `txn_type`)
- `related_to.csv` (`_from`, `_to`, `relation_type`)
- `associated_with.csv` (`_from`, `_to`, `role`)
- `resides_at.csv` (`_from`, `_to`)
- `accessed_from.csv` (`_from`, `_to`, `access_timestamp`, `access_type`)
- `has_digital_location.csv` (`_from`, `_to`)
- `mentioned_in.csv` (`_from`, `_to`, `mention_type`, `confidence`)
- `registered_sale.csv` (`_from`, `_to`)
- `buyer_in.csv` (`_from`, `_to`)
- `seller_in.csv` (`_from`, `_to`)
- `resolved_to.csv` (placeholder)

