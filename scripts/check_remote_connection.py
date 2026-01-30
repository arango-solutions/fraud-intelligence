#!/usr/bin/env python3
"""
Read-only connectivity check for REMOTE ArangoDB.

This script performs safe, read-only checks to verify:
- Server reachability
- Authentication
- Database existence
- Basic AQL execution

Does not print secrets or perform any destructive operations.
"""

from __future__ import annotations

import sys
from typing import Dict, Any

from common import (
    ArangoConfig,
    apply_config_to_env,
    get_arango_config,
    load_dotenv,
    sanitize_url,
)

try:
    from arango import ArangoClient  # type: ignore
except Exception:  # pragma: no cover
    print("ERROR: python-arango not installed. Install dependencies:\n  pip install -r requirements.txt")
    sys.exit(1)


def check_connectivity(cfg: ArangoConfig) -> Dict[str, Any]:
    """
    Perform read-only connectivity checks.
    
    Returns a dictionary with check results (no secrets included).
    """
    results: Dict[str, Any] = {
        "mode": cfg.mode,
        "url": sanitize_url(cfg.url),
        "database": cfg.database,
        "username_length": len(cfg.username),
        "password_set": bool(cfg.password),
        "checks": {},
    }
    
    try:
        # Initialize client
        client = ArangoClient(hosts=cfg.url)
        
        # Check 1: Server version (read-only, no DB access needed)
        try:
            sys_db = client.db("_system", username=cfg.username, password=cfg.password)
            version_info = sys_db.version()
            results["checks"]["server_version"] = {
                "ok": True,
                "version": version_info.get("server", "unknown"),
                "license": version_info.get("license", "unknown"),
            }
        except Exception as e:
            results["checks"]["server_version"] = {
                "ok": False,
                "error": f"{type(e).__name__}: {str(e)}",
            }
            return results  # Can't proceed without _system access
        
        # Check 2: List accessible databases (read-only)
        try:
            databases = sys_db.databases()
            results["checks"]["list_databases"] = {
                "ok": True,
                "count": len(databases),
                "databases": databases,  # Safe to list database names
            }
        except Exception as e:
            results["checks"]["list_databases"] = {
                "ok": False,
                "error": f"{type(e).__name__}: {str(e)}",
            }
        
        # Check 3: Database existence (read-only check)
        try:
            db_exists = sys_db.has_database(cfg.database)
            results["checks"]["database_exists"] = {
                "ok": True,
                "exists": db_exists,
            }
        except Exception as e:
            results["checks"]["database_exists"] = {
                "ok": False,
                "error": f"{type(e).__name__}: {str(e)}",
            }
        
        # Check 4: If database exists, check collections (read-only)
        if results["checks"].get("database_exists", {}).get("exists"):
            try:
                db = client.db(cfg.database, username=cfg.username, password=cfg.password)
                collections = db.collections()
                collection_names = [c["name"] for c in collections if not c["name"].startswith("_")]
                results["checks"]["list_collections"] = {
                    "ok": True,
                    "count": len(collection_names),
                    "collections": collection_names,
                }
            except Exception as e:
                results["checks"]["list_collections"] = {
                    "ok": False,
                    "error": f"{type(e).__name__}: {str(e)}",
                }
            
            # Check 5: Simple AQL query (read-only)
            try:
                cursor = db.aql.execute("RETURN 1", count=True)
                result = list(cursor)
                results["checks"]["aql_execution"] = {
                    "ok": True,
                    "result": result[0] if result else None,
                }
            except Exception as e:
                results["checks"]["aql_execution"] = {
                    "ok": False,
                    "error": f"{type(e).__name__}: {str(e)}",
                }
        else:
            results["checks"]["list_collections"] = {
                "ok": False,
                "error": "Database does not exist",
            }
            results["checks"]["aql_execution"] = {
                "ok": False,
                "error": "Database does not exist",
            }
        
        # Overall status
        all_checks_ok = all(
            check.get("ok", False)
            for check in results["checks"].values()
            if isinstance(check, dict)
        )
        results["overall"] = "PASS" if all_checks_ok else "FAIL"
        
    except Exception as e:
        results["overall"] = "FAIL"
        results["error"] = f"{type(e).__name__}: {str(e)}"
    
    return results


