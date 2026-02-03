#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict

from common import apply_config_to_env, get_arango_config, load_dotenv, sanitize_url

try:
    from arango import ArangoClient  # type: ignore
except Exception:  # pragma: no cover
    ArangoClient = None  # type: ignore


@dataclass
class RiskRunSummary:
    bank_accounts_updated: int
    persons_updated: int
    organizations_updated: int
    properties_updated: int
    real_estate_txs_updated: int
    golden_records_updated: int


def connect(cfg):
    if ArangoClient is None:  # pragma: no cover
        raise SystemExit("python-arango not installed. Install: pip install -r requirements.txt")
    return ArangoClient(hosts=cfg.url).db(cfg.database, username=cfg.username, password=cfg.password)


def aql_update_bank_account_direct(db) -> int:
    """
    Seed riskDirect on BankAccount from known fraud pattern tags.
    """
    q = """
WITH BankAccount, transferredTo
FOR a IN BankAccount
  LET muleIn = LENGTH(
    FOR e IN transferredTo
      FILTER e.scenario == "mule"
      FILTER e._to == a._id
      RETURN 1
  )
  LET muleOut = LENGTH(
    FOR e IN transferredTo
      FILTER e.scenario == "mule"
      FILTER e._from == a._id
      RETURN 1
  )
  LET cycleAny = LENGTH(
    FOR e IN transferredTo
      FILTER e.scenario == "cycle"
      FILTER e._from == a._id OR e._to == a._id
      LIMIT 1
      RETURN 1
  ) > 0

  LET direct = (
    muleIn >= 50 ? 95 :
    muleOut > 0 ? 80 :
    cycleAny ? 85 :
    0
  )

  LET reasons = UNIQUE(
    APPEND(
      (muleIn >= 50 ? ["mule_hub_inbound>=50"] : []),
      APPEND(
        (muleOut > 0 ? ["mule_source_outbound"] : []),
        (cycleAny ? ["circular_trading_cycle_participant"] : [])
      )
    )
  )

  UPDATE a WITH {
    riskDirect: direct,
    riskReasons: reasons
  } IN BankAccount

  COLLECT WITH COUNT INTO n
  RETURN n
"""
    return int(list(db.aql.execute(q))[0])


def aql_update_property_direct(db) -> Dict[str, int]:
    """
    Seed riskDirect on RealProperty + RealEstateTransaction based on undervaluation condition.
    """
    q_prop = """
WITH RealProperty, RealEstateTransaction, registeredSale
FOR e IN registeredSale
  LET p = DOCUMENT(e._from)
  LET tx = DOCUMENT(e._to)
  FILTER p != null && tx != null
  LET undervalued = (tx.transactionValue <= p.circleRateValue)
  FILTER undervalued
  UPDATE p WITH {
    riskDirect: 70,
    riskReasons: UNIQUE(APPEND(p.riskReasons ? p.riskReasons : [], ["undervalued_property"]))
  } IN RealProperty
  UPDATE tx WITH {
    riskDirect: 70,
    riskReasons: UNIQUE(APPEND(tx.riskReasons ? tx.riskReasons : [], ["undervalued_transaction"]))
  } IN RealEstateTransaction
  RETURN 1
"""
    updated = list(db.aql.execute(q_prop))
    return {"undervalued_edges": len(updated)}


