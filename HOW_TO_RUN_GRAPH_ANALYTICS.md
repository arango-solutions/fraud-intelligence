# How to Run Graph Analytics - Fraud Intelligence

**CRITICAL: There is NO UI for running graph analytics. You run Python scripts locally on your machine.**

---

## The Setup

You have TWO repositories working together:

1. **`~/code/agentic-graph-analytics`** - The analytics engine (library/package)
2. **`~/code/fraud-intelligence`** - Your fraud detection project (uses the engine)

The fraud-intelligence project runs **Python scripts** that call the agentic-graph-analytics library.

---

## How It Works

```
┌─────────────────────────────────────┐
│  fraud-intelligence repo            │
│                                     │
│  1. You write a Python script      │
│  2. You run: python script.py      │
│  3. Script imports the platform    │
│  4. Script connects to ArangoDB    │
│  5. Platform runs analysis         │
│  6. Reports saved to disk          │
└─────────────────────────────────────┘
```

**No browser. No UI. No "Retry" button. Just: `python your_script.py`**

---

## Step-by-Step: Run Graph Analytics RIGHT NOW

### 1. Open Terminal

```bash
cd ~/code/fraud-intelligence
```

### 2. Verify Platform is Installed

```bash
pip list | grep graph-analytics-ai
```

**If you don't see it:**

```bash
pip install -e ~/code/agentic-graph-analytics
```

### 3. Verify Your .env File Exists

```bash
ls -la .env
```

**If it doesn't exist, create it:**

```bash
cp .env.example .env
# Then edit .env with your real credentials
```

Your `.env` should have (examples only; **do not paste real values into docs**):

```env
ARANGO_URL=https://your-cluster:8529         # or ARANGO_ENDPOINT=...
ARANGO_DATABASE=fraud-intelligence
ARANGO_USERNAME=root                         # or ARANGO_USER=...
ARANGO_PASSWORD=your_actual_password

# Graph API (if using GAE)
ARANGO_GRAPH_API_KEY_ID=your_key_id
ARANGO_GRAPH_API_KEY_SECRET=your_key_secret

# LLM Provider
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_key

# Or if using OpenAI directly
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_openai_key
```

### 4. Test Database Connection

```bash
python -c "from graph_analytics_ai import db_connection; print('✓ Connection OK' if db_connection.test_connection() else '✗ Connection Failed')"
```

**If this fails, your credentials are wrong or your cluster is down.**

### 5. Create the Analysis Script

Create a file called `run_fraud_analysis.py`:

