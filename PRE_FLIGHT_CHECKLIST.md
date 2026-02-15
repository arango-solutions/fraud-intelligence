# Pre-Flight Checklist - Fraud Intelligence Analysis

Before running `python run_fraud_analysis.py`, verify these items:

## ✅ Checklist

### 1. Platform Installation

```bash
pip list | grep graph-analytics-ai
```

**Expected:** `graph-analytics-ai` appears in the list

**If not:**
```bash
pip install -e ~/code/agentic-graph-analytics
```

---

### 2. Environment File
 
Do **not** print or paste `.env` contents (it contains secrets).
 
```bash
cd ~/code/fraud-intelligence
test -f .env && echo "✓ .env exists" || echo "✗ .env missing"
```
 
**Expected:** `✓ .env exists`

**If "No such file":**
```bash
cd ~/code/fraud-intelligence
cp .env.example .env
# Then edit .env with real credentials
```

**Required variables:**
- ArangoDB connection (this repo supports either naming scheme):
  - `ARANGO_URL` (or `ARANGO_ENDPOINT`)
  - `ARANGO_DATABASE`
  - `ARANGO_USERNAME` (or `ARANGO_USER`)
  - `ARANGO_PASSWORD`
- `OPENROUTER_API_KEY` or `OPENAI_API_KEY` - For LLM
- `LLM_PROVIDER` - Either "openrouter" or "openai"

**Safe key-presence check (prints names only, not values):**

```bash
python - <<'PY'
import os
from pathlib import Path

# minimal .env existence check only (do not print values)
print("envFile:", "present" if Path(".env").exists() else "missing")

keys = [
  "ARANGO_URL","ARANGO_ENDPOINT","ARANGO_DATABASE","ARANGO_USERNAME","ARANGO_USER","ARANGO_PASSWORD",
  "LLM_PROVIDER","OPENROUTER_API_KEY","OPENAI_API_KEY"
]
missing = [k for k in keys if not os.getenv(k)]
print("missingKeys:", missing)
PY
```

---

### 3. Database Connection

```bash
cd ~/code/fraud-intelligence
python -c "from graph_analytics_ai import db_connection; print('✓ Connected' if db_connection.test_connection() else '✗ Failed')"
```

**Expected:** `✓ Connected`

**If failed:**
- Check cluster is running (ArangoDB Cloud UI)
- Verify credentials in `.env`
- Check network/firewall

---

### 4. Graph Exists

Login to ArangoDB Web UI and verify:
- [ ] Database exists (e.g. `fraud-intelligence`)
- [ ] Graph exists (this repo’s demo graphs are: `KnowledgeGraph`, `DataGraph`, `OntologyGraph`)
- [ ] Collections have data (Person, BankAccount, Organization, etc.)

**If graph name is different, edit `run_fraud_analysis.py`:**
```python
GRAPH_NAME = "your_actual_graph_name"  # Line ~60
```

---

### 5. Graph Has Data

```bash
python -c "
from graph_analytics_ai.db_connection import get_db
db = get_db()
counts = {
    'Person': db.collection('Person').count() if db.has_collection('Person') else 0,
    'BankAccount': db.collection('BankAccount').count() if db.has_collection('BankAccount') else 0,
    'transferredTo': db.collection('transferredTo').count() if db.has_collection('transferredTo') else 0,
}
print('Collection counts:', counts)
print('✓ Data exists' if any(counts.values()) else '✗ No data found')
"
```

**Expected:** Non-zero counts

---

### 6. Input Documents Exist

```bash
ls -l ~/code/fraud-intelligence/docs/business_requirements.md
ls -l ~/code/fraud-intelligence/docs/domain_description.md
```

**Expected:** Both files exist

**Note:** These are optional but highly recommended for better results

---

### 7. LLM API Key Valid
Avoid commands that print tokens or place them in shell history. Prefer running the main script and fixing any auth error it reports.

---

## 🚀 Ready to Run

If all checks pass:

```bash
cd ~/code/fraud-intelligence
python run_fraud_analysis.py
```

---

## 🐛 Common Issues

### "ModuleNotFoundError: No module named 'graph_analytics_ai'"

**Fix:**
```bash
pip install -e ~/code/agentic-graph-analytics
```

### "Connection to database failed"

**Check:**
1. Cluster is running (ArangoDB Cloud)
2. `.env` has the required ArangoDB keys (this repo supports `ARANGO_URL` or `ARANGO_ENDPOINT`)
3. Run: `python -m graph_analytics_ai.cli.test_connection`

### "Graph '...' not found"

**Fix:** Edit `run_fraud_analysis.py` line ~60:
```python
GRAPH_NAME = "your_actual_graph_name"
```

In this repo, the demo graphs are: `KnowledgeGraph` (recommended), `DataGraph`, `OntologyGraph`.

### "No reports generated"

**Possible causes:**
1. Graph has no data
2. Collection names don't match schema
3. Queries returned empty results

**Debug:**
- Check collection counts (see checklist #5)
- Run with `enable_tracing=True` (already enabled)
- Check terminal output for error messages

### "Rate limit exceeded" or "API key invalid"

**Fix:**
1. Verify LLM API key in `.env`
2. Check billing/credits on OpenRouter or OpenAI
3. Wait a few minutes if rate limited

### "Out of memory" or "Resource exhausted"

**Fix:** Edit `run_fraud_analysis.py` line ~165:
```python
state = await runner.run_async(
    enable_parallelism=False,  # Change to False
    input_files=input_files if input_files else None
)
```

Or use GAE if available:
```env
# Add to .env
USE_GAE=true
ARANGO_GRAPH_API_KEY_ID=your_gae_key
ARANGO_GRAPH_API_KEY_SECRET=your_gae_secret
```

---

## 📞 Still Stuck?

### Check these docs:
- `HOW_TO_RUN_GRAPH_ANALYTICS.md` - Step-by-step instructions
- `QUICK_START.md` - Overview and examples
- `GRAPH_ANALYTICS_SETUP_GUIDE.md` - Detailed setup

### Verify your setup:
```bash
# Check Python version (3.8+)
python --version

# Check installed packages
pip list | grep -E "(graph-analytics|arango|openai)"

# Do NOT print .env contents (contains secrets). Just verify it exists:
test -f .env && echo "✓ .env exists" || echo "✗ .env missing"

# Check working directory
pwd  # Should be ~/code/fraud-intelligence
```

### Test minimal connection:
```python
# test_minimal.py
from graph_analytics_ai.db_connection import get_db

try:
    db = get_db()
    print(f"✓ Connected to database: {db.name}")
    print(f"✓ Collections: {len(db.collections())}")
except Exception as e:
    print(f"✗ Error: {e}")
```

---

## 💡 Remember

**There is NO web UI. You run Python scripts locally.**

1. Check this list ✅
2. Run: `python run_fraud_analysis.py`
3. Wait 1-3 minutes ⏱
4. Open reports in `fraud_analysis_output/` 📊

That's it!
