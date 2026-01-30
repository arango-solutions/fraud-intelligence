# Phase 1 Remote ArangoDB Run Checklist

**Goal:** Run Phase 1 validation against a REMOTE managed ArangoDB instance safely.

**Constraints:**
- Do not read or print `.env` contents
- No destructive operations unless explicitly requested
- Read-only connectivity checks before any writes

---

## 1. Required Environment Variables for REMOTE Mode

The runner expects the following environment variables when `MODE=REMOTE`:

### Primary Variables (Preferred)
- `MODE=REMOTE` (or `ARANGO_MODE=REMOTE`)
- `ARANGO_URL` (or `ARANGO_ENDPOINT`) - **REQUIRED** - Full URL (e.g., `https://your-instance.arangodb.cloud:8529`)
- `ARANGO_USERNAME` (or `ARANGO_USER`) - Defaults to `"root"` if not set
- `ARANGO_PASSWORD` (or `ARANGO_PASS`) - **REQUIRED** - Empty string if not set (may cause auth failures)
- `ARANGO_DATABASE` (or `ARANGO_DB`) - Defaults to `"fraud_intelligence"` if not set

### Optional Variables
- `ARANGO_VERIFY_SSL` - Currently not implemented in code, but documented in `.env.example` (would need code changes to use)

### Variable Resolution Logic
When `MODE=REMOTE`:
1. Uses `ARANGO_URL` / `ARANGO_ENDPOINT` (non-LOCAL prefixed vars)
2. Falls back to `LOCAL_ARANGO_*` vars if non-LOCAL vars are missing
3. Defaults: username=`"root"`, database=`"fraud_intelligence"`, password=`""`

**Note:** The code in `scripts/common.py:get_arango_config()` handles this resolution.

---

## 2. Read-Only Connectivity Check Query

Before running Phase 1, execute this read-only check to verify connectivity:

```python
# Minimal connectivity check (read-only)
# This can be run via Python script or arangosh

from arango import ArangoClient
import os

url = os.getenv("ARANGO_URL")
username = os.getenv("ARANGO_USERNAME", "root")
password = os.getenv("ARANGO_PASSWORD", "")
database = os.getenv("ARANGO_DATABASE", os.getenv("ARANGO_DB", "fraud_intelligence"))

try:
    client = ArangoClient(hosts=url)
    sys_db = client.db("_system", username=username, password=password)
    
    # Check 1: Server version (read-only, no DB access needed)
    version = sys_db.version()
    print(f"✓ Server version: {version.get('server', 'unknown')}")
    
    # Check 2: Database exists (read-only check)
    db_exists = sys_db.has_database(database)
    print(f"✓ Database '{database}' exists: {db_exists}")
    
    # Check 3: List databases (read-only, shows accessible DBs)
    dbs = sys_db.databases()
    print(f"✓ Accessible databases: {len(dbs)} found")
    
    # Check 4: If database exists, check collections (read-only)
    if db_exists:
        db = client.db(database, username=username, password=password)
        collections = db.collections()
        print(f"✓ Database '{database}' has {len(collections)} collections")
        
        # Check 5: Simple AQL query (read-only)
        result = db.aql.execute("RETURN 1", count=True)
        print(f"✓ AQL execution test: PASS")
    
    print("\n✓ All connectivity checks passed")
    
except Exception as e:
    print(f"✗ Connectivity check failed: {type(e).__name__}: {str(e)}")
    raise
```

**Or via AQL (arangosh/UI):**
```aql
// Read-only checks
RETURN VERSION()  // Server version
RETURN LENGTH(DATABASES())  // Count accessible databases
RETURN LENGTH(COLLECTIONS())  // Count collections in current DB
RETURN 1  // Simple execution test
```

---

## 3. Failure Modes & Diagnosis (Without Printing Secrets)

### 3.1 Authentication Failures

**Symptoms:**
- `ArangoServerError: [HTTP 401][ERR 401] Not authorized`
- `ArangoServerError: [HTTP 403][ERR 403] Forbidden`

**Diagnosis Steps:**
1. Check if `ARANGO_USERNAME` is set correctly (sanitize for logging: show only first/last char or length)
2. Check if `ARANGO_PASSWORD` is non-empty (check length, not value)
3. Verify URL format doesn't include credentials in the URL itself
4. Test with `_system` database first (lower privilege requirement)

**Evidence to Record:**
- `len(ARANGO_USERNAME)` (not the value)
- `ARANGO_PASSWORD` is set: `True/False` (not the value)
- `sanitize_url(ARANGO_URL)` (URL with credentials redacted)
- Error message type (401 vs 403)
- Whether `_system` database access works

**Code Reference:** `scripts/common.py:sanitize_url()` already handles URL sanitization.

---

### 3.2 Database Name Mismatch

**Symptoms:**
- `ArangoServerError: [HTTP 404][ERR 1207] database not found`
- `Database {db_name} does not exist and could not be created: {e}`

