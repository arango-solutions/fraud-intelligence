# Analytics Catalog - Usage Guide for Fraud Intelligence

The fraud intelligence workflow now includes **Analytics Catalog** support for comprehensive execution tracking, compliance, and historical analysis.

---

## What's New

### Automatic Tracking

When you run `run_fraud_analysis.py`, the workflow now automatically:

1. **Creates Monthly Epochs** - Groups analyses by month (e.g., "fraud-detection-2026-02")
2. **Tracks All Executions** - Every algorithm run (WCC, PageRank, cycles) is recorded
3. **Stores Results** - Result summaries and samples are saved
4. **Records Performance** - Execution times, status, errors
5. **Maintains Lineage** - Links requirements → use cases → templates → executions

### Compliance & Audit Benefits

- **Full Traceability** - Complete audit trail from business requirements to results
- **Historical Analysis** - Compare current fraud patterns with previous months
- **Regulatory Compliance** - Documentation for PMLA, FEMA, FIU-IND reviews
- **Performance Monitoring** - Track execution times and optimization needs

---

## Quick Start

### Enable Catalog (Default)

The catalog is **enabled by default**. Just run your analysis as usual:

```bash
python run_fraud_analysis.py
```

You'll see new output:

```
[1/5] Initializing agentic workflow...
      Graph: KnowledgeGraph
      Industry: fraud_intelligence
✓ Created catalog epoch: fraud-detection-2026-02
  Epoch ID: epoch-20260210-123456
  📊 Catalog tracking ENABLED (for compliance/audit)
```

### Disable Catalog (Optional)

If you want to run without catalog tracking:

```bash
FRAUD_ANALYSIS_ENABLE_CATALOG=false python run_fraud_analysis.py
```

---

## Environment Variables

Add to your `.env` file:

```bash
# Catalog Configuration (optional)
FRAUD_ANALYSIS_ENABLE_CATALOG=true   # Enable/disable catalog (default: true)
```

---

## What Gets Tracked

### 1. Epochs

Logical groupings of analyses (typically monthly):

```
Epoch: fraud-detection-2026-02
├── Description: Monthly fraud detection analysis for Indian banking - February 2026
├── Tags: production, fraud_intelligence, monthly, india, compliance
├── Status: active
└── Executions: [all executions from this period]
```

### 2. Requirements

Extracted business requirements:

```
Requirement: Detect Circular Trading Rings
├── Source: docs/business_requirements.md
├── Objectives: Identify money laundering through circular fund transfers
└── Success Criteria: Detect cycles involving ₹2+ Cr
```

### 3. Use Cases

Generated analysis use cases:

```
Use Case: WCC Analysis for Connected Account Groups
├── Requirement: [linked back]
├── Algorithm: weakly_connected_components
└── Parameters: min_component_size=3
```

### 4. Templates

Generated AQL query templates:

```
Template: WCC_Connected_Accounts
├── Use Case: [linked back]
├── Algorithm: weakly_connected_components
└── AQL Query: [full query]
```

### 5. Executions

Algorithm execution records:

```
Execution: exec-20260210-145623-wcc
├── Template: WCC_Connected_Accounts
├── Algorithm: weakly_connected_components
├── Status: completed
├── Duration: 2,345 ms
├── Timestamp: 2026-02-10T14:56:23Z
├── Results: 127 components detected
└── Risk Findings: 8 CRITICAL, 15 HIGH
```

---

## Querying the Catalog

### View Current Month's Executions

```python
from graph_analytics_ai.catalog import (
    AnalysisCatalog,
    CatalogQueries,
    ExecutionFilter
)
from graph_analytics_ai.catalog.storage import ArangoDBStorage
from graph_analytics_ai.db_connection import get_db_connection

# Initialize
db = get_db_connection()
storage = ArangoDBStorage(db)
queries = CatalogQueries(storage)

# Get this month's executions
executions = queries.query_with_pagination(
    filter=ExecutionFilter(
        epoch_id="epoch-20260210-123456",  # Your epoch ID
        status="completed"
    ),
    page=1,
    page_size=100
)

print(f"Found {executions.total_count} executions:")
for exec in executions.items:
    print(f"  - {exec.algorithm}: {exec.execution_duration_ms}ms")
    print(f"    Results: {exec.result_summary.get('result_count', 0)} records")
```

