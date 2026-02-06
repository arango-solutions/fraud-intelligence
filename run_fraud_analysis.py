#!/usr/bin/env python3
"""
Fraud Intelligence Graph Analysis

This script runs AI-powered fraud detection on your Indian banking graph.
It uses the graph-analytics-ai-platform with specialized fraud intelligence
prompts and pattern detectors.

Usage:
    python run_fraud_analysis.py

Requirements:
    - graph-analytics-ai-platform installed (pip install -e ~/code/graph-analytics-ai-platform)
    - .env file with ArangoDB credentials and LLM API keys
    - Graph data loaded in ArangoDB

Output:
    - Markdown reports in fraud_analysis_output/
    - HTML reports with charts (if enabled)
    - Fraud patterns with risk classifications
    - STR-ready recommendations
"""

import asyncio
import sys
from pathlib import Path
from typing import List

def _require_platform():
    try:
        from graph_analytics_ai.ai.agents import AgenticWorkflowRunner
        from graph_analytics_ai.ai.reporting import ReportFormat
        from graph_analytics_ai.ai.reporting.formatter import format_report

        return AgenticWorkflowRunner, ReportFormat, format_report
    except ImportError as e:
        print("ERROR: graph-analytics-ai-platform not installed")
        print("\nFix:")
        print("  pip install -e ~/code/graph-analytics-ai-platform")
        print("\nOr:")
        print("  cd ~/code/graph-analytics-ai-platform && pip install -e .")
        raise SystemExit(1) from e


def _apply_env_mapping() -> None:
    """
    Map this repo's env naming (ARANGO_URL/ARANGO_USERNAME) to the platform's
    expected naming (ARANGO_ENDPOINT/ARANGO_USER) without printing secrets.
    """
    # Prefer this repo's config helpers if available.
    try:
        sys.path.insert(0, "scripts")
        from common import apply_config_to_env, get_arango_config, load_dotenv  # type: ignore

        load_dotenv()
        cfg = get_arango_config(forced_mode=os.getenv("MODE") or None)
        apply_config_to_env(cfg)
    except Exception:
        # Fall back to env-only; do not error here.
        pass

    # Bridge variable names.
    if os.getenv("ARANGO_ENDPOINT") is None and os.getenv("ARANGO_URL"):
        os.environ["ARANGO_ENDPOINT"] = os.environ["ARANGO_URL"]
    if os.getenv("ARANGO_USER") is None and os.getenv("ARANGO_USERNAME"):
        os.environ["ARANGO_USER"] = os.environ["ARANGO_USERNAME"]