```python
#!/usr/bin/env python3
"""
Fraud Intelligence Graph Analysis
Run with: python run_fraud_analysis.py
"""
import asyncio
from pathlib import Path
from graph_analytics_ai.ai.agents import AgenticWorkflowRunner
from graph_analytics_ai.ai.reporting import ReportFormat
from graph_analytics_ai.ai.reporting.formatter import format_report

async def main():
    print("=" * 60)
    print("FRAUD INTELLIGENCE GRAPH ANALYSIS")
    print("=" * 60)
    
    # Output directory
    output_dir = Path("fraud_analysis_output")
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Output directory: {output_dir.absolute()}")
    
    # Initialize the runner with FRAUD INTELLIGENCE industry
    print("\n[1/4] Initializing workflow runner...")
        runner = AgenticWorkflowRunner(
            graph_name="KnowledgeGraph",  # This repo's demo graph (see scripts/define_graphs.py)
        industry="fraud_intelligence",          # KEY: Fraud-specific prompts & patterns
        enable_tracing=True
    )
    print("✓ Runner initialized with fraud_intelligence industry")
    
    # Input files (optional but recommended)
    input_files = []
    if Path("docs/business_requirements.md").exists():
        input_files.append("docs/business_requirements.md")
    if Path("docs/domain_description.md").exists():
        input_files.append("docs/domain_description.md")
    if Path("PRD/Fraud Use Cases PRD.md").exists():
        input_files.append("PRD/Fraud Use Cases PRD.md")
    
    if input_files:
        print(f"✓ Using {len(input_files)} input files for context")
    
    # Run the analysis
    print("\n[2/4] Running agentic workflow...")
    print("  - Analyzing schema")
    print("  - Generating fraud detection queries")
    print("  - Executing graph algorithms")
    print("  - Detecting fraud patterns")
    print("  - Generating intelligence reports")
    print("\nThis will take 1-3 minutes...\n")
    
    state = await runner.run_async(
        enable_parallelism=True,  # Speed up with parallel execution
        input_files=input_files if input_files else None
    )
    
    print("✓ Workflow completed")
    
    # Check results
    print("\n[3/4] Processing results...")
    if not state.reports:
        print("✗ No reports generated. Check workflow state for errors.")
        return
    
    print(f"✓ Generated {len(state.reports)} intelligence reports")
    
    # Save reports
    print("\n[4/4] Saving reports...")
    for i, report in enumerate(state.reports, 1):
        # Markdown
        md_path = output_dir / f"fraud_report_{i}.md"
        md_content = format_report(report, ReportFormat.MARKDOWN)
        md_path.write_text(md_content)
        print(f"  ✓ {md_path.name}")
        
        # HTML (if charts available)
        try:
            from graph_analytics_ai.ai.reporting import HTMLReportFormatter
            html_formatter = HTMLReportFormatter()
            charts = report.metadata.get('charts', {})
            html_content = html_formatter.format_report(report, charts=charts)
            html_path = output_dir / f"fraud_report_{i}.html"
            html_path.write_text(html_content)
            print(f"  ✓ {html_path.name}")
        except Exception as e:
            print(f"  ⚠ HTML report skipped: {e}")
        
        # Preview insights
        print(f"\n  Report: {report.title}")
        for insight in report.insights[:3]:  # Show first 3
            risk = insight.metadata.get('risk_level', 'N/A')
            conf = insight.metadata.get('confidence', 0)
            print(f"    [{risk}] {insight.title} (confidence: {conf:.2f})")
        if len(report.insights) > 3:
            print(f"    ... and {len(report.insights) - 3} more insights")
    
    print("\n" + "=" * 60)
    print("✓ ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nReports saved to: {output_dir.absolute()}")
    print("\nNext steps:")
    print("  1. Open the HTML reports in your browser")
    print("  2. Review fraud patterns and risk classifications")
    print("  3. Identify accounts requiring STR filing")
    print("  4. Share reports with compliance team")

if __name__ == "__main__":
    asyncio.run(main())
```

### 6. Run It

```bash
python run_fraud_analysis.py
```

**That's it. No UI. No retry button. Just run the script.**

---

## What Happens When You Run It

```
FRAUD INTELLIGENCE GRAPH ANALYSIS
============================================================
✓ Output directory: /Users/you/code/fraud-intelligence/fraud_analysis_output

[1/4] Initializing workflow runner...
✓ Runner initialized with fraud_intelligence industry
✓ Using 3 input files for context

[2/4] Running agentic workflow...
  - Analyzing schema
  - Generating fraud detection queries
  - Executing graph algorithms
  - Detecting fraud patterns
  - Generating intelligence reports

This will take 1-3 minutes...

✓ Workflow completed

[3/4] Processing results...
✓ Generated 4 intelligence reports

[4/4] Saving reports...
  ✓ fraud_report_1.md
  ✓ fraud_report_1.html
  
  Report: Circular Trading Detection - Weakly Connected Components
    [CRITICAL] Money Mule Hub: 47 Accounts Channel ₹8.2 Cr in 48 Hours (confidence: 0.92)
    [HIGH] Benami Identity Clusters: 15 Proxy Networks Detected (confidence: 0.78)
    ... and 3 more insights

  ✓ fraud_report_2.md
  ✓ fraud_report_2.html
  
  Report: Transaction Hub Analysis - PageRank
    [CRITICAL] Transaction Hub Detected: Account BA-456 - PageRank 0.0847 (confidence: 0.88)
    ... and 5 more insights

============================================================
✓ ANALYSIS COMPLETE
============================================================

Reports saved to: /Users/you/code/fraud-intelligence/fraud_analysis_output

Next steps:
  1. Open the HTML reports in your browser
  2. Review fraud patterns and risk classifications
  3. Identify accounts requiring STR filing
  4. Share reports with compliance team
```

---

## Understanding the .env File

The `.env` file contains **your credentials** so the Python script can:

1. **Connect to ArangoDB** - Read your fraud intelligence graph
2. **Execute graph algorithms** - Run WCC, PageRank, cycle detection
3. **Call the LLM** - Generate natural language fraud insights

**The script reads .env automatically. You don't pass credentials as arguments.**

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'graph_analytics_ai'"