### Compare This Month vs Last Month

```python
from datetime import datetime, timedelta

# Get executions from this month
this_month_start = datetime(2026, 2, 1)
this_month_end = datetime(2026, 3, 1)

this_month = queries.query_with_pagination(
    filter=ExecutionFilter(
        algorithm="wcc",
        start_date=this_month_start,
        end_date=this_month_end,
        status="completed"
    )
)

# Get executions from last month
last_month_start = datetime(2026, 1, 1)
last_month_end = datetime(2026, 2, 1)

last_month = queries.query_with_pagination(
    filter=ExecutionFilter(
        algorithm="wcc",
        start_date=last_month_start,
        end_date=last_month_end,
        status="completed"
    )
)

print(f"WCC Executions:")
print(f"  This month: {this_month.total_count}")
print(f"  Last month: {last_month.total_count}")

# Compare average performance
this_avg = sum(e.execution_duration_ms for e in this_month.items) / len(this_month.items)
last_avg = sum(e.execution_duration_ms for e in last_month.items) / len(last_month.items)

print(f"\nAverage Duration:")
print(f"  This month: {this_avg:.0f}ms")
print(f"  Last month: {last_avg:.0f}ms")
print(f"  Change: {((this_avg - last_avg) / last_avg * 100):+.1f}%")
```

### Time-Series Analysis

```python
from graph_analytics_ai.catalog import TimeSeriesQuery

# Analyze PageRank results over time
time_series = queries.time_series_analysis(
    TimeSeriesQuery(
        algorithm="pagerank",
        metric="avg_rank",
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 2, 10),
        interval="week"
    )
)

print("PageRank Weekly Trends:")
for point in time_series.data_points:
    print(f"  {point.timestamp}: avg={point.value:.4f}")
```

### Lineage Tracking

```python
from graph_analytics_ai.catalog import LineageTracker

tracker = LineageTracker(storage)

# Get complete lineage for a specific execution
lineage = tracker.get_complete_lineage("exec-20260210-145623-wcc")

print("Execution Lineage:")
print(f"  Requirement: {lineage.requirement.title}")
print(f"  Use Case: {lineage.use_cases[0].title}")
print(f"  Template: {lineage.templates[0].name}")
print(f"  Execution: {lineage.executions[0].execution_id}")
print(f"  Results: {lineage.executions[0].result_summary}")
```

### Impact Analysis

```python
# Analyze impact of a requirement change
impact = tracker.analyze_impact("req-detect-circular-trading", "requirement")

print(f"Requirement Impact Analysis:")
print(f"  Affects {impact.affected_count} downstream items:")
print(f"  - {impact.affected_use_cases} use cases")
print(f"  - {impact.affected_templates} templates")
print(f"  - {impact.affected_executions} executions")
```

### Coverage Report

```python
# Ensure all requirements are addressed
coverage = tracker.generate_coverage_report("epoch-20260210-123456")

print(f"Coverage Report:")
print(f"  Requirements: {coverage.total_requirements}")
print(f"  Use Cases: {coverage.total_use_cases}")
print(f"  Executions: {coverage.total_executions}")
print(f"  Coverage: {coverage.coverage_percentage:.1f}%")

if coverage.uncovered_requirements:
    print(f"\n⚠ Uncovered Requirements:")
    for req_id in coverage.uncovered_requirements:
        print(f"    - {req_id}")
```

---

## Compliance Use Cases

### 1. Monthly Compliance Report

Generate a monthly report for regulatory review:

```python
from graph_analytics_ai.catalog import CatalogManager

manager = CatalogManager(storage)

# Get statistics for the epoch
stats = manager.get_catalog_statistics(
    epoch_id="epoch-20260210-123456"
)

print(f"Monthly Compliance Report - February 2026")
print(f"=" * 70)
print(f"Total Executions: {stats.total_executions}")
print(f"Success Rate: {stats.success_rate:.1%}")
print(f"Avg Duration: {stats.avg_execution_duration_ms:.0f}ms")
print(f"\nBy Algorithm:")
for algo, count in stats.executions_by_algorithm.items():
    print(f"  - {algo}: {count} runs")
print(f"\nCritical Findings: [from execution results]")
print(f"STRs Filed: [manual tracking]")
print(f"Accounts Frozen: [manual tracking]")
```

