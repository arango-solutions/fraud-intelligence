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
def test_golden_records_populated_after_phase2():
    if ArangoClient is None:
        pytest.skip("python-arango not installed")
    arango_url, username, password, db_name = _cfg()
    db = ArangoClient(hosts=arango_url).db(db_name, username=username, password=password)

    q = "RETURN LENGTH(FOR g IN GoldenRecord RETURN 1)"
    res = list(db.aql.execute(q))
    assert res and res[0] > 0, "expected GoldenRecord to be populated (>0)"


@pytest.mark.integration
def test_at_least_one_golden_has_two_people_inbound():
    if ArangoClient is None:
        pytest.skip("python-arango not installed")
    arango_url, username, password, db_name = _cfg()
    db = ArangoClient(hosts=arango_url).db(db_name, username=username, password=password)

    q = """
FOR g IN GoldenRecord
  LET n = LENGTH(
    FOR v, e IN 1..1 INBOUND g resolvedTo
      FILTER IS_SAME_COLLECTION("Person", v)
      RETURN 1
  )
  FILTER n >= 2
  LIMIT 1
  RETURN n
"""
    res = list(db.aql.execute(q))
    assert res and res[0] >= 2, "expected at least one GoldenRecord with >=2 inbound resolvedTo edges from Person"


@pytest.mark.integration
def test_no_person_has_more_than_one_resolvedto_edge():
    if ArangoClient is None:
        pytest.skip("python-arango not installed")
    arango_url, username, password, db_name = _cfg()
    db = ArangoClient(hosts=arango_url).db(db_name, username=username, password=password)

    q = """
FOR p IN Person
  LET n = LENGTH(FOR e IN resolvedTo FILTER e._from == p._id RETURN 1)
  FILTER n > 1
  LIMIT 1
  RETURN { person: p._id, n }
"""
    bad = list(db.aql.execute(q))
    assert not bad, f"expected <=1 resolvedTo edge per Person; found: {bad[0]}"

