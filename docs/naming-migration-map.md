# Naming migration map (snake_case → OWL conventions)

This project aligns ArangoDB collection names and document fields to OWL conventions:

- **Vertex collections**: PascalCase (OWL Classes)
- **Edge collections**: camelCase (OWL ObjectProperties)
- **Document fields**: camelCase (OWL DatatypeProperties)
- **Arango system fields**: `_key`, `_from`, `_to` (unchanged)

Database target: `fraud-intelligence` (never `_system` for application data).

## Collections

### Vertex collections

| Previous | Target |
| --- | --- |
| `person` | `Person` |
| `organization` | `Organization` |
| `watchlist_entity` | `WatchlistEntity` |
| `bank_account` | `BankAccount` |
| `real_property` | `RealProperty` |
| `address` | `Address` |
| `digital_location` | `DigitalLocation` |
| `transaction` | `Transaction` |
| `real_estate_transaction` | `RealEstateTransaction` |
| `document` | `Document` |
| `golden_record` | `GoldenRecord` |

### Edge collections

| Previous | Target |
| --- | --- |
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

## CSV filenames

CSV filenames must match collection names **exactly** (case-sensitive).

| Previous CSV | Target CSV |
| --- | --- |
| `person.csv` | `Person.csv` |
| `organization.csv` | `Organization.csv` |
| `watchlist_entity.csv` | `WatchlistEntity.csv` |
| `bank_account.csv` | `BankAccount.csv` |
| `real_property.csv` | `RealProperty.csv` |
| `address.csv` | `Address.csv` |
| `digital_location.csv` | `DigitalLocation.csv` |
| `transaction.csv` | `Transaction.csv` |
| `real_estate_transaction.csv` | `RealEstateTransaction.csv` |
| `document.csv` | `Document.csv` |
| `golden_record.csv` | `GoldenRecord.csv` |
| `has_account.csv` | `hasAccount.csv` |
| `transferred_to.csv` | `transferredTo.csv` |
| `related_to.csv` | `relatedTo.csv` |
| `associated_with.csv` | `associatedWith.csv` |
| `resides_at.csv` | `residesAt.csv` |
| `accessed_from.csv` | `accessedFrom.csv` |
| `has_digital_location.csv` | `hasDigitalLocation.csv` |
| `mentioned_in.csv` | `mentionedIn.csv` |
| `registered_sale.csv` | `registeredSale.csv` |
| `buyer_in.csv` | `buyerIn.csv` |
| `seller_in.csv` | `sellerIn.csv` |
| `resolved_to.csv` | `resolvedTo.csv` |

## Field names (examples)

| Previous field | Target field |
| --- | --- |
| `risk_score` | `riskScore` |
| `risk_direct` | `riskDirect` |
| `risk_inferred` | `riskInferred` |
| `risk_path` | `riskPath` |
| `risk_reasons` | `riskReasons` |
| `circle_rate_value` | `circleRateValue` |
| `market_value` | `marketValue` |
| `transaction_value` | `transactionValue` |
| `pan_number` | `panNumber` |
| `aadhaar_masked` | `aadhaarMasked` |
| `account_number` | `accountNumber` |
| `avg_monthly_balance` | `avgMonthlyBalance` |
| `ip_address` | `ipAddress` |
| `device_id` | `deviceId` |
| `mac_address` | `macAddress` |
| `access_timestamp` | `accessTimestamp` |
| `access_type` | `accessType` |
| `txn_type` | `txnType` |
| `payment_method` | `paymentMethod` |
| `survey_number` | `surveyNumber` |

Notes:
- Single-word fields like `name`, `amount`, `timestamp`, `city`, `district`, `state` remain unchanged.
- Edges keep `_from`/`_to` pointing to **PascalCase** vertex collection IDs, e.g. `Person/<_key>`.

