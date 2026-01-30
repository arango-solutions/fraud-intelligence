# Ontology ↔ storage mapping (Phase 1)

This document is the authoritative mapping between ontology URIs (camelCase) and stored ArangoDB fields (snake_case), plus how conceptual classes map to physical collections.

## Base URI / prefix

- **Base URI:** `http://www.semanticweb.org/fraud-intelligence#`
- **Prefix:** `fi:`

## Classes → collections

Collections are snake_case:

| Ontology class | Collection |
| --- | --- |
| `fi:Person` | `person` |
| `fi:Organization` | `organization` |
| `fi:WatchlistEntity` | `watchlist_entity` |
| `fi:BankAccount` | `bank_account` |
| `fi:RealProperty` | `real_property` |
| `fi:Address` | `address` |
| `fi:DigitalLocation` | `digital_location` |
| `fi:Transaction` | `transaction` |
| `fi:RealEstateTransaction` | `real_estate_transaction` |
| `fi:Document` | `document` |
| `fi:GoldenRecord` | `golden_record` |

## Object properties → edge collections

| Ontology property | Edge collection |
| --- | --- |
| `fi:has_account` | `has_account` |
| `fi:transferred_to` | `transferred_to` |
| `fi:related_to` | `related_to` |
| `fi:associated_with` | `associated_with` |
| `fi:resides_at` | `resides_at` |
| `fi:accessed_from` | `accessed_from` |
| `fi:has_digital_location` | `has_digital_location` |
| `fi:mentioned_in` | `mentioned_in` |
| `fi:registered_sale` | `registered_sale` |
| `fi:buyer_in` | `buyer_in` |
| `fi:seller_in` | `seller_in` |
| `fi:resolved_to` | `resolved_to` |

## Datatype properties → stored fields

| Ontology URI | Stored field |
| --- | --- |
| `fi:riskScore` | `risk_score` |
| `fi:riskDirect` | `risk_direct` |
| `fi:riskInferred` | `risk_inferred` |
| `fi:riskPath` | `risk_path` |
| `fi:riskReasons` | `risk_reasons` |
| `fi:circleRateValue` | `circle_rate_value` |
| `fi:marketValue` | `market_value` |
| `fi:transactionValue` | `transaction_value` |
| `fi:transactionType` | `txn_type` |
| `fi:timestamp` | `timestamp` |
| `fi:amount` | `amount` |

