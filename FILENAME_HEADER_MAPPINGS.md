# Exact Filename and Header Mappings

## Filename Mappings

### Vertices (snake_case → PascalCase)

| Current Filename | Target Filename | Collection Name |
|-----------------|-----------------|-----------------|
| `address.csv` | `Address.csv` | `address` |
| `digital_location.csv` | `DigitalLocation.csv` | `digital_location` |
| `person.csv` | `Person.csv` | `person` |
| `organization.csv` | `Organization.csv` | `organization` |
| `watchlist_entity.csv` | `WatchlistEntity.csv` | `watchlist_entity` |
| `bank_account.csv` | `BankAccount.csv` | `bank_account` |
| `real_property.csv` | `RealProperty.csv` | `real_property` |
| `real_estate_transaction.csv` | `RealEstateTransaction.csv` | `real_estate_transaction` |
| `document.csv` | `Document.csv` | `document` |
| `transaction.csv` | `Transaction.csv` | `transaction` |
| `golden_record.csv` | `GoldenRecord.csv` | `golden_record` |

### Edges (snake_case → camelCase)

| Current Filename | Target Filename | Collection Name |
|-----------------|-----------------|-----------------|
| `has_account.csv` | `hasAccount.csv` | `has_account` |
| `transferred_to.csv` | `transferredTo.csv` | `transferred_to` |
| `related_to.csv` | `relatedTo.csv` | `related_to` |
| `associated_with.csv` | `associatedWith.csv` | `associated_with` |
| `resides_at.csv` | `residesAt.csv` | `resides_at` |
| `accessed_from.csv` | `accessedFrom.csv` | `accessed_from` |
| `has_digital_location.csv` | `hasDigitalLocation.csv` | `has_digital_location` |
| `mentioned_in.csv` | `mentionedIn.csv` | `mentioned_in` |
| `registered_sale.csv` | `registeredSale.csv` | `registered_sale` |
| `buyer_in.csv` | `buyerIn.csv` | `buyer_in` |
| `seller_in.csv` | `sellerIn.csv` | `seller_in` |
| `resolved_to.csv` | `resolvedTo.csv` | `resolved_to` |

## Column Header Mappings

### Address.csv → Address.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `street` | `street` | Single word, unchanged |
| `city` | `city` | Single word, unchanged |
| `district` | `district` | Single word, unchanged |
| `state` | `state` | Single word, unchanged |
| `pincode` | `pincode` | Single word, unchanged |
| `lat` | `lat` | Single word, unchanged |
| `long` | `long` | Single word, unchanged |

### DigitalLocation.csv → DigitalLocation.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `ip_address` | `ipAddress` | snake_case → camelCase |
| `device_id` | `deviceId` | snake_case → camelCase |
| `mac_address` | `macAddress` | snake_case → camelCase |

### Person.csv → Person.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `name` | `name` | Single word, unchanged |
| `pan_number` | `panNumber` | snake_case → camelCase |
| `aadhaar_masked` | `aadhaarMasked` | snake_case → camelCase |
| `risk_score` | `riskScore` | snake_case → camelCase |
| `risk_direct` | `riskDirect` | snake_case → camelCase |
| `risk_inferred` | `riskInferred` | snake_case → camelCase |
| `risk_path` | `riskPath` | snake_case → camelCase |
| `risk_reasons` | `riskReasons` | snake_case → camelCase |

### Organization.csv → Organization.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `name` | `name` | Single word, unchanged |
| `org_type` | `orgType` | snake_case → camelCase |
| `risk_score` | `riskScore` | snake_case → camelCase |

### WatchlistEntity.csv → WatchlistEntity.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `name` | `name` | Single word, unchanged |
| `listing_reason` | `listingReason` | snake_case → camelCase |
| `risk_score` | `riskScore` | snake_case → camelCase |
| `risk_direct` | `riskDirect` | snake_case → camelCase |
| `risk_reasons` | `riskReasons` | snake_case → camelCase |

