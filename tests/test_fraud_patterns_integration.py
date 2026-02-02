import os

import pytest

try:
    from arango import ArangoClient  # type: ignore
except Exception:  # pragma: no cover
    ArangoClient = None  # type: ignore


def _cfg():
    arango_url = os.getenv("ARANGO_URL")
    username = os.getenv("ARANGO_USERNAME")
    password = os.getenv("ARANGO_PASSWORD")
    db_name = os.getenv("ARANGO_DATABASE") or os.getenv("ARANGO_DB")
    if not (arango_url and username and password and db_name):
        pytest.skip("ARANGO_* env vars not set")
    return arango_url, username, password, db_name


@pytest.mark.integration
def test_cycle_exists_in_graph_after_ingest():
    if ArangoClient is None:
        pytest.skip("python-arango not installed")
    arango_url, username, password, db_name = _cfg()
    db = ArangoClient(hosts=arango_url).db(db_name, username=username, password=password)

    # Use scenario-tagged cycle edges and confirm a closed walk exists.
    q = """
WITH BankAccount, transferredTo
LET start = FIRST(
  FOR e IN transferredTo
    FILTER e.scenario == "cycle"
    RETURN e._from
)
FILTER start != null
FOR v, e, p IN 1..6 OUTBOUND start transferredTo
  FILTER e.scenario == "cycle"
  FILTER v._id == start
  LIMIT 1
  RETURN 1
"""
    res = list(db.aql.execute(q))
    assert res == [1], "expected at least one directed cycle in transferredTo edges"


@pytest.mark.integration
def test_mule_hub_and_shared_device_after_ingest():
    if ArangoClient is None:
        pytest.skip("python-arango not installed")
    arango_url, username, password, db_name = _cfg()
    db = ArangoClient(hosts=arango_url).db(db_name, username=username, password=password)

    # Hub receiving >= 50 mule transfers
    q_hub = """
FOR e IN transferredTo
  FILTER e.scenario == "mule"
  COLLECT hub = e._to WITH COUNT INTO n
  FILTER n >= 50
  LIMIT 1
  RETURN { hub, n }
"""
    hubs = list(db.aql.execute(q_hub))
    assert hubs and hubs[0]["n"] >= 50, "expected a mule hub receiving >= 50 transfers"

    # Mule accounts share a single digital location (accessedFrom edges)
    q_shared = """
LET muleFrom = UNIQUE(
  FOR e IN transferredTo
    FILTER e.scenario == "mule"
    RETURN e._from
)
LET devices = UNIQUE(
  FOR a IN accessedFrom
    FILTER a._from IN muleFrom
    RETURN a._to
)
RETURN LENGTH(devices)
"""
    devices = list(db.aql.execute(q_shared))
    assert devices == [1], f"expected 1 shared digital location; got {devices}"


@pytest.mark.integration
def test_undervalued_property_transaction_after_ingest():
    if ArangoClient is None:
        pytest.skip("python-arango not installed")
    arango_url, username, password, db_name = _cfg()
    db = ArangoClient(hosts=arango_url).db(db_name, username=username, password=password)

    q = """
FOR e IN registeredSale
  LET p = DOCUMENT(e._from)
  LET tx = DOCUMENT(e._to)
  FILTER p != null && tx != null
  FILTER tx.transactionValue <= p.circleRateValue
  LIMIT 1
  RETURN 1
"""
    res = list(db.aql.execute(q))
    assert res == [1], "expected at least one undervalued property transaction"