def aql_update_person_org_direct(db) -> Dict[str, int]:
    """
    Seed riskDirect for Person/Organization based on:
    - owning risky accounts (hasAccount -> BankAccount)
    - buying/selling in undervalued transactions
    """
    q_person = """
WITH Person, hasAccount, BankAccount, buyerIn, sellerIn, RealEstateTransaction, RealProperty, registeredSale

// 1) direct from risky accounts
FOR p IN Person
  LET acctRisk = MAX(
    FOR ha IN hasAccount
      FILTER ha._from == p._id
      LET a = DOCUMENT(ha._to)
      FILTER a != null
      RETURN TO_NUMBER(a.riskDirect ? a.riskDirect : 0)
  )
  LET directFromAccounts = (acctRisk ? acctRisk : 0)

  // 2) direct from undervalued real estate involvement
  LET undervaluedParty = LENGTH(
    FOR bx IN buyerIn
      FILTER bx._from == p._id
      LET tx = DOCUMENT(bx._to)
      FILTER tx != null
      FOR rs IN registeredSale
        FILTER rs._to == tx._id
        LET prop = DOCUMENT(rs._from)
        FILTER prop != null
        FILTER tx.transactionValue <= prop.circleRateValue
        LIMIT 1
        RETURN 1
  ) > 0
  LET undervaluedParty2 = LENGTH(
    FOR sx IN sellerIn
      FILTER sx._from == p._id
      LET tx = DOCUMENT(sx._to)
      FILTER tx != null
      FOR rs IN registeredSale
        FILTER rs._to == tx._id
        LET prop = DOCUMENT(rs._from)
        FILTER prop != null
        FILTER tx.transactionValue <= prop.circleRateValue
        LIMIT 1
        RETURN 1
  ) > 0

  LET direct = MAX([directFromAccounts, (undervaluedParty || undervaluedParty2) ? 75 : 0])
  LET reasons = UNIQUE(APPEND(
    (directFromAccounts > 0 ? ["owns_high_risk_bank_account"] : []),
    ((undervaluedParty || undervaluedParty2) ? ["undervalued_property_party"] : [])
  ))

  UPDATE p WITH { riskDirect: direct, riskReasons: UNIQUE(APPEND(p.riskReasons ? p.riskReasons : [], reasons)) } IN Person
  COLLECT WITH COUNT INTO n
  RETURN n
"""

    q_org = """
WITH Organization, hasAccount, BankAccount
FOR o IN Organization
  LET acctRisk = MAX(
    FOR ha IN hasAccount
      FILTER ha._from == o._id
      LET a = DOCUMENT(ha._to)
      FILTER a != null
      RETURN TO_NUMBER(a.riskDirect ? a.riskDirect : 0)
  )
  LET direct = (acctRisk ? acctRisk : 0)
  LET reasons = UNIQUE(APPEND((direct > 0 ? ["organization_controls_high_risk_bank_account"] : []), []))
  UPDATE o WITH { riskDirect: direct, riskReasons: UNIQUE(APPEND(o.riskReasons ? o.riskReasons : [], reasons)) } IN Organization
  COLLECT WITH COUNT INTO n
  RETURN n
"""

    return {
        "persons_updated": int(list(db.aql.execute(q_person))[0]),
        "orgs_updated": int(list(db.aql.execute(q_org))[0]),
    }


def aql_update_inferred_risk(db) -> Dict[str, int]:
    """
    One-hop inferred risk for Person from high-risk neighbors.
    Uses decay factors: relatedTo=0.8, associatedWith=0.6
    """
    q = """
WITH Person, Organization, relatedTo, associatedWith
FOR p IN Person
  LET neighborRisks = (
    FOR v, e IN 1..1 ANY p relatedTo, associatedWith
      LET base = TO_NUMBER(v.riskScore ? v.riskScore : (v.riskDirect ? v.riskDirect : 0))
      LET decay = (
        IS_SAME_COLLECTION("relatedTo", e) ? 0.8 :
        IS_SAME_COLLECTION("associatedWith", e) ? 0.6 :
        0.5
      )
      RETURN base * decay
  )
  LET inferred = (LENGTH(neighborRisks) > 0 ? MIN([100, MAX(neighborRisks)]) : 0)
  UPDATE p WITH { riskInferred: inferred } IN Person
  COLLECT WITH COUNT INTO n
  RETURN n
"""
    persons = int(list(db.aql.execute(q))[0])
    return {"persons_updated": persons}


