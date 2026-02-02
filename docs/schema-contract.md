# Schema contract (Phase 1)

**Source of truth:** `PRD/PRD.md` (canonical schema + naming)  
**Physical naming:** collections and fields follow OWL conventions (PascalCase collections, camelCase fields).

---

## Collections (vertices)

| Collection | Required fields (Phase 1) |
| --- | --- |
| `Person` | `_key`, `name`, `panNumber`, `aadhaarMasked`, `riskScore` |
| `Organization` | `_key`, `name`, `orgType`, `riskScore` |
| `WatchlistEntity` | `_key`, `name`, `listingReason`, `riskScore`, `riskDirect`, `riskReasons` |
| `BankAccount` | `_key`, `accountNumber`, `accountType`, `balance`, `avgMonthlyBalance`, `riskScore` |
| `RealProperty` | `_key`, `surveyNumber`, `district`, `state`, `pincode`, `circleRateValue`, `marketValue` |
| `Address` | `_key`, `street`, `city`, `district`, `state`, `pincode`, `lat`, `long` |
| `DigitalLocation` | `_key`, `ipAddress`, `deviceId`, `macAddress` |
| `Transaction` | `_key`, `amount`, `timestamp`, `txnType` |
| `RealEstateTransaction` | `_key`, `transactionValue`, `timestamp`, `paymentMethod` |
| `Document` | `_key`, `docType`, `title`, `content`, `timestamp` |
| `GoldenRecord` | `_key`, `canonicalName` |

### Common risk fields (optional in Phase 1, present in outputs)

`riskDirect`, `riskInferred`, `riskPath`, `riskReasons`

---

## Edge collections

| Edge collection | Required fields |
| --- | --- |
| `hasAccount` | `_from`, `_to`, `ownershipType` |
| `transferredTo` | `_from`, `_to`, `amount`, `timestamp`, `txnType`, `scenario` |
| `relatedTo` | `_from`, `_to`, `relationType` |
| `associatedWith` | `_from`, `_to`, `role` |
| `residesAt` | `_from`, `_to` |
| `accessedFrom` | `_from`, `_to`, `accessTimestamp`, `accessType` |
| `hasDigitalLocation` | `_from`, `_to` |
| `mentionedIn` | `_from`, `_to`, `mentionType`, `confidence` |
| `registeredSale` | `_from`, `_to` |
| `buyerIn` | `_from`, `_to` |
| `sellerIn` | `_from`, `_to` |
| `resolvedTo` | `_from`, `_to` |

---

## Invariants

- **Keys**: `_key` unique within a collection
- **Edge references**: every `_from` / `_to` references an existing document `_id`
- **PAN format**: when present, `panNumber` matches `[A-Z]{5}[0-9]{4}[A-Z]{1}`
- **Amounts**: `amount > 0`, `transactionValue > 0`
- **Timestamps**: ISO-8601 strings
- **Risk scores**: within `[0, 100]` when present

