# Graph Analytics AI Platform - Setup Guide for Fraud Intelligence Demo

**Project:** Fraud Intelligence Demo  
**Platform:** graph-analytics-ai (v3.2.0+)  
**Industry:** Indian Banking / Fraud Detection

> **Note (template / forward-looking):** This guide is for an *optional future integration* with an external
> “graph-analytics-ai” platform. It is not required for the current Phase 1–3 scripts in this repo.
> Any dataset sizes and credentials shown below are **illustrative**. Do not paste real secrets into docs.

---

## Overview

This guide shows how to integrate the **graph-analytics-ai** platform into your fraud-intelligence project to get AI-powered fraud detection insights.

### How this relates to the current repo

This repo already ships a working Phase 1–3 demo using ArangoDB + AQL:

- Phase 1 runner: `python scripts/test_phase1.py --remote-only --install-visualizer`
- Phase 2 runner: `python scripts/test_phase2.py --remote-only`
- Phase 3 runner: `python scripts/test_phase3.py --remote-only`
- Named graphs: `OntologyGraph`, `DataGraph`, `KnowledgeGraph`

The “graph-analytics-ai” platform integration described below is an **optional next step** to showcase
agentic orchestration and algorithm-backed reporting beyond the Visualizer.

---

## Prerequisites

1. **Graph Analytics AI Platform** installed
2. **ArangoDB cluster** with fraud intelligence data loaded
3. **LLM API key** (OpenRouter, OpenAI, or Anthropic)
4. **Python 3.10+**

---

## Step 1: Install graph-analytics-ai Library

```bash
cd ~/code/fraud-intelligence

# Install the library
pip install -e ~/code/graph-analytics-ai-platform

# Verify installation
python -c "from graph_analytics_ai.ai.agents import AgenticWorkflowRunner; print('✓ Installed')"
```

---

## Step 2: Configure Environment

Create `.env` file in your fraud-intelligence project (do **not** commit it):

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
vim .env
```

**.env file contents (example placeholders):**

```env
# ArangoDB Configuration (align to this repo's scripts)
MODE=REMOTE
ARANGO_URL=https://your-cluster.arangodb.cloud:8529
ARANGO_DATABASE=fraud-intelligence
ARANGO_USERNAME=root
ARANGO_PASSWORD=your_password

# Optional: platform-specific keys (if required by your deployment)
# ARANGO_GRAPH_API_KEY_ID=...
# ARANGO_GRAPH_API_KEY_SECRET=...

# LLM Configuration
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemini-2.0-flash-exp

# Workflow Configuration
WORKFLOW_OUTPUT_DIR=./fraud_analysis_output
AI_WORKFLOW_ENABLED=true
```

---

## Step 3: Test Connection

```bash
# Test database connection
python -m graph_analytics_ai.cli.test_connection
```

Expected output:
```
✅ ArangoDB connection successful
✅ Database 'fraud_intelligence' accessible
✅ GAE engine available
```

---

## Step 4: Create Domain Description Document

This repo already contains `docs/domain_description.md`. Review/update it as needed rather than re-creating it from scratch.

```markdown
# Fraud Intelligence - Indian Banking Domain

**Industry:** Banking & Financial Services  
**Geography:** India  
**Focus:** Fraud Detection & AML Compliance

## Domain Context

### Business Context
Indian banking fraud detection system designed to identify:
- Circular trading and layering schemes
- Money mule networks (smurfing/structuring)
- Circle rate evasion in property transactions
- Benami transactions (proxy identities)
- Hawala network indicators

### Graph Structure

**Vertex Collections (Entities):**
- **Person** (10,000+): Bank customers, beneficial owners
- **BankAccount** (15,000+): Bank accounts and instruments
- **Organization** (2,000+): Companies, shell corporations
- **RealProperty** (5,000+): Real estate with circle rate data
- **WatchlistEntity** (500+): Regulatory watchlists, defaulters
- **DigitalLocation** (8,000+): IP addresses, devices
- **Transaction** (50,000+): Money transfers
- **GoldenRecord** (8,000+): Resolved identities post-ER

**Edge Collections (Relationships):**
- **transferredTo** (50,000+): Money flows between accounts
- **hasAccount**: Account ownership/control
- **resolvedTo**: Identity resolution (Person → GoldenRecord)
- **relatedTo**: Family/social relationships
- **associatedWith**: Directors, partners, UBOs
- **residesAt**: Physical addresses
- **accessedFrom**: Digital access patterns
- **registeredSale**: Property sales

**Named Graph:** Use `KnowledgeGraph` for investigations in this repo (or configure an equivalent graph name in your platform).

