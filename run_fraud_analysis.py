#!/usr/bin/env python3
"""
Fraud Intelligence Graph Analysis

This script runs AI-powered fraud detection on your Indian banking graph.
It uses the agentic-graph-analytics library with specialized fraud intelligence
prompts and pattern detectors.

Usage:
    python run_fraud_analysis.py

Requirements:
    - agentic-graph-analytics installed (pip install -e ~/code/agentic-graph-analytics)
    - .env file with ArangoDB credentials and LLM API keys
    - Graph data loaded in ArangoDB

Output:
    - Markdown reports in fraud_analysis_output/
    - HTML reports with charts (if enabled)
    - Fraud patterns with risk classifications
    - STR-ready recommendations
    - Historical tracking in analytics catalog (for compliance/audit)
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any

def _require_platform():
    try:
        from graph_analytics_ai.ai.llm import create_llm_provider  # type: ignore
        from graph_analytics_ai.db_connection import get_db_connection  # type: ignore

        from graph_analytics_ai.ai.agents import (  # type: ignore
            OrchestratorAgent,
            AgentNames,
            AgentDefaults,
            SchemaAnalysisAgent,
            RequirementsAgent,
            UseCaseAgent,
            TemplateAgent,
            ExecutionAgent,
            ReportingAgent,
        )

        from graph_analytics_ai.ai.reporting import ReportGenerator, ReportFormat  # type: ignore
        
        from graph_analytics_ai.catalog import (  # type: ignore
            AnalysisCatalog,
            CatalogQueries,
            ExecutionFilter,
            ExecutionStatus,
        )
        from graph_analytics_ai.catalog.storage import ArangoDBStorage  # type: ignore

        return (
            create_llm_provider,
            get_db_connection,
            OrchestratorAgent,
            AgentNames,
            AgentDefaults,
            SchemaAnalysisAgent,
            RequirementsAgent,
            UseCaseAgent,
            TemplateAgent,
            ExecutionAgent,
            ReportingAgent,
            ReportGenerator,
            ReportFormat,
            AnalysisCatalog,
            CatalogQueries,
            ExecutionFilter,
            ExecutionStatus,
            ArangoDBStorage,
        )
    except ImportError as e:
        print("ERROR: agentic-graph-analytics is not available in this environment.")
        print("\nFix:")
        print("  pip install -e ~/code/agentic-graph-analytics")
        print("\nOr:")
        print("  cd ~/code/agentic-graph-analytics && pip install -e .")
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

    # Bridge variable names (apply_config_to_env sets both when it runs)
    if os.getenv("ARANGO_ENDPOINT") is None and os.getenv("ARANGO_URL"):
        try:
            from common import ensure_endpoint_has_port  # type: ignore
            endpoint = ensure_endpoint_has_port(os.environ["ARANGO_URL"])
        except Exception:
            endpoint = os.environ["ARANGO_URL"]
        os.environ["ARANGO_ENDPOINT"] = endpoint
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
        AgentDefaults,
        SchemaAnalysisAgent,
        RequirementsAgent,
        UseCaseAgent,
        TemplateAgent,
        ExecutionAgent,
        ReportingAgent,
        ReportGenerator,
        ReportFormat,
        AnalysisCatalog,
        CatalogQueries,
        ExecutionFilter,
        ExecutionStatus,
        ArangoDBStorage,
    ) = _require_platform()

    # Optional: run more (or all) use cases per execution.
    # The upstream agentic workflow defaults to 3 for safety/demo speed.
    max_exec_raw = (os.getenv("FRAUD_ANALYSIS_MAX_EXECUTIONS") or "").strip()
    if max_exec_raw:
        try:
            max_exec = int(max_exec_raw)
            if max_exec > 0:
                AgentDefaults.MAX_EXECUTIONS = max_exec
        except ValueError:
            # Ignore invalid values (keep platform defaults).
            pass
    
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
    # STEP 1: Initialize Workflow Runner & Catalog
    # ========================================================================
    
    print("[1/5] Initializing agentic workflow...")
    print(f"      Graph: {GRAPH_NAME}")
    print(f"      Industry: {INDUSTRY}")
    
    # Check if catalog tracking should be enabled
    enable_catalog = os.getenv("FRAUD_ANALYSIS_ENABLE_CATALOG", "true").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    
    try:
        db = get_db_connection()
        llm_provider = create_llm_provider()
        
        # Initialize catalog (optional but recommended for compliance)
        catalog: Optional[Any] = None
        current_epoch: Optional[Any] = None
        
        if enable_catalog:
            try:
                storage = ArangoDBStorage(db)
                catalog = AnalysisCatalog(storage)
                
                # Create epoch for this analysis period
                epoch_name = f"fraud-detection-{datetime.now().strftime('%Y-%m')}"
                
                # Check if epoch already exists
                try:
                    existing_epochs = catalog.query_epochs(
                        filter=None,  # Get all epochs
                        limit=100
                    )
                    current_epoch = next(
                        (e for e in existing_epochs if e.name == epoch_name), 
                        None
                    )
                except Exception:
                    current_epoch = None
                
                if current_epoch:
                    print(f"✓ Using existing epoch: {epoch_name}")
                else:
                    current_epoch = catalog.create_epoch(
                        name=epoch_name,
                        description=f"Monthly fraud detection analysis for Indian banking - {datetime.now().strftime('%B %Y')}",
                        tags=["production", "fraud_intelligence", "monthly", "india", "compliance"]
                    )
                    print(f"✓ Created catalog epoch: {epoch_name}")
                
                print(f"  Epoch ID: {current_epoch.epoch_id}")
                print("  📊 Catalog tracking ENABLED (for compliance/audit)")
            except Exception as e:
                print(f"⚠ Failed to initialize catalog: {e}")
                print("  Continuing without catalog tracking...")
                catalog = None
                current_epoch = None
        else:
            print("  📊 Catalog tracking DISABLED")
            print("     (Set FRAUD_ANALYSIS_ENABLE_CATALOG=true to enable)")

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
            AgentNames.REQUIREMENTS_ANALYST: RequirementsAgent(
                llm_provider=llm_provider,
                catalog=catalog  # ← Catalog integration
            ),
            AgentNames.USE_CASE_EXPERT: UseCaseAgent(
                llm_provider=llm_provider,
                catalog=catalog  # ← Catalog integration
            ),
            AgentNames.TEMPLATE_ENGINEER: TemplateAgent(
                llm_provider=llm_provider,
                graph_name=GRAPH_NAME,
                core_collections=core_collections,
                satellite_collections=satellite_collections,
                catalog=catalog  # ← Catalog integration
            ),
            AgentNames.EXECUTION_SPECIALIST: ExecutionAgent(
                llm_provider=llm_provider,
                catalog=catalog  # ← Catalog integration
            ),
            AgentNames.REPORTING_SPECIALIST: ReportingAgent(
                llm_provider=llm_provider, industry=INDUSTRY
            ),
        }

        orchestrator = OrchestratorAgent(
            llm_provider=llm_provider, 
            agents=agents,
            catalog=catalog  # ← Catalog integration
        )
        report_generator = ReportGenerator(llm_provider=llm_provider, industry=INDUSTRY)

        # Associate executor with current epoch so executions are linked to this epoch
        if catalog and current_epoch:
            agents[AgentNames.EXECUTION_SPECIALIST].executor.epoch_id = (
                current_epoch.epoch_id
            )

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
    
    print("[2/5] Running agentic workflow...")
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
        if enable_parallelism:
            state = await orchestrator.run_workflow_async(
                input_documents=input_files if input_files else [],
                database_config=None,
                enable_parallelism=True,
            )
        else:
            # Run synchronously to avoid parallel template execution (which can
            # overwhelm the self-managed GRAL service and cause 503/500 errors).
            state = orchestrator.run_workflow(
                input_documents=input_files if input_files else [],
                database_config=None,
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
    
    print("[3/5] Processing results...")
    
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
    # STEP 4: Query Catalog (if enabled)
    # ========================================================================
    
    if catalog and current_epoch:
        print("[4/5] Querying catalog for historical context...")
        
        try:
            queries = CatalogQueries(storage)
            
            # Get all executions from this epoch
            recent_executions = queries.query_with_pagination(
                filter=ExecutionFilter(
                    epoch_id=current_epoch.epoch_id,
                    status=ExecutionStatus.COMPLETED,
                ),
                page=1,
                page_size=100
            )
            
            print(f"✓ Tracked {recent_executions.total_count} executions in catalog:")
            
            # Group by algorithm
            by_algorithm = {}
            for exec in recent_executions.items:
                algo = exec.algorithm
                if algo not in by_algorithm:
                    by_algorithm[algo] = []
                by_algorithm[algo].append(exec)
            
            for algo, execs in by_algorithm.items():
                avg_duration_ms = sum(
                    e.performance_metrics.execution_time_seconds * 1000 for e in execs
                ) / len(execs)
                total_results = sum(getattr(e, "result_count", 0) for e in execs)
                print(f"  - {algo.upper()}: {len(execs)} runs, avg {avg_duration_ms:.0f}ms, {total_results} total results")
            
            print("  📈 Full execution history stored for compliance/audit")
            
        except Exception as e:
            print(f"⚠ Failed to query catalog: {e}")
    else:
        print("[4/5] Catalog tracking disabled, skipping history query")
    
    print()
    
    # ========================================================================
    # STEP 5: Save Reports
    # ========================================================================
    
    print("[5/5] Saving reports...")
    
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
    
    if catalog and current_epoch:
        print("📊 Catalog Information:")
        print(f"   - Epoch: {current_epoch.name}")
        print(f"   - Epoch ID: {current_epoch.epoch_id}")
        print("   - All executions tracked for compliance/audit")
        print("   - Query history: Use catalog.query_executions()")
        print("   - View lineage: Use LineageTracker")
        print()
        print("   Example queries:")
        print("     from graph_analytics_ai.catalog import CatalogQueries, ExecutionFilter")
        print("     queries = CatalogQueries(storage)")
        print(f"     history = queries.query_with_pagination(filter=ExecutionFilter(epoch_id='{current_epoch.epoch_id}'))")
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
