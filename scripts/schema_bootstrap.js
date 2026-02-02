/* eslint-disable */
// Fraud Intelligence schema bootstrap (Phase 1)
//
// Run (local):
//   arangosh --server.endpoint tcp://127.0.0.1:8529 --server.username root --server.password <pwd> \
//     --javascript.execute scripts/schema_bootstrap.js
//
// Or run via python ingest (recommended).

(function () {
  function ensureCollection(name) {
    if (!db._collection(name)) {
      db._create(name);
      print("created collection:", name);
    }
  }

  function ensureEdgeCollection(name) {
    if (!db._collection(name)) {
      db._createEdgeCollection(name);
      print("created edge collection:", name);
    }
  }

  // Vertex collections (PascalCase per PRD canonical schema)
  [
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
  ].forEach(ensureCollection);

  // Edge collections (camelCase per OWL ObjectProperties)
  [
    "hasAccount",
    "transferredTo",
    "relatedTo",
    "associatedWith",
    "residesAt",
    "accessedFrom",
    "hasDigitalLocation",
    "mentionedIn",
    "registeredSale",
    "buyerIn",
    "sellerIn",
    "resolvedTo",
  ].forEach(ensureEdgeCollection);

  // Indexes (idempotent)
  db.Person.ensureIndex({ type: "persistent", fields: ["panNumber"], sparse: true });
  db.BankAccount.ensureIndex({ type: "persistent", fields: ["accountNumber"], sparse: true });
  db.RealProperty.ensureIndex({ type: "persistent", fields: ["surveyNumber"], sparse: true });
  db.Address.ensureIndex({ type: "persistent", fields: ["district", "state"] });

  db.transferredTo.ensureIndex({ type: "persistent", fields: ["timestamp"] });
  db.transferredTo.ensureIndex({ type: "persistent", fields: ["amount"] });

  print("schema bootstrap complete");
})();