### 2. Audit Trail for STR Filing

When filing an STR with FIU-IND, provide complete lineage:

```python
# For a specific fraud detection result
execution_id = "exec-20260210-145623-wcc"

lineage = tracker.get_complete_lineage(execution_id)

print("STR Audit Trail")
print("=" * 70)
print(f"Business Requirement:")
print(f"  {lineage.requirement.title}")
print(f"  {lineage.requirement.description}")
print()
print(f"Analysis Method:")
print(f"  Use Case: {lineage.use_cases[0].title}")
print(f"  Algorithm: {lineage.use_cases[0].algorithm}")
print()
print(f"Query Template:")
print(f"  {lineage.templates[0].name}")
print(f"  Generated: {lineage.templates[0].created_at}")
print()
print(f"Execution:")
print(f"  ID: {lineage.executions[0].execution_id}")
print(f"  Timestamp: {lineage.executions[0].execution_timestamp}")
print(f"  Results: {lineage.executions[0].result_summary}")
print()
print("This provides complete traceability for regulatory review.")
```

### 3. Historical Trend Analysis

Compare fraud patterns over multiple months:

```python
# Get all epochs
catalog = AnalysisCatalog(storage)
epochs = catalog.query_epochs(limit=12)  # Last 12 months

print("Historical Fraud Trend Analysis")
print("=" * 70)

for epoch in epochs:
    executions = queries.query_with_pagination(
        filter=ExecutionFilter(
            epoch_id=epoch.epoch_id,
            algorithm="wcc",
            status="completed"
        )
    )
    
    # Calculate average component count
    avg_components = sum(
        e.result_summary.get("component_count", 0)
        for e in executions.items
    ) / len(executions.items) if executions.items else 0
    
    print(f"{epoch.name}: {avg_components:.0f} avg components")

print("\nInsights:")
print("  - Increasing components → more fragmentation")
print("  - Decreasing components → more consolidation")
print("  - Sudden changes → new fraud patterns emerging")
```

---

## Catalog Maintenance

### Archive Old Epochs

Keep recent data, archive old data:

```python
from graph_analytics_ai.catalog import CatalogManager

manager = CatalogManager(storage)

# Archive epochs older than 180 days
archived = manager.archive_old_epochs(older_than_days=180)

print(f"Archived {len(archived)} old epochs")
```

### Validate Catalog Integrity

Ensure catalog data is consistent:

```python
integrity = manager.validate_catalog_integrity()

if integrity.is_valid:
    print("✓ Catalog integrity OK")
else:
    print(f"⚠ Found {len(integrity.issues)} issues:")
    for issue in integrity.issues:
        print(f"  - {issue}")
```

### Cleanup Failed Executions

Remove incomplete or failed runs:

```python
# Get failed executions
failed = queries.query_with_pagination(
    filter=ExecutionFilter(status="failed"),
    page=1,
    page_size=100
)

print(f"Found {failed.total_count} failed executions")

# Review and delete if needed
for exec in failed.items:
    print(f"  {exec.execution_id}: {exec.error_details}")
    # catalog.delete_execution(exec.execution_id)  # Uncomment to delete
```

---

## Storage Requirements

### Collections Created

The catalog creates these collections in your ArangoDB database:

- `analysis_executions` - Execution records
- `analysis_epochs` - Epoch metadata
- `extracted_requirements` - Business requirements
- `generated_use_cases` - Analysis use cases
- `analysis_templates` - Query templates
- `execution_lineage` (edge) - Lineage relationships

### Storage Estimates

**Per month (typical fraud analysis):**
- 10-20 executions: ~1-2 MB
- 1 epoch: ~10 KB
- Requirements, use cases, templates: ~500 KB
- **Total: ~2-3 MB/month**

**Annual retention:**
- 12 months: ~25-35 MB
- Negligible compared to graph data

---

## Best Practices

### 1. Monthly Epochs

Let the workflow auto-create monthly epochs:

```python
# The workflow automatically creates:
# "fraud-detection-2026-01" (January)
# "fraud-detection-2026-02" (February)
# etc.
```

### 2. Tag Critical Analyses

Add custom tags for important analyses:

