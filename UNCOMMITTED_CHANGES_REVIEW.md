# Review of Uncommitted Changes

**Date:** January 27, 2026

## Summary

23 files modified, ~2000 lines changed
1 untracked file: `docs/business_requirements.pdf`

---

## Category 1: Script Improvements (RECOMMEND: COMMIT)

### `run_fraud_analysis.py`
**Changes:**
- Added `AgentDefaults` import
- Added `FRAUD_ANALYSIS_MAX_EXECUTIONS` environment variable support
- Added synchronous workflow option (when parallelism disabled) to avoid overwhelming services
- Better error handling

**Recommendation:** ✅ **COMMIT** - These are legitimate improvements
**Reason:** Functional enhancements, no sensitive data

---

### `scripts/*.py` (4 files)
**Files:**
- `define_graphs.py` (77 lines changed)
- `generate_data.py` (46 lines changed)
- `ingest.py` (12 lines changed)
- `render_interactive_html_reports.py` (38 lines changed)

**Recommendation:** ✅ **COMMIT** - Functional improvements
**Reason:** Script enhancements, no customer data

---

## Category 2: Documentation Updates (RECOMMEND: COMMIT)

### `PRD/Fraud Use Cases PRD.md`
**Changes:**
- Removed `instanceOf` from WITH clauses (6 lines)
- Minor AQL query cleanup

**Recommendation:** ✅ **COMMIT** - Documentation fix
**Reason:** Technical correction, no sensitive data

---

### `docs/demo/demo-investigator-script.md`
**Changes:**
- Added 129 new lines
- Added "Use Case 2: Money mule hub discovery"
- Added "Use Case 3: Circle rate evasion"
- Added demo talk tracks

**Recommendation:** ✅ **COMMIT** - Valuable demo content
**Reason:** Generic demo scenarios, no customer references

---

## Category 3: Sample Data Files (REVIEW CAREFULLY)

### `data/sample/*.csv` (16 files, ~1800 lines changed)

**Files:**
- `person.csv` (800 lines)
- `BankAccount.csv` (900 lines)
- `residesAt.csv` (796 lines)
- Plus 13 other CSV files

**Sample content:**
```csv
person_42_000000,Victor Tella,VVLDA4636Q,XXXX-XXXX-6474,True,0,,,,
person_42_000001,Victor Tella,VVLDA4636Q,XXXX-XXXX-4064,True,0,,,,
person_42_000002,Rajata Bahl,ASVYX0974Y,XXXX-XXXX-3953,False,0,,,,
```

**Changes appear to be:**
- Added `isSyntheticDuplicate` column
- Data regenerated with new random values
- Names look synthetic (Victor Tella, Rajata Bahl, etc.)
- PAN/Aadhaar are masked/random

**Questions to consider:**
1. Are these names real people or synthetic? (Look synthetic/random)
2. Are PAN numbers real? (Look random)
3. Is this demo data or derived from production?

**Recommendation:** ⚠️ **REVIEW FIRST**
**Options:**
- ✅ **COMMIT** if purely synthetic demo data
- 📦 **KEEP LOCAL** if you're unsure
- 🗑️ **DISCARD** if derived from real data

**Action needed:** Verify data is 100% synthetic before committing

---

### `data/sample/metadata.json`
**Changes:**
- Version or timestamp update (2 lines)

**Recommendation:** ✅ **COMMIT** with the data files

---

## Category 4: Configuration Files (RECOMMEND: COMMIT)

### `docs/themes/knowledgegraph_theme.json`
**Changes:**
- Removed 1 line

**Recommendation:** ✅ **COMMIT** - Configuration cleanup
**Reason:** Theme file, no sensitive data

---

## Category 5: Untracked Files (DECIDE)

### `docs/business_requirements.pdf`
**Status:** Untracked (not in Git)

**Recommendation:** ⚠️ **REVIEW FIRST**
**Options:**
- 📦 **ADD TO .gitignore** - Keep local, don't commit PDFs
- ✅ **COMMIT** - If it's generic demo documentation
- 🗑️ **DELETE** - If it contains sensitive info

**Most common practice:** Add `*.pdf` to `.gitignore` for demo repos

---

## Recommendations Summary

### ✅ SAFE TO COMMIT (No Review Needed)

**Scripts:**
- `run_fraud_analysis.py`
- `scripts/define_graphs.py`
- `scripts/generate_data.py`
- `scripts/ingest.py`
- `scripts/render_interactive_html_reports.py`