### Scale & Activity
- Total nodes: ~40,000
- Total edges: ~80,000
- Transaction volume: ₹500+ Crores monitored
- Watchlist entities: 500+ high-risk
- Resolved identities: 8,000+ golden records

### Domain-Specific Terminology

**Indian Banking / Regulatory:**
- **Benami Transaction**: Proxy/nominee transaction to hide beneficial owner
- **Circle Rate**: Government-mandated minimum property value (varies by area)
- **CTR**: Cash Transaction Report (required for ₹10 Lakhs+)
- **STR**: Suspicious Transaction Report (to FIU-IND)
- **FIU-IND**: Financial Intelligence Unit - India
- **PMLA**: Prevention of Money Laundering Act, 2002
- **FEMA**: Foreign Exchange Management Act
- **KYC**: Know Your Customer compliance
- **PAN**: Permanent Account Number (tax identifier)
- **Aadhaar**: Biometric identity number

**Fraud Patterns:**
- **Circular Trading**: Round-trip transfers A→B→C→A (layering)
- **Money Mule**: Low-level account in fund transfer chain
- **Smurfing**: Structuring transactions below reporting threshold
- **Hawala**: Informal value transfer system (unregulated)
- **Shell Company**: Corporation with no real operations
- **Layering**: Complex transaction chains to obscure fund source

### Data Characteristics
- **Transaction data**: 12 months of transfers with amounts, timestamps
- **Identity data**: Names, PAN, addresses, phone numbers
- **Real estate data**: Properties with circle rates and market values
- **Digital forensics**: IP addresses, devices, access logs
- **Watchlists**: RBI defaulters, ED investigations, sanctions lists
- **Entity resolution**: Phonetic matching for Indian names

---

## Business Objectives

### OBJ-001: Detect Circular Trading Schemes
**Priority:** Critical  
**Goal:** Identify closed-loop money transfers indicative of layering operations.

**Success Criteria:**
- Detect all cycles of length 3-6 accounts
- Calculate total amount cycled
- Identify timing patterns (velocity)
- Flag for STR filing

**Expected Value:** Prevent ₹50+ Cr annual laundering exposure

### OBJ-002: Identify Money Mule Networks
**Priority:** Critical  
**Goal:** Find hub-and-spoke patterns where many accounts funnel to central aggregator.

**Success Criteria:**
- Detect hub accounts with 20+ inbound transfers
- Identify shared digital footprint across mules
- Calculate structuring patterns (amounts below ₹10L CTR threshold)
- Map complete mule network topology

**Expected Value:** Disrupt 80% of smurfing operations, improve CTR compliance

### OBJ-003: Flag Circle Rate Evasion
**Priority:** High  
**Goal:** Identify real estate transactions at/below circle rate indicating tax evasion and money laundering.

**Success Criteria:**
- Find properties where transactionValue ≤ circleRateValue
- Calculate estimated tax evasion exposure
- Identify repeat offenders (sellers/buyers)
- Cross-reference with high-risk entities

**Expected Value:** Recover ₹10+ Cr in evaded stamp duty, detect laundering vehicles

### OBJ-004: Resolve Benami Identities
**Priority:** High  
**Goal:** Consolidate duplicate/proxy identities to reveal hidden beneficial ownership.

**Success Criteria:**
- Resolve 80%+ of duplicate Person records
- Create GoldenRecord entities
- Map hidden account control
- Update risk propagation based on resolved identities

**Expected Value:** 40% improvement in KYC accuracy, detect hidden ownership structures

### OBJ-005: Assess Risk Propagation
**Priority:** High  
**Goal:** Calculate and propagate risk from known bad actors (watchlist) to connected entities.

**Success Criteria:**
- Implement risk scoring (direct, inferred, path)
- Calculate risk contagion across network
- Generate risk reasons for audit trail
- Prioritize investigations by risk score

**Expected Value:** 60% reduction in false positives, focus resources on high-risk

---

## Constraints & Considerations

### Regulatory Compliance
- Must generate audit trail for all risk assessments
- STR filing required within 7 days of detection
- PAN verification mandatory for high-risk entities
- Watchlist screening required

### Performance
- Analysis must complete within 5 minutes for demo
- Support real-time risk scoring (<1 second per entity)
- Handle 40K nodes, 80K edges efficiently

### Accuracy
- False positive rate < 5% for fraud detection
- Confidence scores ≥ 70% for regulatory actions
- Entity resolution accuracy ≥ 95%

---

## Indian Context Requirements

