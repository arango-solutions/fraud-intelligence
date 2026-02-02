# Data dictionary (Phase 1)

This dictionary documents the CSV outputs produced by `scripts/generate_data.py`.

## Conventions

- CSV encoding: UTF-8
- Header row present
- ArangoDB import:
  - Vertex docs use `_key`
  - Edge docs use `_from`/`_to` in the form `{collection}/{_key}`

## Vertex collections

### `Person.csv`

- `_key` (string): document key (e.g., `person_42_000001`)
- `name` (string)
- `panNumber` (string, optional): `[A-Z]{5}[0-9]{4}[A-Z]{1}`
- `aadhaarMasked` (string)
- `riskScore` (number 0-100)
- `riskDirect` (number 0-100, optional)
- `riskInferred` (number 0-100, optional)
- `riskPath` (number 0-100, optional)
- `riskReasons` (string, optional): JSON array string

### `BankAccount.csv`

- `_key` (string)
- `accountNumber` (string)
- `accountType` (string): `Savings|Current|NRE`
- `balance` (number)
- `avgMonthlyBalance` (number)
- `riskScore` (number 0-100)

### `RealProperty.csv`

- `_key` (string)
- `surveyNumber` (string)
- `district` (string)
- `state` (string)
- `pincode` (string)
- `circleRateValue` (number)
- `marketValue` (number)
- `riskScore` (number 0-100)
- `riskReasons` (string, optional): JSON array string

### Other vertex CSVs

The generator also produces:

- `Organization.csv`
- `WatchlistEntity.csv`
- `Address.csv`
- `DigitalLocation.csv`
- `Transaction.csv`
- `RealEstateTransaction.csv`
- `Document.csv`
- `GoldenRecord.csv` (placeholder)

## Edge collections

The generator produces one CSV per edge collection:

- `hasAccount.csv` (`_from`, `_to`, `ownershipType`)
- `transferredTo.csv` (`_from`, `_to`, `amount`, `timestamp`, `txnType`, `scenario`)
- `relatedTo.csv` (`_from`, `_to`, `relationType`)
- `associatedWith.csv` (`_from`, `_to`, `role`)
- `residesAt.csv` (`_from`, `_to`)
- `accessedFrom.csv` (`_from`, `_to`, `accessTimestamp`, `accessType`)
- `hasDigitalLocation.csv` (`_from`, `_to`)
- `mentionedIn.csv` (`_from`, `_to`, `mentionType`, `confidence`)
- `registeredSale.csv` (`_from`, `_to`)
- `buyerIn.csv` (`_from`, `_to`)
- `sellerIn.csv` (`_from`, `_to`)
- `resolvedTo.csv` (placeholder)