def aql_update_path_risk_bank_accounts(db, alpha: float, max_depth: int) -> int:
    """
    Multi-source outward propagation of path risk from high direct-risk seed accounts
    over transferredTo edges.
    """
    # IMPORTANT: AQL can error with "access after data-modification by traversal"
    # if we mix UPDATEs and traversals in the same query. Run as two phases:
    # (1) reset riskPath (no traversal), (2) traverse and collect updates, then apply.

    q_reset = """
WITH BankAccount
FOR a IN BankAccount
  UPDATE a WITH { riskPath: 0 } IN BankAccount
  RETURN 1
"""
    list(db.aql.execute(q_reset))

    q_propagate = """
WITH BankAccount, transferredTo
LET seeds = (
  FOR a IN BankAccount
    FILTER TO_NUMBER(a.riskDirect ? a.riskDirect : 0) >= 80
    RETURN a
)

LET updates = (
  FOR s IN seeds
    FOR v, e, p IN 1..@maxDepth OUTBOUND s transferredTo
      LET depth = LENGTH(p.edges)
      LET score = 100 * POW(@alpha, depth)
      RETURN { id: v._id, score: score }
)

FOR u IN updates
  COLLECT id = u.id AGGREGATE score = MAX(u.score)
  LET k = SPLIT(id, "/")[1]
  UPDATE { _key: k } WITH { riskPath: score } IN BankAccount
  RETURN 1
"""
    return int(len(list(db.aql.execute(q_propagate, bind_vars={"alpha": float(alpha), "maxDepth": int(max_depth)}))))


def aql_rollup_risk_person_from_accounts(db) -> int:
    q = """
WITH Person, hasAccount, BankAccount
FOR p IN Person
  LET path = MAX(
    FOR ha IN hasAccount
      FILTER ha._from == p._id
      LET a = DOCUMENT(ha._to)
      FILTER a != null
      RETURN TO_NUMBER(a.riskPath ? a.riskPath : 0)
  )
  UPDATE p WITH { riskPath: (path ? path : 0) } IN Person
  COLLECT WITH COUNT INTO n
  RETURN n
"""
    return int(list(db.aql.execute(q))[0])


def aql_rollup_total_risk(db) -> Dict[str, int]:
    """
    riskScore = MAX(direct, inferred, path) and ensure riskReasons is an array.
    """
    q_person = """
WITH Person
FOR p IN Person
  LET direct = TO_NUMBER(p.riskDirect ? p.riskDirect : 0)
  LET inf = TO_NUMBER(p.riskInferred ? p.riskInferred : 0)
  LET path = TO_NUMBER(p.riskPath ? p.riskPath : 0)
  LET total = MAX([direct, inf, path])
  UPDATE p WITH { riskScore: total, riskReasons: (IS_ARRAY(p.riskReasons) ? p.riskReasons : []) } IN Person
  COLLECT WITH COUNT INTO n
  RETURN n
"""
    q_org = """
WITH Organization
FOR o IN Organization
  LET direct = TO_NUMBER(o.riskDirect ? o.riskDirect : 0)
  LET inf = TO_NUMBER(o.riskInferred ? o.riskInferred : 0)
  LET path = TO_NUMBER(o.riskPath ? o.riskPath : 0)
  LET total = MAX([direct, inf, path])
  UPDATE o WITH { riskScore: total, riskReasons: (IS_ARRAY(o.riskReasons) ? o.riskReasons : []) } IN Organization
  COLLECT WITH COUNT INTO n
  RETURN n
"""
    q_acct = """
WITH BankAccount
FOR a IN BankAccount
  LET direct = TO_NUMBER(a.riskDirect ? a.riskDirect : 0)
  LET inf = TO_NUMBER(a.riskInferred ? a.riskInferred : 0)
  LET path = TO_NUMBER(a.riskPath ? a.riskPath : 0)
  LET total = MAX([direct, inf, path])
  UPDATE a WITH { riskScore: total, riskReasons: (IS_ARRAY(a.riskReasons) ? a.riskReasons : []) } IN BankAccount
  COLLECT WITH COUNT INTO n
  RETURN n
"""
    q_prop = """
WITH RealProperty
FOR p IN RealProperty
  LET direct = TO_NUMBER(p.riskDirect ? p.riskDirect : 0)
  LET inf = TO_NUMBER(p.riskInferred ? p.riskInferred : 0)
  LET path = TO_NUMBER(p.riskPath ? p.riskPath : 0)
  LET total = MAX([direct, inf, path])
  UPDATE p WITH { riskScore: total, riskReasons: (IS_ARRAY(p.riskReasons) ? p.riskReasons : []) } IN RealProperty
  COLLECT WITH COUNT INTO n
  RETURN n
"""
    q_tx = """
WITH RealEstateTransaction
FOR t IN RealEstateTransaction
  LET direct = TO_NUMBER(t.riskDirect ? t.riskDirect : 0)
  LET inf = TO_NUMBER(t.riskInferred ? t.riskInferred : 0)
  LET path = TO_NUMBER(t.riskPath ? t.riskPath : 0)
  LET total = MAX([direct, inf, path])
  UPDATE t WITH { riskScore: total, riskReasons: (IS_ARRAY(t.riskReasons) ? t.riskReasons : []) } IN RealEstateTransaction
  COLLECT WITH COUNT INTO n
  RETURN n
"""

    return {
        "persons": int(list(db.aql.execute(q_person))[0]),
        "orgs": int(list(db.aql.execute(q_org))[0]),
        "accounts": int(list(db.aql.execute(q_acct))[0]),
        "properties": int(list(db.aql.execute(q_prop))[0]),
        "real_estate_txs": int(list(db.aql.execute(q_tx))[0]),
    }


