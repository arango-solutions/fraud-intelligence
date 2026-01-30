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

  // Vertex collections
  [
    "person",
    "organization",
    "watchlist_entity",
    "bank_account",
    "real_property",
    "address",
    "digital_location",
    "transaction",
    "real_estate_transaction",
    "document",
    "golden_record",
  ].forEach(ensureCollection);

  // Edge collections
  [
    "has_account",
    "transferred_to",
    "related_to",
    "associated_with",
    "resides_at",
    "accessed_from",
    "has_digital_location",
    "mentioned_in",
    "registered_sale",
    "buyer_in",
    "seller_in",
    "resolved_to",
  ].forEach(ensureEdgeCollection);

  // Indexes (idempotent)
  db.person.ensureIndex({ type: "persistent", fields: ["pan_number"], sparse: true });
  db.bank_account.ensureIndex({ type: "persistent", fields: ["account_number"], sparse: true });
  db.real_property.ensureIndex({ type: "persistent", fields: ["survey_number"], sparse: true });
  db.address.ensureIndex({ type: "persistent", fields: ["district", "state"] });

  db.transferred_to.ensureIndex({ type: "persistent", fields: ["timestamp"] });
  db.transferred_to.ensureIndex({ type: "persistent", fields: ["amount"] });

  print("schema bootstrap complete");
})();

