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
def test_phase3_risk_fields_written():
    if ArangoClient is None:
        pytest.skip("python-arango not installed")
    arango_url, username, password, db_name = _cfg()
    db = ArangoClient(hosts=arango_url).db(db_name, username=username, password=password)

    # At least some entities should have riskScore > 0.
    q = """
RETURN {
  persons: LENGTH(FOR p IN Person FILTER TO_NUMBER(p.riskScore ? p.riskScore : 0) > 0 RETURN 1),
  accounts: LENGTH(FOR a IN BankAccount FILTER TO_NUMBER(a.riskScore ? a.riskScore : 0) > 0 RETURN 1),
  golden: LENGTH(FOR g IN GoldenRecord FILTER TO_NUMBER(g.riskScore ? g.riskScore : 0) > 0 RETURN 1)
}
"""
    res = list(db.aql.execute(q))[0]
    assert res["persons"] > 0 or res["accounts"] > 0, f"expected some riskScore>0; got {res}"

    # riskReasons should be an array when present on Persons with riskScore>0.
    q2 = """
FOR p IN Person
  FILTER TO_NUMBER(p.riskScore ? p.riskScore : 0) > 0
  FILTER !IS_ARRAY(p.riskReasons)
  LIMIT 1
  RETURN p._id
"""
    bad = list(db.aql.execute(q2))
    assert not bad, f"expected riskReasons to be an array; found non-array on {bad[0]}"


@pytest.mark.integration
def test_phase3_patterns_still_detectable():
    if ArangoClient is None:
        pytest.skip("python-arango not installed")
    arango_url, username, password, db_name = _cfg()
    db = ArangoClient(hosts=arango_url).db(db_name, username=username, password=password)

    q = """
RETURN {
  cycle: LENGTH(FOR e IN transferredTo FILTER e.scenario == "cycle" RETURN 1),
  mule: LENGTH(FOR e IN transferredTo FILTER e.scenario == "mule" RETURN 1),
  undervalued: LENGTH(
    FOR e IN registeredSale
      LET p = DOCUMENT(e._from)
      LET tx = DOCUMENT(e._to)
      FILTER p != null && tx != null
      FILTER tx.transactionValue <= p.circleRateValue
      RETURN 1
  )
}
"""
    out = list(db.aql.execute(q))[0]
    assert out["cycle"] > 0, f"expected cycle edges > 0; got {out}"
    assert out["mule"] > 0, f"expected mule edges > 0; got {out}"
    assert out["undervalued"] > 0, f"expected undervalued > 0; got {out}"