When generating insights, the AI must:
- Use ₹ Crores/Lakhs for currency amounts
- Reference Indian regulations (PMLA, FEMA, Benami Act)
- Cite FIU-IND reporting requirements
- Consider Indian name variations (phonetic matching)
- Account for circle rate data in property analysis
- Understand Indian banking thresholds (₹10L CTR, ₹20L PAN)
```

---

## Step 5: Create Use Cases Document

This repo already contains `docs/business_requirements.md`. Review/update it as needed rather than re-creating it from scratch.

See next section for full template...

---

## Step 6: Run Agentic Workflow with Fraud Intelligence Industry

Create `run_fraud_detection_workflow.py`:

```python
"""
Fraud Intelligence Demo - Agentic Workflow
Runs autonomous fraud detection analysis on Indian banking graph
"""

import asyncio
from graph_analytics_ai.ai.agents import AgenticWorkflowRunner

async def main():
    """Run fraud detection analysis with Indian banking context."""
    
    print("=" * 60)
    print("FRAUD INTELLIGENCE DEMO - Agentic Workflow")
    print("=" * 60)
    print()
    print("Domain: Indian Banking - Fraud Detection")
    print("Graph: fraud_intelligence_graph")
    print("Industry: fraud_intelligence (optimized for AML/fraud patterns)")
    print()
    
    # Initialize agentic workflow with fraud intelligence industry
    runner = AgenticWorkflowRunner(
        graph_name="fraud_intelligence_graph",
        enable_tracing=True,
        industry="fraud_intelligence"  # Key: Use fraud intelligence prompts
    )
    
    # Run with parallelism for speed (demo requirement: <2 minutes)
    print("Starting autonomous fraud detection workflow...")
    print("This will:")
    print("  1. Analyze graph schema")
    print("  2. Extract fraud detection requirements")
    print("  3. Generate fraud detection use cases")
    print("  4. Create GAE analysis templates")
    print("  5. Execute fraud detection algorithms")
    print("  6. Generate intelligence reports with fraud insights")
    print()
    
    state = await runner.run_async(
        enable_parallelism=True,
        input_files=["docs/business_requirements.md"]  # Optional
    )
    
    # Display results
    print()
    print("=" * 60)
    print("FRAUD DETECTION ANALYSIS COMPLETE")
    print("=" * 60)
    print()
    print(f"Status: {state.status}")
    print(f"Reports Generated: {len(state.reports)}")
    print()
    
    # Show fraud intelligence reports
    for i, report in enumerate(state.reports, 1):
        print(f"\n{'='*60}")
        print(f"REPORT {i}: {report.title}")
        print(f"{'='*60}")
        print(f"\nSummary: {report.summary}")
        print(f"\nInsights: {len(report.insights)}")
        
        for j, insight in enumerate(report.insights, 1):
            print(f"\n  [{j}] {insight.title}")
            print(f"      Risk: {insight.metadata.get('risk_level', 'N/A')}")
            print(f"      Confidence: {insight.confidence:.0%}")
            print(f"      Impact: {insight.business_impact[:100]}...")
        
        print(f"\nRecommendations: {len(report.recommendations)}")
        for j, rec in enumerate(report.recommendations, 1):
            print(f"  [{j}] {rec.title}")
            print(f"      Priority: {rec.priority.value}")
    
    # Show trace summary (performance metrics)
    print()
    print("=" * 60)
    print("PERFORMANCE METRICS")
    print("=" * 60)
    runner.print_trace_summary()
    
    # Export reports
    print()
    print("Exporting reports...")
    from pathlib import Path
    output_dir = Path("fraud_analysis_output")
    output_dir.mkdir(exist_ok=True)
    
    for i, report in enumerate(state.reports):
        # Export as Markdown
        md_path = output_dir / f"fraud_report_{i+1}.md"
        from graph_analytics_ai.ai.reporting import ReportFormat, HTMLReportFormatter
        from graph_analytics_ai.ai.reporting.formatter import format_report
        
        markdown = format_report(report, ReportFormat.MARKDOWN)
        md_path.write_text(markdown)
        
        # Export as HTML with charts
        html_path = output_dir / f"fraud_report_{i+1}.html"
        html_formatter = HTMLReportFormatter()
        charts = report.metadata.get('charts', {})
        html = html_formatter.format_report(report, charts=charts)
        html_path.write_text(html)
        
        print(f"  ✓ {md_path}")
        print(f"  ✓ {html_path}")
    
    print()
    print(f"✅ Fraud detection analysis complete!")
    print(f"   View reports in: {output_dir}/")
    print()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Step 7: Key Configuration Differences

### For Fraud Intelligence (vs generic e-commerce):

```python
# When initializing AgenticWorkflowRunner
runner = AgenticWorkflowRunner(
    graph_name="fraud_intelligence_graph",  # Your graph name
    industry="fraud_intelligence",  # KEY: Activates Indian banking prompts
    enable_tracing=True
)

# When using ReportGenerator directly
from graph_analytics_ai.ai.reporting import ReportGenerator

generator = ReportGenerator(
    industry="fraud_intelligence",  # Activates fraud detection patterns
    enable_charts=True  # Interactive charts for fraud analysis
)
```

