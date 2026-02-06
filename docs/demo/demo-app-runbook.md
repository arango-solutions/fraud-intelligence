## Streamlit MVP app runbook (Phase 3 “Three Lenses”)

### Prerequisites

- Python deps installed:

```bash
pip install -r requirements.txt
```

- `.env` configured for the devops-managed cluster (do not paste secrets).

### Run (REMOTE)

```bash
streamlit run apps/phase3_demo_app.py
```

### What to show

- **Investigator tab**
  - Search for an entity (e.g., `Victor Tella`)
  - Show `riskScore` + `riskReasons`
  - Use this to bridge into the Visualizer flow (pivot to accounts, then run cycle action)

- **Analyst tab**
  - Highlight pattern stats (cycles/mules/undervalued)
  - Explain: “these are the measurable signals we monitor continuously”

- **Executive tab**
  - Show district-level summary / risk concentration
  - Explain: “resource allocation, hotspot monitoring, and reporting”

### Troubleshooting

- **Connection fails**
  - Confirm `MODE=REMOTE` and required env keys exist (`ARANGO_URL`, `ARANGO_DATABASE`, `ARANGO_USERNAME`, `ARANGO_PASSWORD`).
  - Run: `python scripts/test_phase3.py --remote-only` to validate connectivity and data.

- **Empty results**
  - Data/ER/risk may not have been run yet; run Phase 1–3:

```bash
python scripts/test_phase1.py --remote-only --install-visualizer
python scripts/test_phase2.py --remote-only
python scripts/test_phase3.py --remote-only
```

# Demo App Runbook

This runbook describes how to run and use the Phase 3 Streamlit MVP demo application.

## Prerequisites

### Required Packages

Ensure the following Python packages are installed:

```bash
pip install -r requirements.txt
```

The app specifically requires:
- `streamlit` - Web framework for the demo interface
- `python-arango` - ArangoDB client library

### Environment Configuration

The app reads configuration from environment variables. Ensure your `.env` file is properly configured:

- `MODE` - Set to `LOCAL` or `REMOTE` (defaults to `LOCAL` if not set)
- `ARANGO_URL` / `ARANGO_ENDPOINT` - ArangoDB server URL
- `ARANGO_USERNAME` / `ARANGO_USER` - Database username
- `ARANGO_PASSWORD` / `ARANGO_PASS` - Database password
- `ARANGO_DATABASE` / `ARANGO_DB` - Database name (defaults to `fraud-intelligence`)

For LOCAL mode, you can also use:
- `LOCAL_ARANGO_URL` / `LOCAL_ARANGO_ENDPOINT`
- `LOCAL_ARANGO_USERNAME` / `LOCAL_ARANGO_USER`
- `LOCAL_ARANGO_PASSWORD` / `LOCAL_ARANGO_PASS`
- `LOCAL_ARANGO_DATABASE` / `LOCAL_ARANGO_DB`

**Note:** The app sanitizes URLs before displaying them and never prints credentials.

### Database Requirements

The app expects the following collections to exist and contain data:
- `Person` - Person entities with risk scores
- `GoldenRecord` - Resolved identity records
- `BankAccount` - Bank account entities
- `Address` - Address entities
- `transferredTo` - Transaction edges (with `scenario` field)
- `registeredSale` - Property sale edges
- `residesAt` - Person-to-address relationships

Ensure Phase 3 analytics and risk scoring have been run to populate risk scores:
```bash
python scripts/phase3_analytics.py --mode REMOTE
python scripts/phase3_risk.py --mode REMOTE
```

## Running the App

### Basic Usage

From the repository root directory:

```bash
streamlit run apps/phase3_demo_app.py
```

The app will:
1. Load environment variables from `.env`
2. Connect to ArangoDB using the configured mode (LOCAL or REMOTE)
3. Start a Streamlit server (typically on `http://localhost:8501`)
4. Open your default web browser automatically

### Command Line Options

You can pass standard Streamlit options:

