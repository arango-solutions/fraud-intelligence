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
import os
import sys
from pathlib import Path
from typing import List

def _require_platform():
    try:
        from graph_analytics_ai.ai.llm import create_llm_provider  # type: ignore
        from graph_analytics_ai.db_connection import get_db_connection  # type: ignore

        from graph_analytics_ai.ai.agents import (  # type: ignore
            OrchestratorAgent,
            AgentNames,
            SchemaAnalysisAgent,
            RequirementsAgent,
            UseCaseAgent,
            TemplateAgent,
            ExecutionAgent,
            ReportingAgent,
        )

        from graph_analytics_ai.ai.reporting import ReportGenerator, ReportFormat  # type: ignore

        return (
            create_llm_provider,
            get_db_connection,
            OrchestratorAgent,
            AgentNames,
            SchemaAnalysisAgent,
            RequirementsAgent,
            UseCaseAgent,
            TemplateAgent,
            ExecutionAgent,
            ReportingAgent,
            ReportGenerator,
            ReportFormat,
        )
    except ImportError as e:
        print("ERROR: graph-analytics-ai-platform is not available in this environment.")
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

    # Default to self-managed GAE (GenAI suite) unless AMP keys are present.
    # The upstream library defaults to AMP; if AMP keys are absent we must force
    # self-managed or execution will fail requesting ARANGO_GRAPH_API_KEY_*.
    mode = (os.getenv("GAE_DEPLOYMENT_MODE") or "").strip().lower()
    api_key_id = os.getenv("ARANGO_GRAPH_API_KEY_ID")  # may be unset or empty
    if (not mode or mode in ("amp", "managed", "arangograph")) and not api_key_id:
        os.environ["GAE_DEPLOYMENT_MODE"] = "self_managed"


async def main():
    """Run fraud intelligence graph analysis workflow."""
    
    print("=" * 70)
    print(" " * 15 + "FRAUD INTELLIGENCE GRAPH ANALYSIS")
    print(" " * 20 + "Indian Banking Fraud Detection")
    print("=" * 70)
    print()

    _apply_env_mapping()
    (
        create_llm_provider,
        get_db_connection,
        OrchestratorAgent,
        AgentNames,
        SchemaAnalysisAgent,
        RequirementsAgent,
        UseCaseAgent,
        TemplateAgent,
        ExecutionAgent,
        ReportingAgent,
        ReportGenerator,
        ReportFormat,
    ) = _require_platform()
    
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
    
    print("[1/4] Initializing agentic workflow...")
    print(f"      Graph: {GRAPH_NAME}")
    print(f"      Industry: {INDUSTRY}")
    
    try:
        db = get_db_connection()
        llm_provider = create_llm_provider()

        core_collections = [
            "Person",
            "BankAccount",
            "Organization",
            "RealProperty",
            "RealEstateTransaction",
            "DigitalLocation",
            "GoldenRecord",
        ]
        satellite_collections = ["Class", "Property", "Ontology"]

        agents = {
            AgentNames.SCHEMA_ANALYST: SchemaAnalysisAgent(
                llm_provider=llm_provider, db_connection=db
            ),
            AgentNames.REQUIREMENTS_ANALYST: RequirementsAgent(llm_provider=llm_provider),
            AgentNames.USE_CASE_EXPERT: UseCaseAgent(llm_provider=llm_provider),
            AgentNames.TEMPLATE_ENGINEER: TemplateAgent(
                llm_provider=llm_provider,
                graph_name=GRAPH_NAME,
                core_collections=core_collections,
                satellite_collections=satellite_collections,
            ),
            AgentNames.EXECUTION_SPECIALIST: ExecutionAgent(llm_provider=llm_provider),
            AgentNames.REPORTING_SPECIALIST: ReportingAgent(
                llm_provider=llm_provider, industry=INDUSTRY
            ),
        }

        orchestrator = OrchestratorAgent(llm_provider=llm_provider, agents=agents)
        report_generator = ReportGenerator(llm_provider=llm_provider, industry=INDUSTRY)

        print("✓ Initialized agents (fraud_intelligence reporting enabled)")
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
    enable_parallelism = os.getenv("FRAUD_ANALYSIS_PARALLELISM", "false").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    print(
        f"      🚀 Parallelism: {'ENABLED' if enable_parallelism else 'DISABLED'} "
        "(set FRAUD_ANALYSIS_PARALLELISM=true to enable)"
    )
    print()
    
    try:
        state = await orchestrator.run_workflow_async(
            input_documents=input_files if input_files else [],
            database_config=None,
            enable_parallelism=enable_parallelism,
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
    
    # Count insights and (if present) report risk levels
    total_insights = sum(len(getattr(r, "insights", []) or []) for r in state.reports)
    risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}

    for report in state.reports:
        level = (getattr(report, "metadata", {}) or {}).get("risk_level", "unknown")
        level = str(level).lower()
        if level not in risk_counts:
            level = "unknown"
        risk_counts[level] += 1
    
    print(f"✓ Total insights: {total_insights}")
    print("✓ Report risk levels:")
    for k in ["critical", "high", "medium", "low", "unknown"]:
        print(f"    - {k.upper()}: {risk_counts[k]}")
    
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
            md_content = report_generator.format_report(report, ReportFormat.MARKDOWN)
            md_path.write_text(md_content)
            print(f"  ✓ {md_path.name}")
        except Exception as e:
            print(f"  ✗ Failed to save Markdown: {e}")
        
        # Save HTML (if possible)
        html_path = output_dir / f"{report_name}.html"
        try:
            html_content = report_generator.format_report(report, ReportFormat.HTML)
            html_path.write_text(html_content)
            print(f"  ✓ {html_path.name}")
        except Exception as e:
            print(f"  ⚠ Failed to generate HTML: {e}")
        
        # Preview report
        print(f"\n  📊 Report {i}: {report.title}")
        print(f"     Algorithm: {report.metadata.get('algorithm', 'N/A')}")
        print(f"     Insights: {len(report.insights)}")
        
        # Show top insights
        for j, insight in enumerate(report.insights[:3], 1):
            conf = getattr(insight, "confidence", None)
            conf_str = f"{conf:.2f}" if isinstance(conf, (int, float)) else "N/A"
            print(f"       {j}. {insight.title}")
            print(f"          Confidence: {conf_str}")
        
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
    print(f"   - {risk_counts['critical']} CRITICAL risk findings")
    print(f"   - {risk_counts['high']} HIGH risk findings")
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