def aql_rollup_golden_record_risk(db) -> int:
    """
    GoldenRecord riskScore = MAX inbound Person riskScore.
    """
    q = """
WITH GoldenRecord, Person, resolvedTo
FOR g IN GoldenRecord
  LET s = MAX(
    FOR p IN Person
      FOR e IN resolvedTo
        FILTER e._from == p._id
        FILTER e._to == g._id
        RETURN TO_NUMBER(p.riskScore ? p.riskScore : 0)
  )
  UPDATE g WITH {
    riskScore: (s ? s : 0),
    riskReasons: UNIQUE(APPEND(g.riskReasons ? g.riskReasons : [], (s ? ["golden_record_rollup"] : [])))
  } IN GoldenRecord
  COLLECT WITH COUNT INTO n
  RETURN n
"""
    return int(list(db.aql.execute(q))[0])


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Phase 3: compute direct/inferred/path risk and persist risk fields.")
    p.add_argument("--mode", choices=["LOCAL", "REMOTE"], default=None, help="Override MODE from .env")
    p.add_argument("--alpha", type=float, default=0.5, help="Path risk decay per hop (0..1).")
    p.add_argument("--max-depth", type=int, default=3, help="Max traversal depth for path risk.")
    return p.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    cfg = get_arango_config(forced_mode=args.mode)
    apply_config_to_env(cfg)

    if not cfg.url:
        raise SystemExit("ARANGO_URL is not set")

    print(f"[phase3] risk mode={cfg.mode} arango={sanitize_url(cfg.url)} db={cfg.database}")
    db = connect(cfg)

    # Direct risk seeds
    bank_accounts_updated = aql_update_bank_account_direct(db)
    _ = aql_update_property_direct(db)
    po = aql_update_person_org_direct(db)

    # Inferred risk (1 hop)
    _ = aql_update_inferred_risk(db)

    # Path risk
    _ = aql_update_path_risk_bank_accounts(db, alpha=float(args.alpha), max_depth=int(args.max_depth))
    persons_updated = aql_rollup_risk_person_from_accounts(db)

    # Total risk rollup
    totals = aql_rollup_total_risk(db)
    golden_records_updated = aql_rollup_golden_record_risk(db)

    summary = RiskRunSummary(
        bank_accounts_updated=int(bank_accounts_updated),
        persons_updated=int(persons_updated),
        organizations_updated=int(totals["orgs"]),
        properties_updated=int(totals["properties"]),
        real_estate_txs_updated=int(totals["real_estate_txs"]),
        golden_records_updated=int(golden_records_updated),
    )

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "bank_accounts_updated": summary.bank_accounts_updated,
        "persons_updated": summary.persons_updated,
        "organizations_updated": summary.organizations_updated,
        "properties_updated": summary.properties_updated,
        "real_estate_txs_updated": summary.real_estate_txs_updated,
        "golden_records_updated": summary.golden_records_updated,
    }
    print(out)


if __name__ == "__main__":
    sys.exit(main())