**Diagnosis Steps:**
1. List accessible databases (read-only operation)
2. Compare expected database name with actual available databases
3. Check if database name has case sensitivity issues
4. Verify if database creation is permitted (managed instances often deny this)

**Evidence to Record:**
- Expected database name: `ARANGO_DATABASE` value
- List of accessible databases (from `sys_db.databases()`)
- Whether database creation was attempted and failed
- Error message indicating permission denied vs not found

**Code Reference:** `scripts/ingest.py:196-204` attempts database creation if missing.

---

### 3.3 TLS/SSL Certificate Issues

**Symptoms:**
- `SSL: CERTIFICATE_VERIFY_FAILED`
- `urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]>`
- Connection timeout or handshake failures

**Diagnosis Steps:**
1. Check if `ARANGO_URL` uses `https://` scheme
2. Verify certificate chain (without printing cert details)
3. Check if `ARANGO_VERIFY_SSL` is set (currently not implemented in code)
4. Test with `curl` or `openssl s_client` to verify certificate validity separately

**Evidence to Record:**
- URL scheme: `http://` vs `https://`
- `ARANGO_VERIFY_SSL` value (if set)
- SSL error type (certificate verify failed, handshake failure, etc.)
- Whether the issue occurs during initial connection vs during queries

**Note:** Current code (`scripts/test_phase1.py:60`, `scripts/ingest.py:193`) doesn't pass SSL verification parameters to `ArangoClient()`. The `python-arango` library may use system defaults. Managed ArangoDB instances typically require proper SSL verification.

**Potential Fix Needed:**
```python
# If ARANGO_VERIFY_SSL is needed, would require code changes:
verify = os.getenv("ARANGO_VERIFY_SSL", "true").lower() == "true"
client = ArangoClient(
    hosts=url,
    verify=verify  # This parameter may need to be added
)
```

---

### 3.4 Network Connectivity Issues

**Symptoms:**
- `ConnectionError`, `TimeoutError`
- `urllib.error.URLError: <urlopen error [Errno 8] nodename nor servname provided>`
- `wait_for_http_ok()` timeout

**Diagnosis Steps:**
1. Test basic HTTP connectivity to `ARANGO_URL/_api/version` (without auth)
2. Check DNS resolution (hostname resolves correctly)
3. Verify firewall/network rules allow outbound connections
4. Check if port is correct (default 8529, but managed instances may differ)

**Evidence to Record:**
- Hostname from URL (parsed, not full URL)
- Port number (if specified)
- DNS resolution: `True/False` (can resolve hostname)
- HTTP reachability: `True/False` (can reach `/_api/version` endpoint)
- Timeout duration if applicable

**Code Reference:** `scripts/common.py:wait_for_http_ok()` tests basic HTTP connectivity.

---

### 3.5 Permission/Authorization Issues

**Symptoms:**
- Database creation fails: `[HTTP 403] Forbidden`
- Collection creation fails: `[HTTP 403] Forbidden`
- AQL execution fails: `[HTTP 403] Forbidden`

**Diagnosis Steps:**
1. Test read-only operations first (list databases, list collections)
2. Verify if database creation is permitted (managed instances often restrict this)
3. Check if user has write permissions on the target database
4. Verify if collections can be created (vs. must pre-exist)

**Evidence to Record:**
- Can list databases: `True/False`
- Can list collections: `True/False`
- Can create database: `True/False` (if attempted)
- Can create collection: `True/False` (if attempted)
- Can execute AQL: `True/False`
- Specific permission error codes/messages (403 vs 401)

---

## 4. Actionable Checklist for Remote Run

### Pre-Flight Checks (Before Running Phase 1)

- [ ] **Set MODE=REMOTE**
  - Verify: `MODE=REMOTE` or `ARANGO_MODE=REMOTE` is set
  - Evidence: Log `MODE` value (should be "REMOTE")

- [ ] **Verify Required Environment Variables**
  - Check: `ARANGO_URL` is set and non-empty
  - Check: `ARANGO_PASSWORD` is set and non-empty (check length > 0, not value)
  - Check: `ARANGO_USERNAME` is set (defaults to "root" if missing)
  - Check: `ARANGO_DATABASE` is set (defaults to "fraud_intelligence" if missing)
  - Evidence: Log variable names that are set (not values), and lengths where applicable

- [ ] **Sanitize URL for Logging**
  - Use `sanitize_url()` function to log URL without credentials
  - Evidence: Log sanitized URL format

- [ ] **Run Read-Only Connectivity Check**
  - Execute connectivity check script (Section 2)
  - Verify: Server version retrieved
  - Verify: Database exists or can be created
  - Verify: AQL execution works
  - Evidence: Record pass/fail for each check

### Phase 1 Execution

- [ ] **Run Phase 1 with Remote-Only Flag**
  ```bash
  python scripts/test_phase1.py --remote-only --data-dir data/sample
  ```
  - This skips LOCAL mode and Docker setup
  - Uses `MODE=REMOTE` configuration

