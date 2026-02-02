import os

import pytest

try:
    from arango import ArangoClient  # type: ignore
except Exception:  # pragma: no cover
    ArangoClient = None  # type: ignore


REQUIRED_COLLECTIONS = [
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
]


@pytest.mark.integration
def test_required_collections_exist_after_ingest():
    if ArangoClient is None:
        pytest.skip("python-arango not installed")

    arango_url = os.getenv("ARANGO_URL")
    username = os.getenv("ARANGO_USERNAME")
    password = os.getenv("ARANGO_PASSWORD")
    db_name = os.getenv("ARANGO_DATABASE") or os.getenv("ARANGO_DB")
    if not (arango_url and username and password and db_name):
        pytest.skip("ARANGO_* env vars not set")

    client = ArangoClient(hosts=arango_url)
    db = client.db(db_name, username=username, password=password)
    existing = {c["name"] for c in db.collections()}
    missing = [c for c in REQUIRED_COLLECTIONS if c not in existing]
    assert not missing, f"missing collections: {missing}"