### BankAccount.csv → BankAccount.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `account_number` | `accountNumber` | snake_case → camelCase |
| `account_type` | `accountType` | snake_case → camelCase |
| `balance` | `balance` | Single word, unchanged |
| `avg_monthly_balance` | `avgMonthlyBalance` | snake_case → camelCase |
| `risk_score` | `riskScore` | snake_case → camelCase |

### RealProperty.csv → RealProperty.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `survey_number` | `surveyNumber` | snake_case → camelCase |
| `district` | `district` | Single word, unchanged |
| `state` | `state` | Single word, unchanged |
| `pincode` | `pincode` | Single word, unchanged |
| `circle_rate_value` | `circleRateValue` | snake_case → camelCase |
| `market_value` | `marketValue` | snake_case → camelCase |
| `risk_score` | `riskScore` | snake_case → camelCase |
| `risk_reasons` | `riskReasons` | snake_case → camelCase |

### RealEstateTransaction.csv → RealEstateTransaction.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `transaction_value` | `transactionValue` | snake_case → camelCase |
| `timestamp` | `timestamp` | Single word, unchanged |
| `payment_method` | `paymentMethod` | snake_case → camelCase |
| `risk_score` | `riskScore` | snake_case → camelCase |
| `risk_reasons` | `riskReasons` | snake_case → camelCase |

### Document.csv → Document.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `doc_type` | `docType` | snake_case → camelCase |
| `title` | `title` | Single word, unchanged |
| `content` | `content` | Single word, unchanged |
| `timestamp` | `timestamp` | Single word, unchanged |

### Transaction.csv → Transaction.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `amount` | `amount` | Single word, unchanged |
| `timestamp` | `timestamp` | Single word, unchanged |
| `txn_type` | `txnType` | snake_case → camelCase |

### GoldenRecord.csv → GoldenRecord.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_key` | `_key` | System field, unchanged |
| `canonical_name` | `canonicalName` | snake_case → camelCase |

### Edge Collections

#### hasAccount.csv → hasAccount.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |
| `ownership_type` | `ownershipType` | snake_case → camelCase |

#### transferredTo.csv → transferredTo.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |
| `amount` | `amount` | Single word, unchanged |
| `timestamp` | `timestamp` | Single word, unchanged |
| `txn_type` | `txnType` | snake_case → camelCase |
| `scenario` | `scenario` | Single word, unchanged |

#### relatedTo.csv → relatedTo.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |
| `relation_type` | `relationType` | snake_case → camelCase |

#### associatedWith.csv → associatedWith.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |
| `role` | `role` | Single word, unchanged |

#### residesAt.csv → residesAt.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |

#### accessedFrom.csv → accessedFrom.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |
| `access_timestamp` | `accessTimestamp` | snake_case → camelCase |
| `access_type` | `accessType` | snake_case → camelCase |

#### hasDigitalLocation.csv → hasDigitalLocation.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |

#### mentionedIn.csv → mentionedIn.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |
| `mention_type` | `mentionType` | snake_case → camelCase |
| `confidence` | `confidence` | Single word, unchanged |

#### registeredSale.csv → registeredSale.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |

#### buyerIn.csv → buyerIn.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |

#### sellerIn.csv → sellerIn.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |

#### resolvedTo.csv → resolvedTo.csv

| Current Header | Target Header | Notes |
|---------------|---------------|-------|
| `_from` | `_from` | System field, unchanged |
| `_to` | `_to` | System field, unchanged |

## Summary Statistics

- **Total files:** 23 CSVs
- **Vertices:** 11 files (snake_case → PascalCase)
- **Edges:** 12 files (snake_case → camelCase)
- **Fields requiring conversion:** ~40+ fields (snake_case → camelCase)
- **System fields unchanged:** 3 (`_key`, `_from`, `_to`)
- **Single-word fields unchanged:** ~15 fields (`name`, `city`, `state`, `balance`, `amount`, `timestamp`, `role`, `title`, `content`, `scenario`, `confidence`, etc.)