- [ ] **Monitor for Failure Modes**
  - Watch for authentication errors (401/403)
  - Watch for database not found errors (404)
  - Watch for SSL/TLS errors
  - Watch for network connectivity errors
  - Watch for permission errors

- [ ] **Record Evidence for Each Step**
  - `generate`: PASS/FAIL
  - `ingest`: PASS/FAIL (with error details if failed)
  - `pytest`: PASS/FAIL
  - `pytest_integration`: PASS/FAIL
  - `smoke_queries`: PASS/FAIL (with query index if failed)

### Post-Run Validation

- [ ] **Check Validation Report**
  - Review `docs/phase1-validation-report.md`
  - Verify REMOTE section is populated
  - Check collection counts if smoke queries passed

- [ ] **Document Any Issues**
  - Record failure mode category (auth, DB name, TLS, network, permissions)
  - Record sanitized diagnostic information
  - Note any required code changes (e.g., SSL verification support)

---

## 5. Evidence to Record (Without Secrets)

### Connection Configuration Evidence
- Mode: `LOCAL` or `REMOTE`
- Sanitized URL: `https://hostname:port` (no credentials)
- Database name: `fraud_intelligence` (or configured value)
- Username length: `len(username)` (not the username itself)
- Password is set: `True/False` (not the password)

### Connectivity Evidence
- Server version: `{version}` (from `/_api/version`)
- Database exists: `True/False`
- Accessible databases count: `{count}`
- Collections count: `{count}` (if database exists)
- AQL execution test: `PASS/FAIL`

### Failure Evidence
- Error type: `{exception_type}`
- Error message: `{sanitized_message}` (redact any credentials)
- HTTP status code: `{code}` (if applicable)
- Failure step: `{step_name}` (generate, ingest, pytest, etc.)

### Phase 1 Results Evidence
- Each step status: `PASS/FAIL`
- Collection counts: `{collection_name}: {count}` (if ingest succeeded)
- Smoke query results: `PASS/FAIL` (with query index if failed)

---

## 6. Safe Diagnostic Commands

### Check Environment Variables (Without Printing Secrets)
```bash
# Check which variables are set (not their values)
env | grep -E "^ARANGO_|^MODE=" | sed 's/=.*/=***/' | sort

# Check URL format (sanitized)
python3 -c "from scripts.common import get_arango_config, sanitize_url, load_dotenv; load_dotenv(); cfg = get_arango_config('REMOTE'); print(f'URL: {sanitize_url(cfg.url)}'); print(f'DB: {cfg.database}'); print(f'Mode: {cfg.mode}')"
```

### Test Basic Connectivity (Read-Only)
```bash
# Test HTTP endpoint (no auth required for /_api/version)
curl -s -o /dev/null -w "%{http_code}" "$ARANGO_URL/_api/version"

# Test with Python connectivity check
python3 scripts/test_connectivity.py  # (would need to create this)
```

### Verify Database Exists (Read-Only)
```python
# Minimal script to check database existence
from arango import ArangoClient
import os
from scripts.common import load_dotenv, get_arango_config

load_dotenv()
cfg = get_arango_config("REMOTE")
client = ArangoClient(hosts=cfg.url)
sys_db = client.db("_system", username=cfg.username, password=cfg.password)
print(f"Database exists: {sys_db.has_database(cfg.database)}")
```

---

## 7. Notes on Current Implementation

### SSL Verification
- `ARANGO_VERIFY_SSL` is documented in `.env.example` but **not currently implemented** in code
- `ArangoClient()` is instantiated without SSL verification parameters
- Managed ArangoDB instances typically require proper SSL verification
- **Action Needed:** May need to add SSL verification support if TLS errors occur

### Database Creation
- `scripts/ingest.py` attempts to create database if it doesn't exist
- Managed instances may deny database creation
- **Safe Behavior:** Script will fail gracefully with clear error message

### Force Flag
- `--force` flag in ingest truncates collections (destructive)
- Phase 1 runner uses `--remote-force` flag to allow `--force` in REMOTE mode
- **Default Behavior:** Without `--force`, ingest skips collections that already have data

---

## 8. Quick Reference: Environment Variable Priority

For `MODE=REMOTE`, variables are resolved in this order:

1. **URL:** `ARANGO_URL` → `ARANGO_ENDPOINT` → `LOCAL_ARANGO_URL` → `""`
2. **Username:** `ARANGO_USERNAME` → `ARANGO_USER` → `"root"`
3. **Password:** `ARANGO_PASSWORD` → `ARANGO_PASS` → `""`
4. **Database:** `ARANGO_DATABASE` → `ARANGO_DB` → `LOCAL_ARANGO_DATABASE` → `LOCAL_ARANGO_DB` → `"fraud_intelligence"`

**Code Location:** `scripts/common.py:get_arango_config()` lines 107-114
