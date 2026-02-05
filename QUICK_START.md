# Quick Start - Fraud Intelligence Demo

Ready to run AI-powered fraud detection on your Indian banking graph!

> **Note (template / forward-looking):** This quick start is for an *optional future integration* with an external
> “graph-analytics-ai” platform. The current repo already demonstrates Phase 1–3 using ArangoDB + AQL + Visualizer.
> Any dataset sizes and credentials shown below are **illustrative**.

---

## ✅ What's Been Set Up for You

The **graph-analytics-ai-platform** now has specialized fraud intelligence capabilities:

### 1. Industry Switch: `fraud_intelligence`

```python
# In your fraud-intelligence project, use:
runner = AgenticWorkflowRunner(
    graph_name="fraud_intelligence_graph",
    industry="fraud_intelligence"  # ← Activates Indian banking fraud detection
)
```

### 2. Specialized Fraud Prompts

The platform will now:
- Use ₹ Crores and Lakhs for all amounts
- Reference Indian regulations (PMLA, FEMA, Benami Act, FIU-IND)
- Detect circular trading, money mule networks, circle rate evasion
- Generate STR-ready recommendations
- Provide immediate action items (freeze accounts, file STR)

### 3. Fraud Pattern Detectors

**WCC Analysis detects:**
- Money mule networks (20+ connected accounts)
- Benami identity clusters (3-8 proxy identities per owner)
- Isolated high-risk actors

**PageRank Analysis detects:**
- Transaction hub accounts (aggregators)
- Concentration risk (top 5 control %)
- Normal vs suspicious distributions

---

## 📂 Documentation Created

Three key documents in your `fraud-intelligence` project:

1. **`GRAPH_ANALYTICS_SETUP_GUIDE.md`**
   - Complete setup instructions
   - How to install and configure the platform
   - Example code for running fraud detection
   - Troubleshooting guide

2. **`docs/domain_description.md`**
   - Indian banking context and terminology
   - Graph structure explanation
   - Fraud patterns to detect
   - Regulatory requirements
   - Data characteristics

3. **`docs/business_requirements.md`**
   - 5 specific business objectives
   - Technical requirements for each
   - Success metrics
   - Demo scenario
   - Deliverables expected

---

## 🚀 How to Run

### Step 1: Install the Platform

```bash
cd ~/code/fraud-intelligence
pip install -e ~/code/graph-analytics-ai-platform
```

### Step 2: Configure Environment

Copy `.env.example` to `.env` and add your credentials:

```env
MODE=REMOTE
ARANGO_URL=https://your-cluster.arangodb.cloud:8529
ARANGO_DATABASE=fraud-intelligence
ARANGO_USERNAME=root
ARANGO_PASSWORD=your_password
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key
```

### Step 3: Create Your Fraud Detection Script

```python
# run_fraud_detection.py
import asyncio
from graph_analytics_ai.ai.agents import AgenticWorkflowRunner

async def main():
    runner = AgenticWorkflowRunner(
        graph_name="fraud_intelligence_graph",
        industry="fraud_intelligence",  # KEY LINE
        enable_tracing=True
    )
    
    state = await runner.run_async(
        enable_parallelism=True,
        input_files=["docs/business_requirements.md"]
    )
    
    # Reports will include fraud-specific insights
    for report in state.reports:
        print(f"\n{report.title}")
        for insight in report.insights:
            risk = insight.metadata.get('risk_level', 'N/A')
            print(f"  [{risk}] {insight.title}")

asyncio.run(main())
```

### Step 4: Run It

```bash
python run_fraud_detection.py
```

---

## ✨ What You'll Get

### Fraud Intelligence Reports with:

**Circular Trading Detection:**
- "Circular Trading Ring Detected: ₹2.4 Cr Laundering Cycle"
- Specific account IDs in the ring
- Total amount cycled
- IMMEDIATE: File STR with FIU-IND recommendation

**Money Mule Networks:**
- "Money Mule Hub: 47 Accounts Channel ₹8.2 Cr in 48 Hours"
- Hub account identification
- Mule account list
- Shared IP/device evidence
- CTR evasion indicators

**Circle Rate Fraud:**
- "Circle Rate Evasion: 12 Properties at/below Government Minimum"
- Total declared vs circle rate vs market value
- Estimated tax evasion: ₹4.8 Cr
- Income Tax Department referral recommendation

**Benami Identity Resolution:**
- "Benami Identity Resolution: 4 Proxy Identities → 1 Beneficial Owner"
- Hidden account control revealed
- Combined holdings: ₹12 Cr assets
- Benami Act compliance requirements

### Regulatory Context:
- PMLA, FEMA, Benami Act references
- FIU-IND reporting requirements
- Risk classifications (CRITICAL/HIGH/MEDIUM/LOW)
- Immediate action items

---

## 🎯 Key Differences from Generic Analytics