```bash
# Run on a specific port
streamlit run apps/phase3_demo_app.py --server.port 8502

# Disable auto-open browser
streamlit run apps/phase3_demo_app.py --server.headless true

# Run with specific theme
streamlit run apps/phase3_demo_app.py --theme.base dark
```

### Environment Override

You can override the mode at runtime:

```bash
MODE=REMOTE streamlit run apps/phase3_demo_app.py
```

## Application Tabs

The app provides three "lenses" for different user personas:

### 1. Investigator Tab

**Purpose:** Entity-level investigation with risk context

**Features:**
- Entity type selector: Choose from `Person`, `GoldenRecord`, or `BankAccount`
- Search box: Prefix match on entity key or name fields
- Results table: Displays up to 50 entities sorted by risk score (descending)

**Displayed Fields:**

For `Person`:
- `_id` - Document identifier (use this in Visualizer)
- `name` - Person's name
- `panNumber` - PAN number
- `riskScore` - Computed risk score
- `riskReasons` - Array of risk reason strings

For `GoldenRecord`:
- `_id` - Document identifier
- `_key` - Record key
- `riskScore` - Aggregated risk score
- `riskReasons` - Combined risk reasons

For `BankAccount`:
- `_id` - Document identifier
- `accountNumber` - Account number
- `accountType` - Account type
- `riskScore` - Computed risk score
- `riskReasons` - Array of risk reason strings

**Usage Tips:**
- Copy an `_id` value from the table
- Open ArangoDB Visualizer (KnowledgeGraph view)
- Paste the `_id` to explore connected entities and evidence paths
- Use the search box to filter by name, PAN, or account number

### 2. Analyst Tab

**Purpose:** Pattern detection and aggregate statistics

**Features:**

**Pattern Statistics (JSON):**
- `cycleEdges` - Count of circular trading edges (`transferredTo.scenario == "cycle"`)
- `muleEdges` - Count of money mule edges (`transferredTo.scenario == "mule"`)
- `undervalued` - Count of undervalued property sales (`transactionValue <= circleRateValue`)
- `highRiskPeople` - Count of persons with risk score >= 80

**Top Mule Hubs Table:**
- Lists up to 10 accounts receiving the most money mule transfers
- Columns:
  - `hub` - Account document ID receiving transfers
  - `inboundMuleTransfers` - Count of mule scenario transfers received

**Usage Tips:**
- Monitor pattern counts to understand fraud scale
- Identify high-value investigation targets from mule hub list
- Use hub IDs in Visualizer to explore mule network structure

### 3. Executive Tab

**Purpose:** High-level risk aggregation by geographic district

**Features:**
- District-level risk aggregation table
- Up to 25 districts sorted by average risk (descending)

**Displayed Fields:**
- `district` - District name (from `Address.district`)
- `avgRisk` - Average risk score for persons in this district
- `maxRisk` - Maximum risk score in this district
- `count` - Number of persons residing in this district

**Data Source:**
- Aggregates `Person` entities via `residesAt` → `Address` relationships
- Only includes persons with valid district assignments

**Usage Tips:**
- Identify high-risk geographic areas for resource allocation
- Use district names to filter investigations
- Combine with Analyst tab insights for comprehensive risk assessment

## Troubleshooting

### App Won't Start

**Error:** `Streamlit is not installed`

**Solution:**
```bash
pip install streamlit
# Or install all requirements
pip install -r requirements.txt
```

**Error:** `python-arango not installed`

**Solution:**
```bash
pip install python-arango
# Or install all requirements
pip install -r requirements.txt
```

### Connection Errors

**Error:** Cannot connect to ArangoDB

**Checklist:**
1. Verify `.env` file exists and contains correct credentials
2. Check `MODE` is set correctly (`LOCAL` or `REMOTE`)
3. For LOCAL: Ensure ArangoDB is running (`docker-compose up` or local instance)
4. For REMOTE: Verify network connectivity and URL is correct
5. Test connection manually:
   ```bash
   python scripts/check_remote_connection.py
   ```

**Error:** Authentication failed

