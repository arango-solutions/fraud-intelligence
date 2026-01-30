# Schema contract (Phase 1)

**Source of truth:** `PRD/PRD.md` (canonical schema + naming)  
**Physical naming:** collections and fields are **snake_case** in ArangoDB.

---

## Collections (vertices)

| Collection | Required fields (Phase 1) |
| --- | --- |
| `person` | `_key`, `name`, `pan_number`, `aadhaar_masked`, `risk_score` |
| `organization` | `_key`, `name`, `org_type`, `risk_score` |
| `watchlist_entity` | `_key`, `name`, `listing_reason`, `risk_score`, `risk_direct`, `risk_reasons` |
| `bank_account` | `_key`, `account_number`, `account_type`, `balance`, `avg_monthly_balance`, `risk_score` |
| `real_property` | `_key`, `survey_number`, `district`, `state`, `pincode`, `circle_rate_value`, `market_value` |
| `address` | `_key`, `street`, `city`, `district`, `state`, `pincode`, `lat`, `long` |
| `digital_location` | `_key`, `ip_address`, `device_id`, `mac_address` |
| `transaction` | `_key`, `amount`, `timestamp`, `txn_type` |
| `real_estate_transaction` | `_key`, `transaction_value`, `timestamp`, `payment_method` |
| `document` | `_key`, `doc_type`, `title`, `content`, `timestamp` |
| `golden_record` | `_key`, `canonical_name` |

### Common risk fields (optional in Phase 1, present in outputs)

`risk_direct`, `risk_inferred`, `risk_path`, `risk_reasons`

---

## Edge collections

| Edge collection | Required fields |
| --- | --- |
| `has_account` | `_from`, `_to` |
| `transferred_to` | `_from`, `_to`, `amount`, `timestamp`, `txn_type` |
| `related_to` | `_from`, `_to`, `relation_type` |
| `associated_with` | `_from`, `_to`, `role` |
| `resides_at` | `_from`, `_to` |
| `accessed_from` | `_from`, `_to`, `access_timestamp`, `access_type` |
| `has_digital_location` | `_from`, `_to` |
| `mentioned_in` | `_from`, `_to`, `mention_type`, `confidence` |
| `registered_sale` | `_from`, `_to` |
| `buyer_in` | `_from`, `_to` |
| `seller_in` | `_from`, `_to` |
| `resolved_to` | `_from`, `_to` |

---

## Invariants

- **Keys**: `_key` unique within a collection
- **Edge references**: every `_from` / `_to` references an existing document `_id`
- **PAN format**: when present, `pan_number` matches `[A-Z]{5}[0-9]{4}[A-Z]{1}`
- **Amounts**: `amount > 0`, `transaction_value > 0`
- **Timestamps**: ISO-8601 strings
- **Risk scores**: within `[0, 100]` when present