**Fix:**

```bash
pip install -e ~/code/agentic-graph-analytics
```

### Error: "Connection to ArangoDB failed"

**Fix:**

1. Check your cluster is running (login to ArangoDB Cloud UI)
2. Verify credentials in `.env` are correct
3. Test: `python -m graph_analytics_ai.cli.test_connection`

### Error: "Graph '...' not found"

**Fix:**

Change `graph_name` in the script to match your actual graph name. In this repo, the demo graphs are:

- `KnowledgeGraph` (recommended for investigations)
- `DataGraph`
- `OntologyGraph`

```python
runner = AgenticWorkflowRunner(
    graph_name="KnowledgeGraph",  # or DataGraph / OntologyGraph if needed
    industry="fraud_intelligence",
    enable_tracing=True
)

---

## Note on GAE (Graph Analytics Engine) on devops-managed clusters

On some devops-managed clusters, the GRAL/GAE engine pod may be **unscheduled** (no Kubernetes endpoints),
which results in engine API calls returning **503**. In that case:

- The **Phase 1–3 AQL-native demo still works** (this repo’s `scripts/test_phase{1,2,3}.py`).
- Algorithm-backed runs that require the engine data-plane will not work until the GRAL pod is scheduled and healthy.
```

### Script runs but no reports generated

**Check:**

1. Does your graph have data? (Check in ArangoDB UI)
2. Are collection names correct? (Person, BankAccount, Organization, etc.)
3. Check workflow logs in terminal output

### "Resource exhausted" or "Out of memory" errors

**Fix:**

1. Reduce parallelism:
   ```python
   state = await runner.run_async(enable_parallelism=False)
   ```

2. Limit collection scope in business requirements doc

3. Use GAE (Graph Analytics Engine) instead of local queries:
   ```env
   # In .env
   USE_GAE=true
   ARANGO_GRAPH_API_KEY_ID=your_gae_key
   ARANGO_GRAPH_API_KEY_SECRET=your_gae_secret
   ```

---

## Where Are the Reports?

After running, reports are in:

```
fraud-intelligence/
  fraud_analysis_output/
    fraud_report_1.md       ← Read in any text editor
    fraud_report_1.html     ← Open in browser (Chrome, Safari, etc.)
    fraud_report_2.md
    fraud_report_2.html
    ...
```

**Open the HTML files in your browser to see:**
- Fraud patterns with risk classifications
- ₹ Crore/Lakh amounts
- PMLA/FEMA regulatory references
- STR filing recommendations
- Account freeze instructions
- Interactive charts (if enabled)

---

## Key Points (READ THIS)

### ✅ YES - This is how you run analysis:

- Write a Python script (like `run_fraud_analysis.py`)
- Run: `python run_fraud_analysis.py`
- Script uses credentials from `.env`
- Reports saved to `fraud_analysis_output/`

### ❌ NO - These are NOT how you run analysis:

- ❌ There is no web UI to click "Run Analysis"
- ❌ There is no "Retry" button anywhere
- ❌ You don't run it from ArangoGraph Platform UI
- ❌ You don't paste credentials into chat with an AI
- ❌ The agentic-graph-analytics is not a web app you login to

---

## Quick Reference

### To run fraud analysis RIGHT NOW:

```bash
cd ~/code/fraud-intelligence
python run_fraud_analysis.py
```

### To modify what gets analyzed:

Edit `docs/business_requirements.md` to change objectives, then re-run the script.

### To change reporting style:

Edit `graph_name` or `industry` parameter in your script.

### To run again with new data:

Just run the script again: `python run_fraud_analysis.py`

---

## Summary

**There is no UI. You run Python scripts locally.**

1. Write script (or use the one above)
2. Run: `python run_fraud_analysis.py`
3. Wait 1-3 minutes
4. Open reports in `fraud_analysis_output/`

That's the entire process.

---

## Need Help?

Check these docs in this repo:

- `QUICK_START.md` - Overview and tips
- `GRAPH_ANALYTICS_SETUP_GUIDE.md` - Detailed setup instructions
- `docs/business_requirements.md` - What analysis objectives you want
- `docs/domain_description.md` - Indian banking fraud context

Or check the platform repo:

- `~/code/agentic-graph-analytics/README.md`
- `~/code/agentic-graph-analytics/examples/` - More example scripts