### Supported Industry Values for Fraud:
- `fraud_intelligence` (recommended)
- `fraud` (alias)
- `aml` (alias)
- `indian_banking` (alias)

---

## Step 8: Expected Output

With `industry="fraud_intelligence"`, the platform will:

### Prompts Include:
- Indian regulatory context (PMLA, FEMA, Benami Act, FIU-IND)
- Currency in ₹ Crores and Lakhs
- Indian banking thresholds (₹10L CTR, ₹20L PAN)
- Circle rate fraud detection
- Benami transaction patterns

### Pattern Detection:
- **WCC**: Money mule networks, Benami clusters, isolated high-risk actors
- **PageRank**: Transaction hubs, concentration risk, aggregator accounts
- **Cycles**: Circular trading rings (if cycle detection enabled)

### Insights Will Reference:
- Specific account IDs
- Transaction amounts in Indian Rupees
- Risk classifications (CRITICAL/HIGH/MEDIUM/LOW)
- Regulatory filing requirements (STR/CTR)
- Indian banking regulations
- Immediate action items (freeze, investigate, file STR)

---

## Example Usage Scenarios

### Scenario 1: Autonomous Fraud Detection

```python
from graph_analytics_ai.ai.agents import AgenticWorkflowRunner
import asyncio

async def detect_fraud():
    runner = AgenticWorkflowRunner(
        graph_name="fraud_intelligence_graph",
        industry="fraud_intelligence"
    )
    
    # AI autonomously:
    # - Analyzes your fraud graph schema
    # - Identifies appropriate fraud detection algorithms
    # - Executes analyses
    # - Generates fraud intelligence reports
    
    state = await runner.run_async(enable_parallelism=True)
    
    # Get fraud insights
    for report in state.reports:
        print(f"\n{report.title}")
        for insight in report.insights:
            risk = insight.metadata.get('risk_level', 'N/A')
            print(f"  [{risk}] {insight.title}")

asyncio.run(detect_fraud())
```

### Scenario 2: With Custom Requirements

```python
from graph_analytics_ai.ai.agents import AgenticWorkflowRunner

runner = AgenticWorkflowRunner(
    graph_name="fraud_intelligence_graph",
    industry="fraud_intelligence"
)

# Provide your business requirements document
state = runner.run(
    input_files=["docs/business_requirements.md"]
)

# AI will tailor analysis to your specific requirements
```

### Scenario 3: Manual Control with Fraud Context

```python
from graph_analytics_ai.ai.workflow import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(
    graph_name="fraud_intelligence_graph",
    industry="fraud_intelligence"  # Applies to all steps
)

# Step-by-step control with fraud intelligence context
result = orchestrator.run_complete_workflow(
    input_files=["docs/business_requirements.md"]
)
```

---

## Verification Checklist

Before running your demo:

- [ ] Library installed: `pip list | grep graph-analytics-ai`
- [ ] .env configured with database credentials
- [ ] Connection test passes
- [ ] Domain description created
- [ ] Business requirements documented
- [ ] Test run completes successfully
- [ ] Reports generate with fraud-specific insights
- [ ] Output includes Indian rupee amounts (₹ Cr/Lakhs)
- [ ] Reports reference PMLA/FIU-IND appropriately

---

## Troubleshooting

### Issue: Generic insights instead of fraud-specific

**Check:** Verify `industry="fraud_intelligence"` is passed:
```python
runner = AgenticWorkflowRunner(
    graph_name="fraud_intelligence_graph",
    industry="fraud_intelligence"  # Must specify!
)
```

### Issue: No circle rate insights

**Check:** Ensure your RealProperty nodes have:
- `circleRateValue` field
- `marketValue` field
- RealEstateTransaction has `transactionValue` field

### Issue: No Benami detection

**Check:** Ensure entity resolution has run:
- GoldenRecord collection exists
- resolvedTo edges present
- Multiple Person → GoldenRecord links exist

---

## Next Steps

1. ✅ Complete this setup guide
2. Create domain description (template below)
3. Create business requirements document (template below)
4. Run test workflow
5. Review generated reports
6. Prepare demo presentation

---

## Support

See graph-analytics-ai documentation:
- Main README: `~/code/graph-analytics-ai-platform/README.md`
- Industry prompts: `graph_analytics_ai/ai/reporting/prompts.py`
- Pattern detection: `graph_analytics_ai/ai/reporting/algorithm_insights.py`

---

**Setup Status:** Ready to implement  
**Next:** Create domain description and business requirements