```python
# Manually create epoch with specific tags
epoch = catalog.create_epoch(
    name="fraud-detection-q1-review",
    description="Quarterly review for board presentation",
    tags=["production", "quarterly", "board_review", "high_priority"]
)
```

### 3. Regular Maintenance

Schedule monthly maintenance:

```python
# Monthly cleanup script
manager = CatalogManager(storage)

# Archive old epochs (keep 6 months)
archived = manager.archive_old_epochs(older_than_days=180)

# Validate integrity
integrity = manager.validate_catalog_integrity()

# Generate statistics
stats = manager.get_catalog_statistics()

print(f"Monthly Maintenance Report:")
print(f"  Archived: {len(archived)} epochs")
print(f"  Integrity: {'OK' if integrity.is_valid else 'ISSUES FOUND'}")
print(f"  Total Executions: {stats.total_executions}")
```

### 4. Export for Compliance

Export catalog data for external audit:

```python
# Get all executions from an epoch
executions = queries.query_with_pagination(
    filter=ExecutionFilter(epoch_id="epoch-20260210-123456"),
    page=1,
    page_size=1000
)

# Export to CSV
import csv

with open("fraud_analysis_audit_feb2026.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Execution ID", "Algorithm", "Timestamp", "Duration (ms)",
        "Status", "Result Count", "Risk Level"
    ])
    
    for exec in executions.items:
        writer.writerow([
            exec.execution_id,
            exec.algorithm,
            exec.execution_timestamp,
            exec.execution_duration_ms,
            exec.status,
            exec.result_summary.get("result_count", 0),
            exec.result_summary.get("risk_level", "N/A")
        ])

print("Exported to fraud_analysis_audit_feb2026.csv")
```

---

## Troubleshooting

### Issue: Catalog not tracking executions

**Check:**
1. Catalog is enabled: `FRAUD_ANALYSIS_ENABLE_CATALOG=true`
2. No initialization errors in output
3. Epoch was created successfully

**Fix:**
```bash
# Enable catalog explicitly
export FRAUD_ANALYSIS_ENABLE_CATALOG=true
python run_fraud_analysis.py
```

### Issue: Duplicate epochs created

**Cause:** Running multiple analyses in same month creates multiple epochs with same name

**Fix:** The workflow now checks for existing epochs and reuses them

### Issue: Catalog queries timing out

**Cause:** Large number of executions in catalog

**Solution:** Use pagination and filters:

```python
# Instead of getting all executions
executions = queries.query_with_pagination(
    filter=ExecutionFilter(
        start_date=datetime(2026, 2, 1),
        end_date=datetime(2026, 3, 1)
    ),
    page=1,
    page_size=20  # Small page size
)
```

### Issue: Storage growing too large

**Solution:** Regular archival and cleanup:

```python
# Archive epochs older than 6 months
manager.archive_old_epochs(older_than_days=180)

# Delete very old archived epochs if needed
old_epochs = catalog.query_epochs(
    filter=EpochFilter(status="archived"),
    limit=100
)

for epoch in old_epochs:
    age_days = (datetime.now() - epoch.end_date).days
    if age_days > 365:  # Older than 1 year
        catalog.delete_epoch(epoch.epoch_id)
```

---

## Summary

### What You Get

✅ **Automatic tracking** - No code changes needed  
✅ **Monthly epochs** - Organized by analysis period  
✅ **Full lineage** - Requirements → Results  
✅ **Historical data** - Compare trends over time  
✅ **Compliance ready** - Audit trail for regulators  
✅ **Performance monitoring** - Track execution times  

### How to Use

1. **Enable (default):** Just run `python run_fraud_analysis.py`
2. **Query history:** Use `CatalogQueries` to analyze past runs
3. **Generate reports:** Export data for compliance reviews
4. **Maintain catalog:** Archive old epochs regularly

### Next Steps

- Review tracked data: Check your first epoch
- Query historical trends: Compare this month vs last month
- Generate compliance reports: Export for regulatory review
- Set up maintenance: Schedule monthly cleanup

For more details, see:
- **Platform documentation:** `~/code/agentic-graph-analytics/CATALOG_STATUS_REPORT.md`
- **Catalog API:** `graph_analytics_ai/catalog/__init__.py`
- **Examples:** `graph_analytics_ai/catalog/queries.py` docstrings
