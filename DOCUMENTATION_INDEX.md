# 📚 Fraud Intelligence - Documentation Index

**Everything you need to run AI-powered fraud detection on your Indian banking graph.**

---

## 🚀 Quick Start (Start Here)

If you just want to **RUN THE ANALYSIS RIGHT NOW:**

1. Read: **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)** ← **START HERE**
2. Check: **[PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)**
3. Run: `python run_fraud_analysis.py`

**That's it. These 3 steps will get you running.**

---

## 📖 Documentation Guide

### For Humans

| Document | When to Read | What You'll Learn |
|----------|--------------|-------------------|
| **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)** | **First** - Before running anything | Step-by-step instructions, corrects "UI" misconception |
| **[PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)** | Before running the script | Verify setup, troubleshoot common issues |
| **[QUICK_START.md](QUICK_START.md)** | Quick reference | Examples, tips, common patterns |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Want to understand the system | How everything fits together, visual diagrams |
| **[GRAPH_ANALYTICS_SETUP_GUIDE.md](GRAPH_ANALYTICS_SETUP_GUIDE.md)** | Setting up from scratch | Detailed installation and configuration |

### For AI Agents

| Document | Purpose |
|----------|---------|
| **[FOR_AI_AGENTS_README.md](FOR_AI_AGENTS_README.md)** | Key facts, common misconceptions to correct, quick verification |

---

## 🎯 By Use Case

### "I want to run fraud detection now"

1. **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)** - Read this
2. **[PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)** - Verify setup
3. Run: `python run_fraud_analysis.py`

### "Something isn't working"

1. **[PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)** - Troubleshooting guide
2. **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)** - See "Troubleshooting" section
3. **[QUICK_START.md](QUICK_START.md)** - See "🐛 Troubleshooting" section

### "I'm confused about how this works"

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Visual diagrams and explanations
2. **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)** - Clears up UI misconception

### "I'm setting up for the first time"

1. **[GRAPH_ANALYTICS_SETUP_GUIDE.md](GRAPH_ANALYTICS_SETUP_GUIDE.md)** - Complete setup guide
2. **[PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)** - Verify each step
3. **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)** - Run first analysis

### "I want examples and best practices"

1. **[QUICK_START.md](QUICK_START.md)** - Examples, pro tips, demo flow
2. **[docs/business_requirements.md](docs/business_requirements.md)** - What to analyze
3. **[docs/domain_description.md](docs/domain_description.md)** - Domain context

### "I need to explain this to someone else"

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Clear visual explanation
2. **[QUICK_START.md](QUICK_START.md)** - Overview and key differences table
3. **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)** - Step-by-step instructions

---

## 📁 File Structure

```
fraud-intelligence/
│
├── 🚀 EXECUTION
│   └── run_fraud_analysis.py          ← The script you run
│
├── 📚 DOCUMENTATION (How to Run)
│   ├── HOW_TO_RUN_GRAPH_ANALYTICS.md  ← START HERE
│   ├── PRE_FLIGHT_CHECKLIST.md        ← Verify before running
│   ├── QUICK_START.md                 ← Quick reference
│   ├── ARCHITECTURE.md                ← How it works
│   └── GRAPH_ANALYTICS_SETUP_GUIDE.md ← Detailed setup
│
├── 📚 DOCUMENTATION (For AI Agents)
│   ├── FOR_AI_AGENTS_README.md        ← AI agent guide
│   └── DOCUMENTATION_INDEX.md         ← This file
│
├── 📋 REQUIREMENTS (What to Analyze)
│   ├── docs/
│   │   ├── business_requirements.md   ← Business objectives
│   │   └── domain_description.md      ← Indian banking context
│   └── PRD/
│       ├── PRD.md                     ← Product requirements
│       └── Fraud Use Cases PRD.md     ← Detailed fraud scenarios
│
├── ⚙️ CONFIGURATION
│   ├── .env                           ← Your credentials (not in Git)
│   └── .env.example                   ← Template
│
└── 📊 OUTPUT
    └── fraud_analysis_output/         ← Generated reports
        ├── fraud_report_1.md
        ├── fraud_report_1.html
        └── ...
```

---

## 🔑 Key Concepts

### ❌ Common Misconception

**"There's a UI where I click 'Run Graph Analysis'"**

**✅ Reality:**

You run Python scripts locally on your machine:

```bash
cd ~/code/fraud-intelligence
python run_fraud_analysis.py
```

**No browser. No buttons. No web app. Just: `python script.py`**

See **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)** for detailed explanation.

---

### The Two Repositories

1. **`graph-analytics-ai-platform`** (the engine)
   - Python library/package
   - Contains analytics code
   - You `import` it in scripts

2. **`fraud-intelligence`** (your project)
   - Your fraud detection project
   - Contains scripts that USE the platform
   - Where you run commands

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for visual diagrams.

---

### The .env File

**Location:** `~/code/fraud-intelligence/.env`