**Documentation:**
- `PRD/Fraud Use Cases PRD.md`
- `docs/demo/demo-investigator-script.md`
- `docs/themes/knowledgegraph_theme.json`

---

### ⚠️ REQUIRES REVIEW BEFORE COMMITTING

**Data files (16 CSV files + metadata.json):**
- Verify all data is synthetic
- Check for real names, PAN numbers, addresses
- Confirm no production data

**PDF file:**
- `docs/business_requirements.pdf` - Review content or add to .gitignore

---

### 🎯 RECOMMENDED ACTIONS

#### Option A: Conservative Approach (Safest)

```bash
# Commit only scripts and docs
git add run_fraud_analysis.py
git add scripts/*.py
git add "PRD/Fraud Use Cases PRD.md"
git add docs/demo/demo-investigator-script.md
git add docs/themes/knowledgegraph_theme.json
git commit -m "Improve fraud analysis workflow and add demo scenarios"
git push

# Keep data local (don't commit yet)
# Review data carefully before committing
```

#### Option B: Commit Everything (If Data is Verified Synthetic)

```bash
# Add PDF to gitignore first
echo "*.pdf" >> .gitignore
git add .gitignore

# Commit all changes
git add -A
git commit -m "Update fraud detection scripts, demo scenarios, and sample data"
git push
```

#### Option C: Selective Review

```bash
# Commit safe files first
git add run_fraud_analysis.py scripts/*.py "PRD/Fraud Use Cases PRD.md" docs/demo/ docs/themes/
git commit -m "Improve fraud analysis workflow and add demo scenarios"

# Review data files one by one
git diff data/sample/person.csv | less
# If looks safe:
git add data/sample/*.csv data/sample/metadata.json
git commit -m "Update synthetic sample data for fraud detection demos"

git push
```

---

## Quick Decision Matrix

| File Type | Contains Sensitive Data? | Action |
|-----------|-------------------------|---------|
| Scripts (*.py) | No | ✅ Commit |
| PRD/docs (*.md) | No | ✅ Commit |
| Theme (*.json) | No | ✅ Commit |
| Sample data (*.csv) | **VERIFY FIRST** | ⚠️ Review then decide |
| PDF | Unknown | 📦 Add to .gitignore or review |

---

## Commands to Execute

### 1. Review the data first

```bash
# Check if names look real or synthetic
head -20 data/sample/person.csv

# Search for any suspicious patterns
grep -i "real\|actual\|prod" data/sample/*.csv

# Check metadata
cat data/sample/metadata.json
```

### 2. Then choose your path:

**Path A - Safe commits only:**
```bash
git add run_fraud_analysis.py scripts/ PRD/ docs/demo/ docs/themes/
git commit -m "Improve fraud analysis workflow and add demo scenarios

- Add MAX_EXECUTIONS environment variable support
- Add synchronous workflow option for stability
- Improve script error handling
- Add money mule hub discovery demo
- Add circle rate evasion demo
- Clean up AQL queries in PRD"
git push
```

**Path B - After verifying data is synthetic:**
```bash
echo "*.pdf" >> .gitignore
git add .gitignore
git add -A
git commit -m "Update fraud detection demos and regenerate sample data

- Improve fraud analysis workflow with configurable execution limits
- Add synchronous mode to prevent service overload
- Add investigator demo scenarios (money mule, circle rate evasion)
- Regenerate synthetic sample data with duplicate markers
- Clean up AQL queries and theme configuration"
git push
```

---

## ⚠️ CRITICAL: Before Committing Data

Verify these questions:

1. ✅ Are all names synthetic/generated?
2. ✅ Are PAN numbers random (not real)?
3. ✅ Are Aadhaar numbers masked?
4. ✅ Are addresses generic/synthetic?
5. ✅ Is there NO production data mixed in?
6. ✅ Is there NO customer-specific information?

**If you answer "NO" or "UNSURE" to any question, DO NOT commit the data files.**

---

## Need Help Deciding?

Run this check:

```bash
# Look for real-looking email domains
grep -i "@.*\.(com|in|org|net)" data/sample/*.csv

# Look for real company names (adjust as needed)
grep -i "tcs\|infosys\|wipro\|hdfc\|icici\|sbi" data/sample/*.csv

# Check for production markers
grep -i "prod\|production\|real\|actual\|live" data/sample/*.csv
```

If any of these return matches that look real, **DO NOT COMMIT** the data.
