# Running Graph Analytics - For AI Agents

**If you are an AI agent helping with this project, read this first.**

---

## Key Facts

1. **There is NO web UI for graph analytics**
   - No ArangoGraph Platform UI for running analysis
   - No "Retry Graph Analysis" button
   - No web interface to trigger workflows

2. **How it actually works:**
   - You run Python scripts locally on the user's machine
   - Scripts import `graph-analytics-ai-platform` (a Python library)
   - Scripts connect to ArangoDB using credentials from `.env`
   - Scripts generate reports and save them to disk

3. **The setup:**
   - `~/code/graph-analytics-ai-platform` = The analytics engine (library)
   - `~/code/fraud-intelligence` = This project (uses the engine)

---

## How to Run Analysis

### Quick Answer

```bash
cd ~/code/fraud-intelligence
python run_fraud_analysis.py
```

That's it. The script is already created and ready to run.

---

## What the Script Does

The `run_fraud_analysis.py` script:

1. Imports the `graph-analytics-ai-platform` library
2. Reads credentials from `.env` file (automatically)
3. Connects to ArangoDB
4. Initializes `AgenticWorkflowRunner` with `industry="fraud_intelligence"`
5. Runs the agentic workflow (1-3 minutes)
6. Saves reports to `fraud_analysis_output/`

**The user does NOT need to:**
- Login to any UI
- Click any buttons
- Manually pass credentials
- Do anything except run the script

---

## The .env File

Location: `~/code/fraud-intelligence/.env`

**Purpose:** Contains credentials for:
- ArangoDB connection (database access)
- LLM API keys (for generating insights)
- Graph API keys (if using GAE)

**The script reads .env automatically.** The user doesn't pass credentials as arguments.

**Common mistake:** Thinking the user needs to paste credentials into chat or a UI. They don't. Credentials live in `.env` and the script reads them.

---

## Pre-Flight Checks

Before telling the user to run the script, verify:

1. **Platform installed:**
   ```bash
   pip list | grep graph-analytics-ai
   ```

2. **`.env` file exists:**
   ```bash
   ls -la ~/code/fraud-intelligence/.env
   ```

3. **Database connection works:**
   ```bash
   python -c "from graph_analytics_ai import db_connection; db_connection.test_connection()"
   ```

If any of these fail, guide the user through `PRE_FLIGHT_CHECKLIST.md`.

---

## Common Misconceptions to Correct

### ❌ "Run Graph Analysis in the ArangoGraph Platform UI"
**✅ Correction:** There is no UI. Run `python run_fraud_analysis.py`

### ❌ "Click the Retry button"
**✅ Correction:** There is no button. Run the Python script.

### ❌ "The graph-analysis-ai-platform is a web app you login to"
**✅ Correction:** It's a Python library. Scripts import it.

### ❌ "Pass credentials to the script"
**✅ Correction:** Credentials are in `.env`. Script reads them automatically.

### ❌ "I need to access your cluster to run this"
**✅ Correction:** The user runs the script on their machine. It connects to their cluster.

---

## Fraud Intelligence Configuration

The `run_fraud_analysis.py` script is pre-configured for Indian banking fraud:

```python
runner = AgenticWorkflowRunner(
    graph_name="KnowledgeGraph",
    industry="fraud_intelligence",  # ← KEY: Enables fraud-specific prompts
    enable_tracing=True
)
```

**What `industry="fraud_intelligence"` does:**
- Uses specialized LLM prompts for Indian banking fraud
- References PMLA, FEMA, Benami Act, FIU-IND
- Formats amounts as ₹ Crores/Lakhs
- Detects fraud patterns (circular trading, mule networks, etc.)
- Generates STR-ready recommendations

**This configuration was set up a few days ago and is already in the code.**

---

## If the User Says "It's Not Working"

### Checklist:

1. **What error did they get?** (Ask for the actual error message)

2. **Did they run the script?**
   ```bash
   cd ~/code/fraud-intelligence
   python run_fraud_analysis.py
   ```

3. **Common errors:**
   - "ModuleNotFoundError" → Run `pip install -e ~/code/graph-analytics-ai-platform`
   - "Connection failed" → Check `.env` credentials and cluster status
   - "Graph not found" → Verify graph name in script matches ArangoDB
   - "No reports generated" → Check if graph has data

4. **Guide them through:** `PRE_FLIGHT_CHECKLIST.md`

---

## Resource Issues (Memory/Performance)

If the user says "resource problems" or "out of memory":

### Quick Fix:

Edit `run_fraud_analysis.py` line ~165:

```python
# Change this:
state = await runner.run_async(enable_parallelism=True, ...)

# To this:
state = await runner.run_async(enable_parallelism=False, ...)
```

### Better Fix (if they have GAE):

Add to `.env`:
```env
USE_GAE=true
ARANGO_GRAPH_API_KEY_ID=their_gae_key
ARANGO_GRAPH_API_KEY_SECRET=their_gae_secret
```

---

## Documentation Hierarchy

**If the user asks "how do I run this?":**

1. **Start here:** `HOW_TO_RUN_GRAPH_ANALYTICS.md` (most explicit, clearest)
2. **Quick reference:** `QUICK_START.md` (overview and examples)
3. **Before running:** `PRE_FLIGHT_CHECKLIST.md` (verify setup)
4. **Detailed setup:** `GRAPH_ANALYTICS_SETUP_GUIDE.md` (if starting from scratch)

**If the user asks "what does this analyze?":**

1. `docs/business_requirements.md` - What fraud patterns to detect
2. `docs/domain_description.md` - Indian banking fraud context
3. `PRD/Fraud Use Cases PRD.md` - Detailed fraud scenarios

---

## What You Should Do

### When the user says "run graph analytics":

```
cd ~/code/fraud-intelligence
python run_fraud_analysis.py
```

### When the user says "it forgot how to run":

Point them to: `HOW_TO_RUN_GRAPH_ANALYTICS.md`

### When the user says "resource problems":

1. Did they fix the resource issue? (storage, memory, API limits)
2. If yes: Just run `python run_fraud_analysis.py` again
3. If no: Help them fix the resource issue first

### When the user says "there's a UI":

**Correct this misconception firmly:**
"There is NO UI. You run Python scripts locally. See HOW_TO_RUN_GRAPH_ANALYTICS.md"

---

## Quick Verification

To verify everything is set up:

```bash
cd ~/code/fraud-intelligence

# Check script exists
ls -l run_fraud_analysis.py

# Check docs exist
ls -l HOW_TO_RUN_GRAPH_ANALYTICS.md
ls -l QUICK_START.md
ls -l PRE_FLIGHT_CHECKLIST.md

# Check platform installed
pip list | grep graph-analytics-ai

# Run the script
python run_fraud_analysis.py
```

---

## Summary for AI Agents

- **NO UI** - It's all Python scripts
- **Script is ready** - `run_fraud_analysis.py` exists and is configured
- **Just run it** - `python run_fraud_analysis.py`
- **Credentials in .env** - Script reads them automatically
- **Reports to disk** - Saved in `fraud_analysis_output/`
- **Already configured for fraud** - `industry="fraud_intelligence"` is set

**The user's original setup from a few days ago is complete. They just need to run the script.**