async def main():
    """Run fraud intelligence graph analysis workflow."""

    import os
    
    print("=" * 70)
    print(" " * 15 + "FRAUD INTELLIGENCE GRAPH ANALYSIS")
    print(" " * 20 + "Indian Banking Fraud Detection")
    print("=" * 70)
    print()

    _apply_env_mapping()
    AgenticWorkflowRunner, ReportFormat, format_report = _require_platform()
    
    # ========================================================================
    # CONFIGURATION
    # ========================================================================
    
    # Output directory for reports
    output_dir = Path("fraud_analysis_output")
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Output directory: {output_dir.absolute()}")
    
    # Graph configuration (CHANGE THESE if needed)
    # This repo's implemented demo graphs are: KnowledgeGraph / DataGraph / OntologyGraph
    GRAPH_NAME = os.getenv("FRAUD_GRAPH_NAME") or "KnowledgeGraph"
    INDUSTRY = "fraud_intelligence"          # Enables fraud-specific patterns
    
    # Input files for context (optional but recommended)
    input_files: List[str] = []
    possible_inputs = [
        "docs/business_requirements.md",
        "docs/domain_description.md",
        "PRD/Fraud Use Cases PRD.md",
        "PRD/PRD.md",
    ]
    
    for filepath in possible_inputs:
        if Path(filepath).exists():
            input_files.append(filepath)
    
    if input_files:
        print(f"✓ Using {len(input_files)} input files for context:")
        for f in input_files:
            print(f"    - {f}")
    else:
        print("⚠ No input files found (analysis will be generic)")
    
    print()
    
    # ========================================================================
    # STEP 1: Initialize Workflow Runner
    # ========================================================================
    
    print("[1/4] Initializing workflow runner...")
    print(f"      Graph: {GRAPH_NAME}")
    print(f"      Industry: {INDUSTRY}")
    
    try:
        runner = AgenticWorkflowRunner(
            graph_name=GRAPH_NAME,
            industry=INDUSTRY,
            enable_tracing=True  # Helpful for debugging
        )
        print("✓ Runner initialized with fraud_intelligence industry")
    except Exception as e:
        print(f"✗ Failed to initialize runner: {e}")
        print("\nCheck:")
        print("  1. Is your .env file configured?")
        print("  2. Can you connect to ArangoDB?")
        print("     Test: python -m graph_analytics_ai.cli.test_connection")
        sys.exit(1)
    
    print()
    
    # ========================================================================
    # STEP 2: Run Agentic Workflow
    # ========================================================================
    
    print("[2/4] Running agentic workflow...")
    print("      This orchestrates multiple AI agents to:")
    print("        - Analyze your graph schema")
    print("        - Generate fraud detection queries")
    print("        - Execute graph algorithms (WCC, PageRank, cycles)")
    print("        - Detect fraud patterns (mule networks, circular trading)")
    print("        - Generate intelligence reports with recommendations")
    print()
    print("      ⏱  Expected time: 1-3 minutes")
    print("      🚀 Parallelism: ENABLED for faster execution")
    print()
    
    try:
        state = await runner.run_async(
            enable_parallelism=True,  # Parallel execution for speed
            input_files=input_files if input_files else None
        )
        print("✓ Workflow completed successfully")
    except Exception as e:
        print(f"✗ Workflow failed: {e}")
        print("\nCommon issues:")
        print("  - Graph doesn't exist in ArangoDB")
        print("  - Insufficient permissions")
        print("  - LLM API key invalid or rate limited")
        print("  - Out of memory (try enable_parallelism=False)")
        sys.exit(1)
    
    print()
    
    # ========================================================================
    # STEP 3: Process Results
    # ========================================================================
    
    print("[3/4] Processing results...")
    
    if not state.reports:
        print("✗ No reports generated")
        print("\nPossible reasons:")
        print("  - Graph has no data")
        print("  - Collection names don't match expected schema")
        print("  - Queries returned no results")
        print("\nCheck workflow state for errors:")
        print(f"  State: {state}")
        sys.exit(1)
    
    print(f"✓ Generated {len(state.reports)} intelligence reports")
    
    # Count total insights and risk levels
    total_insights = sum(len(r.insights) for r in state.reports)
    risk_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    
    for report in state.reports:
        for insight in report.insights:
            risk = insight.metadata.get('risk_level', 'UNKNOWN')
            if risk in risk_counts:
                risk_counts[risk] += 1
    
    print(f"✓ Total insights: {total_insights}")
    print(f"    - CRITICAL: {risk_counts['CRITICAL']}")
    print(f"    - HIGH: {risk_counts['HIGH']}")
    print(f"    - MEDIUM: {risk_counts['MEDIUM']}")
    print(f"    - LOW: {risk_counts['LOW']}")
    
    print()
    
    # ========================================================================
    # STEP 4: Save Reports
    # ========================================================================
    
    print("[4/4] Saving reports...")
    
    for i, report in enumerate(state.reports, 1):
        report_name = f"fraud_report_{i}"
        
        # Save Markdown
        md_path = output_dir / f"{report_name}.md"
        try:
            md_content = format_report(report, ReportFormat.MARKDOWN)
            md_path.write_text(md_content)
            print(f"  ✓ {md_path.name}")
        except Exception as e:
            print(f"  ✗ Failed to save Markdown: {e}")
        
        # Save HTML (if possible)
        html_path = output_dir / f"{report_name}.html"
        try:
            from graph_analytics_ai.ai.reporting import HTMLReportFormatter
            html_formatter = HTMLReportFormatter()
            charts = report.metadata.get('charts', {})
            html_content = html_formatter.format_report(report, charts=charts)
            html_path.write_text(html_content)
            print(f"  ✓ {html_path.name}")
        except ImportError:
            print(f"  ⚠ HTML formatter not available, skipping {html_path.name}")
        except Exception as e:
            print(f"  ⚠ Failed to generate HTML: {e}")
        
        # Preview report
        print(f"\n  📊 Report {i}: {report.title}")
        print(f"     Algorithm: {report.metadata.get('algorithm', 'N/A')}")
        print(f"     Insights: {len(report.insights)}")
        
        # Show top insights
        for j, insight in enumerate(report.insights[:3], 1):
            risk = insight.metadata.get('risk_level', 'N/A')
            conf = insight.metadata.get('confidence', 0.0)
            print(f"       {j}. [{risk}] {insight.title}")
            print(f"          Confidence: {conf:.2f}")
        
        if len(report.insights) > 3:
            print(f"       ... and {len(report.insights) - 3} more insights")
        
        print()
    
    # ========================================================================
    # COMPLETION
    # ========================================================================
    
    print("=" * 70)
    print(" " * 25 + "✓ ANALYSIS COMPLETE")
    print("=" * 70)
    print()
    print(f"📁 Reports saved to: {output_dir.absolute()}")
    print()
    print("📝 What you have:")
    print(f"   - {len(state.reports)} intelligence reports")
    print(f"   - {total_insights} fraud pattern insights")
    print(f"   - {risk_counts['CRITICAL']} CRITICAL risk findings")
    print(f"   - {risk_counts['HIGH']} HIGH risk findings")
    print()
    print("🎯 Next steps:")
    print("   1. Open HTML reports in your browser")
    print(f"      Example: open {output_dir}/fraud_report_1.html")
    print("   2. Review CRITICAL and HIGH risk insights")
    print("   3. Identify accounts requiring:")
    print("      - Immediate account freeze")
    print("      - STR filing with FIU-IND")
    print("      - Enhanced due diligence")
    print("   4. Share reports with compliance team")
    print("   5. Update monitoring rules based on patterns")
    print()
    print("💡 To run again:")
    print("   python run_fraud_analysis.py")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
