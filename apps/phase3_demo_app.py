#!/usr/bin/env python3
from __future__ import annotations

"""
Phase 3 MVP "Three Lenses" demo app.

This app is intentionally lightweight and reads directly from ArangoDB.
It avoids printing secrets and relies on existing config helpers.
"""

import sys


def _require_streamlit():
    try:
        import streamlit as st  # type: ignore

        return st
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Streamlit is not installed.\n"
            "Install dependencies (REMOTE demo):\n"
            "  pip install -r requirements.txt\n"
        ) from e


def main() -> None:
    st = _require_streamlit()

    import os

    sys.path.insert(0, "scripts")
    from common import apply_config_to_env, get_arango_config, load_dotenv, sanitize_url

    try:
        from arango import ArangoClient  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit("python-arango not installed. Install: pip install -r requirements.txt") from e

    load_dotenv()
    cfg = get_arango_config(forced_mode=os.getenv("MODE") or None)
    apply_config_to_env(cfg)

    st.set_page_config(page_title="Fraud Intelligence Demo (Phase 3)", layout="wide")
    st.title("Fraud Intelligence Demo — Phase 3 (MVP)")
    st.caption(f"mode={cfg.mode} arango={sanitize_url(cfg.url)} db={cfg.database}")

    db = ArangoClient(hosts=cfg.url).db(cfg.database, username=cfg.username, password=cfg.password)

    tabs = st.tabs(["Investigator", "Analyst", "Executive"])

    with tabs[0]:
        st.subheader("Investigator lens")
        st.write("Pick an entity and inspect its risk + key neighbors. Use Visualizer for deep graph exploration.")

        entity_type = st.selectbox("Entity type", ["Person", "GoldenRecord", "BankAccount"])
        query = st.text_input("Search (prefix match on key/name where available)", "")

        if entity_type == "Person":
            q = """
FOR p IN Person
  FILTER @q == "" OR LIKE(LOWER(p.name), CONCAT(LOWER(@q), "%"), true) OR LIKE(p._key, CONCAT(@q, "%"), true)
  SORT p.riskScore DESC
  LIMIT 50
  RETURN { _id: p._id, name: p.name, panNumber: p.panNumber, riskScore: p.riskScore, riskReasons: p.riskReasons }
"""
        elif entity_type == "GoldenRecord":
            q = """
FOR g IN GoldenRecord
  FILTER @q == "" OR LIKE(LOWER(g._key), CONCAT(LOWER(@q), "%"), true) OR LIKE(LOWER(g.name), CONCAT(LOWER(@q), "%"), true)
  SORT g.riskScore DESC
  LIMIT 50
  RETURN { _id: g._id, _key: g._key, riskScore: g.riskScore, riskReasons: g.riskReasons }
"""
        else:
            q = """
FOR a IN BankAccount
  FILTER @q == "" OR LIKE(a.accountNumber, CONCAT(@q, "%"), true) OR LIKE(a._key, CONCAT(@q, "%"), true)
  SORT a.riskScore DESC
  LIMIT 50
  RETURN { _id: a._id, accountNumber: a.accountNumber, accountType: a.accountType, riskScore: a.riskScore, riskReasons: a.riskReasons }
"""

        rows = list(db.aql.execute(q, bind_vars={"q": query}))
        st.dataframe(rows, use_container_width=True)

        st.write("Tip: copy an `_id` and open it in the ArangoDB Visualizer (KnowledgeGraph) for evidence paths.")

    with tabs[1]:
        st.subheader("Analyst lens")

        q_stats = """
RETURN {
  cycleEdges: LENGTH(FOR e IN transferredTo FILTER e.scenario == "cycle" RETURN 1),
  muleEdges: LENGTH(FOR e IN transferredTo FILTER e.scenario == "mule" RETURN 1),
  undervalued: LENGTH(
    FOR e IN registeredSale
      LET p = DOCUMENT(e._from)
      LET tx = DOCUMENT(e._to)
      FILTER p != null && tx != null
      FILTER tx.transactionValue <= p.circleRateValue
      RETURN 1
  ),
  highRiskPeople: LENGTH(FOR p IN Person FILTER TO_NUMBER(p.riskScore ? p.riskScore : 0) >= 80 RETURN 1)
}
"""
        st.json(list(db.aql.execute(q_stats))[0])

        q_hubs = """
FOR e IN transferredTo
  FILTER e.scenario == "mule"
  COLLECT hub = e._to WITH COUNT INTO n
  SORT n DESC
  LIMIT 10
  RETURN { hub, inboundMuleTransfers: n }
"""
        st.write("Top mule hubs")
        st.dataframe(list(db.aql.execute(q_hubs)), use_container_width=True)

    with tabs[2]:
        st.subheader("Executive lens")
        st.write("Aggregate risk by district (from Address/RealProperty).")

        q = """
LET personDistrict = (
  FOR p IN Person
    LET d = FIRST(
      FOR e IN residesAt
        FILTER e._from == p._id
        LET a = DOCUMENT(e._to)
        FILTER a != null
        RETURN a.district
    )
    FILTER d != null
    RETURN { district: d, risk: TO_NUMBER(p.riskScore ? p.riskScore : 0) }
)
FOR row IN personDistrict
  COLLECT district = row.district AGGREGATE
    avgRisk = AVG(row.risk),
    maxRisk = MAX(row.risk),
    n = COUNT(row)
  SORT avgRisk DESC
  LIMIT 25
  RETURN { district, avgRisk, maxRisk, count: n }
"""
        st.dataframe(list(db.aql.execute(q)), use_container_width=True)


if __name__ == "__main__":
    main()