def print_results(results: Dict[str, Any]) -> None:
    """Print check results in a readable format (no secrets)."""
    print("=" * 60)
    print("REMOTE ArangoDB Connectivity Check")
    print("=" * 60)
    print(f"Mode: {results['mode']}")
    print(f"URL: {results['url']}")
    print(f"Database: {results['database']}")
    print(f"Username length: {results['username_length']}")
    print(f"Password set: {results['password_set']}")
    print()
    
    checks = results.get("checks", {})
    
    # Server version
    if "server_version" in checks:
        sv = checks["server_version"]
        status = "✓" if sv.get("ok") else "✗"
        print(f"{status} Server Version")
        if sv.get("ok"):
            print(f"   Version: {sv.get('version', 'unknown')}")
            print(f"   License: {sv.get('license', 'unknown')}")
        else:
            print(f"   Error: {sv.get('error', 'unknown')}")
        print()
    
    # List databases
    if "list_databases" in checks:
        ld = checks["list_databases"]
        status = "✓" if ld.get("ok") else "✗"
        print(f"{status} List Databases")
        if ld.get("ok"):
            print(f"   Count: {ld.get('count', 0)}")
            if ld.get("databases"):
                print(f"   Databases: {', '.join(ld['databases'])}")
        else:
            print(f"   Error: {ld.get('error', 'unknown')}")
        print()
    
    # Database exists
    if "database_exists" in checks:
        de = checks["database_exists"]
        status = "✓" if de.get("ok") else "✗"
        print(f"{status} Database Exists")
        if de.get("ok"):
            exists = de.get("exists", False)
            print(f"   Database '{results['database']}' exists: {exists}")
            if not exists:
                print(f"   ⚠️  Database does not exist. It may be created during ingest.")
        else:
            print(f"   Error: {de.get('error', 'unknown')}")
        print()
    
    # List collections
    if "list_collections" in checks:
        lc = checks["list_collections"]
        status = "✓" if lc.get("ok") else "✗"
        print(f"{status} List Collections")
        if lc.get("ok"):
            print(f"   Count: {lc.get('count', 0)}")
            if lc.get("collections"):
                print(f"   Collections: {', '.join(lc['collections'][:10])}")
                if len(lc["collections"]) > 10:
                    print(f"   ... and {len(lc['collections']) - 10} more")
        else:
            print(f"   Error: {lc.get('error', 'unknown')}")
        print()
    
    # AQL execution
    if "aql_execution" in checks:
        ae = checks["aql_execution"]
        status = "✓" if ae.get("ok") else "✗"
        print(f"{status} AQL Execution")
        if ae.get("ok"):
            print(f"   Test query executed successfully")
        else:
            print(f"   Error: {ae.get('error', 'unknown')}")
        print()
    
    # Overall status
    overall = results.get("overall", "UNKNOWN")
    if overall == "PASS":
        print("=" * 60)
        print("✓ Overall Status: PASS - Ready for Phase 1")
        print("=" * 60)
    elif overall == "FAIL":
        print("=" * 60)
        print("✗ Overall Status: FAIL - Check errors above")
        print("=" * 60)
        if "error" in results:
            print(f"Fatal error: {results['error']}")
    else:
        print("=" * 60)
        print("? Overall Status: UNKNOWN")
        print("=" * 60)


def main() -> None:
    """Main entry point."""
    # Load .env without printing secrets
    load_dotenv()
    
    # Get REMOTE configuration
    cfg = get_arango_config(forced_mode="REMOTE")
    apply_config_to_env(cfg)
    
    # Validate required fields
    if not cfg.url:
        print("ERROR: ARANGO_URL is required for REMOTE mode")
        print("Set ARANGO_URL or ARANGO_ENDPOINT in your .env file")
        sys.exit(1)
    
    if not cfg.password:
        print("WARNING: ARANGO_PASSWORD is empty. Authentication may fail.")
        print("Set ARANGO_PASSWORD or ARANGO_PASS in your .env file")
    
    # Run connectivity checks
    results = check_connectivity(cfg)
    
    # Print results
    print_results(results)
    
    # Exit with appropriate code
    if results.get("overall") == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