**Contains:**
- ArangoDB credentials
- LLM API keys
- Configuration

**Used by:** The Python script (reads automatically)

**Security:** Never commit to Git, never paste in chat

---

### The Industry Switch

**In `run_fraud_analysis.py`:**

```python
runner = AgenticWorkflowRunner(
    graph_name="KnowledgeGraph",
    industry="fraud_intelligence",  # ← This is the magic
    enable_tracing=True
)
```

**What it does:**
- Enables Indian banking fraud prompts
- References PMLA, FEMA, Benami Act, FIU-IND
- Formats amounts as ₹ Crores/Lakhs
- Detects fraud patterns (circular trading, mule networks)
- Generates STR-ready recommendations

**This is already configured. You don't need to change anything.**

---

## ⚡ Quick Commands

### Run Analysis

```bash
cd ~/code/fraud-intelligence
python run_fraud_analysis.py
```

### Test Connection

```bash
python -c "from graph_analytics_ai import db_connection; print('✓' if db_connection.test_connection() else '✗')"
```

### Check Installation

```bash
pip list | grep graph-analytics-ai
```

### Install Platform

```bash
pip install -e ~/code/graph-analytics-ai-platform
```

### Open Reports

```bash
open fraud_analysis_output/fraud_report_1.html
```

---

## 🎓 Learning Path

### Level 1: Complete Beginner

1. **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)** - Understand the basics
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - See how it fits together
3. **[PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)** - Verify setup
4. Run: `python run_fraud_analysis.py`
5. **[QUICK_START.md](QUICK_START.md)** - Learn tips and tricks

### Level 2: Regular User

1. **[QUICK_START.md](QUICK_START.md)** - Quick reference
2. Modify `docs/business_requirements.md` for different analysis
3. Run: `python run_fraud_analysis.py`
4. Share reports with team

### Level 3: Advanced User

1. Study `~/code/graph-analytics-ai-platform/graph_analytics_ai/ai/reporting/prompts.py`
2. Customize `FRAUD_INTELLIGENCE_PROMPT` for your needs
3. Study `~/code/graph-analytics-ai-platform/graph_analytics_ai/ai/reporting/algorithm_insights.py`
4. Add custom pattern detectors
5. Modify `run_fraud_analysis.py` for custom workflows

---

## 🆘 Help! Which Doc Do I Read?

### "I just want to run it"
→ **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)**

### "It's not working"
→ **[PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)**

### "I don't understand what's happening"
→ **[ARCHITECTURE.md](ARCHITECTURE.md)**

### "I need quick answers"
→ **[QUICK_START.md](QUICK_START.md)**

### "I'm setting up from scratch"
→ **[GRAPH_ANALYTICS_SETUP_GUIDE.md](GRAPH_ANALYTICS_SETUP_GUIDE.md)**

### "I'm an AI agent helping someone"
→ **[FOR_AI_AGENTS_README.md](FOR_AI_AGENTS_README.md)**

### "I want to understand what patterns to detect"
→ **[docs/business_requirements.md](docs/business_requirements.md)**

### "I want to understand Indian banking fraud context"
→ **[docs/domain_description.md](docs/domain_description.md)**

---

## 📞 Still Need Help?

### Check these in order:

1. **Error message?** → See troubleshooting sections in docs above
2. **Setup issue?** → [PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)
3. **Conceptual confusion?** → [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Forgot commands?** → [QUICK_START.md](QUICK_START.md)

### Verify basics:

```bash
# Check you're in the right directory
pwd  # Should show: .../fraud-intelligence

# Check platform installed
pip list | grep graph-analytics-ai

# Check .env exists
ls -la .env

# Test connection
python -c "from graph_analytics_ai import db_connection; db_connection.test_connection()"
```

---

## 💡 Remember

**The Golden Rules:**

1. ✅ **There is NO web UI** - You run Python scripts
2. ✅ **Just run the script** - `python run_fraud_analysis.py`
3. ✅ **Credentials in .env** - Script reads them automatically
4. ✅ **Reports to disk** - Saved in `fraud_analysis_output/`
5. ✅ **Already configured** - Everything is set up for Indian banking fraud

---

## 🎯 Success Checklist

Before you start your demo:

- [ ] Read **[HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)**
- [ ] Complete **[PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)**
- [ ] Run `python run_fraud_analysis.py` successfully
- [ ] Open HTML reports in browser
- [ ] Verify reports show ₹ Crore/Lakh amounts
- [ ] Verify reports reference PMLA/FIU-IND
- [ ] Verify reports show CRITICAL/HIGH risk classifications
- [ ] Review top fraud patterns
- [ ] Prepare demo talking points from reports

---

**Ready? Start here: [HOW_TO_RUN_GRAPH_ANALYTICS.md](HOW_TO_RUN_GRAPH_ANALYTICS.md)**

Good luck with your fraud detection demo! 🚀