| Feature | Generic | Fraud Intelligence |
|---------|---------|-------------------|
| Currency | Generic/USD | ₹ Crores/Lakhs |
| Regulations | None | PMLA, FEMA, Benami Act |
| Patterns | Generic | Circular trading, mule networks, circle rate fraud |
| Actions | General recommendations | File STR, freeze accounts, investigate |
| Risk Levels | None | CRITICAL/HIGH/MEDIUM/LOW |
| Confidence | Generic | ≥70% for regulatory actions |

---

## 📋 Checklist

Before your demo:

- [ ] Platform installed: `pip list | grep graph-analytics-ai`
- [ ] Database credentials in `.env`
- [ ] Test connection: `python -m graph_analytics_ai.cli.test_connection`
- [ ] Domain description reviewed
- [ ] Business requirements reviewed
- [ ] Test run with `industry="fraud_intelligence"`
- [ ] Verify reports show ₹ Cr/Lakhs amounts
- [ ] Verify reports reference PMLA/FIU-IND
- [ ] Reports show risk classifications
- [ ] STR recommendations present

---

## 💡 Pro Tips

### 1. Always Specify Industry

```python
# ✅ CORRECT
runner = AgenticWorkflowRunner(
    graph_name="fraud_intelligence_graph",
    industry="fraud_intelligence"
)

# ❌ WRONG (will generate generic insights)
runner = AgenticWorkflowRunner(
    graph_name="fraud_intelligence_graph"
    # Missing industry parameter!
)
```

### 2. Use Your PRD Documents

```python
# Provide your business requirements for tailored analysis
state = await runner.run_async(
    input_files=[
        "docs/business_requirements.md",
        "PRD/Fraud Use Cases PRD.md"
    ]
)
```

### 3. Enable Parallelism for Speed

```python
# Demo requirement: <2 minutes
state = await runner.run_async(enable_parallelism=True)
```

### 4. Export Reports

```python
from pathlib import Path
from graph_analytics_ai.ai.reporting import ReportFormat
from graph_analytics_ai.ai.reporting.formatter import format_report

output_dir = Path("fraud_analysis_output")
output_dir.mkdir(exist_ok=True)

for i, report in enumerate(state.reports):
    # Markdown
    md = format_report(report, ReportFormat.MARKDOWN)
    (output_dir / f"report_{i+1}.md").write_text(md)
    
    # HTML with charts
    from graph_analytics_ai.ai.reporting import HTMLReportFormatter
    html_formatter = HTMLReportFormatter()
    charts = report.metadata.get('charts', {})
    html = html_formatter.format_report(report, charts=charts)
    (output_dir / f"report_{i+1}.html").write_text(html)
```

---

## 🐛 Troubleshooting

### Issue: Generic insights instead of fraud-specific

**Solution:** Check that `industry="fraud_intelligence"` is passed to the runner

### Issue: No ₹ amounts in reports

**Solution:** Ensure `industry="fraud_intelligence"` is set (not "banking" or "fintech")

### Issue: No circle rate insights

**Solution:** Verify RealProperty nodes have `circleRateValue` and `marketValue` fields

### Issue: No Benami detection

**Solution:** Ensure GoldenRecord collection and resolvedTo edges exist

---

## 📚 Additional Resources

- **Setup Guide**: `GRAPH_ANALYTICS_SETUP_GUIDE.md` (detailed instructions)
- **Domain Description**: `docs/domain_description.md` (Indian banking context)
- **Business Requirements**: `docs/business_requirements.md` (objectives and success criteria)
- **Platform README**: `~/code/graph-analytics-ai-platform/README.md`
- **Industry Prompts**: `graph_analytics_ai/ai/reporting/prompts.py` (see FRAUD_INTELLIGENCE_PROMPT)
- **Pattern Detection**: `graph_analytics_ai/ai/reporting/algorithm_insights.py` (fraud patterns)

---

## 🎬 Demo Flow

1. **Setup** (5 min)
   - Show fraud intelligence graph (40K nodes)
   - Explain Indian banking fraud context

2. **Run Analysis** (2 min)
   - Execute: `python run_fraud_detection.py`
   - Show autonomous workflow in action

3. **Results** (10 min)
   - Circular trading rings: ₹12+ Cr detected
   - Money mule networks: 47 mules, ₹45 Cr
   - Circle rate violations: 127 properties, ₹85 Cr tax evasion
   - Benami clusters: 150+ identity groups

4. **Impact** (3 min)
   - 70% reduction in investigation time
   - 60% fewer false positives
   - ₹50+ Cr annual fraud prevention

---

## ✅ Ready to Go!

You now have:
- ✅ Specialized fraud intelligence industry switch
- ✅ Indian banking context and prompts
- ✅ Fraud pattern detectors (WCC, PageRank, cycles)
- ✅ Domain description and business requirements
- ✅ Setup guide and quick start documentation

**Next Step:** Run your first fraud detection workflow!

```bash
cd ~/code/fraud-intelligence
python run_fraud_detection.py
```

---

**Questions?** Check `GRAPH_ANALYTICS_SETUP_GUIDE.md` for detailed troubleshooting.

**Need to customize?** See industry prompts in `graph_analytics_ai/ai/reporting/prompts.py`