**Solution:**
- Verify username and password in `.env`
- Check that credentials match the configured database
- Ensure user has read permissions on required collections

### Empty Results

**Issue:** Tables show no data

**Possible Causes:**
1. Database is empty - Run data ingestion:
   ```bash
   python scripts/ingest.py --mode REMOTE
   ```

2. Risk scores not computed - Run Phase 3 risk scoring:
   ```bash
   python scripts/phase3_risk.py --mode REMOTE
   ```

3. Collections missing - Verify collections exist:
   ```bash
   python -c "from scripts.common import *; from arango import ArangoClient; import os; load_dotenv(); cfg = get_arango_config(); db = ArangoClient(hosts=cfg.url).db(cfg.database, username=cfg.username, password=cfg.password); print(list(db.collections()))"
   ```

**Issue:** Search returns no results

**Solution:**
- Search uses prefix matching - try shorter search terms
- Check that entity type matches the data (e.g., Person vs GoldenRecord)
- Verify entities exist in the selected collection

### Performance Issues

**Issue:** App is slow to load

**Possible Causes:**
1. Large result sets - Queries are limited to 50 results, but initial load may be slow
2. Network latency - REMOTE mode depends on network speed
3. Database performance - Check ArangoDB query performance

**Solutions:**
- Use more specific search terms to reduce result sets
- Consider running against LOCAL database for faster response
- Check database indexes are created for frequently queried fields

**Issue:** Queries timeout

**Solution:**
- Verify database indexes exist on:
  - `Person.name`, `Person._key`
  - `GoldenRecord._key`, `GoldenRecord.name`
  - `BankAccount.accountNumber`, `BankAccount._key`
  - `transferredTo.scenario`
- Check database performance metrics
- Consider reducing query limits if data volume is very large

### Display Issues

**Issue:** Tables not displaying correctly

**Solution:**
- Ensure Streamlit version is up to date: `pip install --upgrade streamlit`
- Try clearing browser cache
- Check browser console for JavaScript errors

**Issue:** Risk scores showing as null or 0

**Solution:**
- Run risk scoring script:
  ```bash
  python scripts/phase3_risk.py --mode REMOTE
  ```
- Verify risk scoring completed successfully
- Check that `riskScore` field exists in documents

### Mode Configuration Issues

**Issue:** App connects to wrong database

**Solution:**
- Check `MODE` environment variable matches intended target
- Verify LOCAL vs REMOTE environment variable prefixes are correct
- Override mode at runtime: `MODE=REMOTE streamlit run apps/phase3_demo_app.py`

**Issue:** URL shows credentials in browser

**Note:** The app sanitizes URLs before display. If you see credentials:
- This is a bug - report it immediately
- Do not share screenshots containing credentials
- Check that `sanitize_url()` function in `scripts/common.py` is working

## Best Practices

1. **Before Demo:**
   - Run full Phase 3 validation: `python scripts/test_phase3.py --remote-only`
   - Verify data is loaded and risk scores computed
   - Test all three tabs with sample searches
   - Have Visualizer ready for deep-dive exploration

2. **During Demo:**
   - Start with Executive tab for high-level overview
   - Move to Analyst tab to show pattern detection
   - Use Investigator tab for specific entity investigation
   - Copy `_id` values to Visualizer for graph exploration

3. **Security:**
   - Never share `.env` file contents
   - App sanitizes URLs automatically
   - Credentials are never printed or logged
   - Use read-only database user if possible

4. **Performance:**
   - Use specific search terms to reduce query time
   - Consider LOCAL mode for faster response during development
   - Monitor database query performance

## Related Documentation

- `docs/phase3-runbook.md` - Phase 3 analytics and risk scoring
- `docs/visualization_runbook.md` - ArangoDB Visualizer usage
- `README.md` - Project overview and setup
- `QUICK_START.md` - Quick start guide

## Support

For issues not covered in this runbook:
1. Check application logs in terminal output
2. Verify database connectivity independently
3. Review Phase 3 validation reports
4. Consult main project documentation
