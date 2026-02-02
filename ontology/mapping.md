# Ontology ↔ storage mapping (Phase 1)

This document is the authoritative mapping between ontology URIs and ArangoDB storage for Phase 1.

**Phase 1 convention:** storage names match the ontology naming:

- **Classes → vertex collections:** PascalCase
- **ObjectProperties → edge collections:** camelCase
- **DatatypeProperties → document fields:** camelCase

## Base URI / prefix

- **Base URI:** `http://www.semanticweb.org/fraud-intelligence#`
- **Prefix:** `fi:`

## Classes → collections

Collections match ontology class names (PascalCase):

| Ontology class | Collection |
| --- | --- |
| `fi:Person` | `Person` |
| `fi:Organization` | `Organization` |
| `fi:WatchlistEntity` | `WatchlistEntity` |
| `fi:BankAccount` | `BankAccount` |
| `fi:RealProperty` | `RealProperty` |
| `fi:Address` | `Address` |
| `fi:DigitalLocation` | `DigitalLocation` |
| `fi:Transaction` | `Transaction` |
| `fi:RealEstateTransaction` | `RealEstateTransaction` |
| `fi:Document` | `Document` |
| `fi:GoldenRecord` | `GoldenRecord` |

## Object properties → edge collections

| Ontology property | Edge collection |
| --- | --- |
| `fi:hasAccount` | `hasAccount` |
| `fi:transferredTo` | `transferredTo` |
| `fi:relatedTo` | `relatedTo` |
| `fi:associatedWith` | `associatedWith` |
| `fi:residesAt` | `residesAt` |
| `fi:accessedFrom` | `accessedFrom` |
| `fi:hasDigitalLocation` | `hasDigitalLocation` |
| `fi:mentionedIn` | `mentionedIn` |
| `fi:registeredSale` | `registeredSale` |
| `fi:buyerIn` | `buyerIn` |
| `fi:sellerIn` | `sellerIn` |
| `fi:resolvedTo` | `resolvedTo` |

## Datatype properties → stored fields

| Ontology URI | Stored field |
| --- | --- |
| `fi:riskScore` | `riskScore` |
| `fi:riskDirect` | `riskDirect` |
| `fi:riskInferred` | `riskInferred` |
| `fi:riskPath` | `riskPath` |
| `fi:riskReasons` | `riskReasons` |
| `fi:circleRateValue` | `circleRateValue` |
| `fi:marketValue` | `marketValue` |
| `fi:transactionValue` | `transactionValue` |
| `fi:txnType` | `txnType` |
| `fi:timestamp` | `timestamp` |
| `fi:amount` | `amount` |

