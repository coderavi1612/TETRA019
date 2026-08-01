import os
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, Any

from app.config import settings
from app.readiness.context import ReportContextBuilder
from app.readiness.scoring import ReadinessScoringEngine
from app.readiness.ai.orchestrator import ReadinessAiOrchestrator
from app.readiness.generator import ReportAssembler
from app.readiness.markdown import MarkdownReportGenerator
from app.readiness.pdf import PdfReportAssembler

class ReadinessOrchestrator:
    @staticmethod
    def run_readiness_pipeline(company_id: str, outputs_dir: str = None) -> Dict[str, Any]:
        """
        Coordinates E2E Milestone 5 pipeline.
        """
        if outputs_dir is None:
            outputs_dir = settings.OUTPUT_DIR
            
        from app.core.logging import DuelensLogger
        from app.core.timing import Timer
        
        DuelensLogger.log("Readiness", "START", f"Starting readiness pipeline for company: {company_id}")
        
        with Timer() as timer:
            # Load verification outputs
            verification_dir = os.path.join(outputs_dir, company_id, "verification")
            issues_path = os.path.join(verification_dir, "issues.json")
            summary_path = os.path.join(verification_dir, "comparison_summary.json")
            readiness_path = os.path.join(verification_dir, "readiness_summary.json")
            
            if not os.path.exists(issues_path) or not os.path.exists(summary_path) or not os.path.exists(readiness_path):
                raise FileNotFoundError(f"Verification outputs not found for company '{company_id}'. Please run verification first.")
                
            with open(issues_path, "r", encoding="utf-8") as f:
                issues_data = json.load(f)
                verification_issues = issues_data.get("issues", []) if isinstance(issues_data, dict) else issues_data
                
            with open(summary_path, "r", encoding="utf-8") as f:
                verification_summary = json.load(f)

            with open(readiness_path, "r", encoding="utf-8") as f:
                readiness_data = json.load(f)
                score = readiness_data.get("readiness_score", 0)
                status = readiness_data.get("overall_status", "NOT_READY")

            # 1. Build and save Report Context
            report_context = ReportContextBuilder.build_and_save_context(company_id, outputs_dir)

            # Ensure reconciliation checkpoints exist
            recon_checkpoints_path = os.path.join(verification_dir, "reconciliation_checkpoints.json")
            if not os.path.exists(recon_checkpoints_path):
                from app.verification.reconciliation import ReconciliationEngine
                ReconciliationEngine.run(company_id, outputs_dir)

            # 2. Deterministic Scoring (Stage 4 outputs)
            scoring = {
                "readiness_score": score,
                "overall_status": status,
                "critical_issues_count": readiness_data.get("verified_mismatches", 0),
                "warning_issues_count": readiness_data.get("unresolved_inconsistencies", 0),
                "company_name": report_context.get("company_name")
            }

            # 3. Call AI Pipeline
            ai_results, prompt_hashes, cache_hits, cache_misses, retry_counts = ReadinessAiOrchestrator.run_ai_pipeline(
                company_id=company_id,
                report_context=report_context,
                outputs_dir=outputs_dir,
                calculated_score=score,
                calculated_status=status
            )

            # 4. Assemble Report JSON Objects
            docs_reviewed = ReportAssembler.get_documents_reviewed(outputs_dir, company_id)
            reports = ReportAssembler.assemble_reports(
                company_id=company_id,
                verification_issues=verification_issues,
                documents_reviewed=docs_reviewed,
                stats=verification_summary,
                scoring_results=scoring,
                ai_narratives=ai_results
            )

            # Save Report JSONs
            readiness_dir = os.path.join(outputs_dir, company_id, "readiness")
            manifests_dir = os.path.join(outputs_dir, company_id, "manifests")
            os.makedirs(readiness_dir, exist_ok=True)
            os.makedirs(manifests_dir, exist_ok=True)
            
            report_hashes = {}
            from app.core import sha256_string
            import datetime
            now_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "") + "Z"
            metadata = {
                "schema_version": "1.0.0",
                "pipeline_version": "1.0.0",
                "created_by": "Duelens Reporting Engine",
                "generated_at": now_str
            }
            
            for name, data in reports.items():
                if isinstance(data, dict):
                    data["metadata"] = metadata
                filepath = os.path.join(readiness_dir, f"{name}.json")
                with open(filepath, "w", encoding="utf-8") as f:
                    content = json.dumps(data, indent=2)
                    f.write(content)
                    report_hashes[f"{name}.json"] = sha256_string(content)

            # 5. Generate Markdown Reports
            markdowns = MarkdownReportGenerator.generate_markdown(company_id, reports)
            for name, md_content in markdowns.items():
                filepath = os.path.join(readiness_dir, name)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(md_content)

            # 6. Generate PDFs
            PdfReportAssembler.generate_all_pdfs(company_id, reports, readiness_dir)

            # 7. Write Prompt Manifest
            from app.core.version import PROMPT_VERSION
            from app.core.manifest import get_utc_now_iso
            prompt_manifest = {
                "prompts": {name: {"hash": p_hash, "version": PROMPT_VERSION} for name, p_hash in prompt_hashes.items()},
                "model": os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
                "temperature": 0.1,
                "generated_at": get_utc_now_iso()
            }
            with open(os.path.join(manifests_dir, "prompt_manifest.json"), "w", encoding="utf-8") as f:
                json.dump(prompt_manifest, f, indent=2)

            # Fetch Registry Version
            from app.extractors.specification_registry import SpecificationRegistry
            registry_version = SpecificationRegistry.get_version() or "unknown"

            # 8. Write Readiness Manifest
            from app.core.version import READINESS_VERSION, PIPELINE_VERSION
            manifest = {
                "schema_version": "1.0",
                "pipeline_version": PIPELINE_VERSION,
                "comparison_version": "1.0",
                "registry_version": registry_version,
                "prompt_version": PROMPT_VERSION,
                "prompt_hashes": prompt_hashes,
                "model": os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
                "temperature": 0.1,
                "cache_hits": cache_hits,
                "cache_misses": cache_misses,
                "processing_times": {
                    "total_time_ms": timer.elapsed_ms
                },
                "report_hashes": report_hashes,
                "generated_files": [
                    "readiness_summary.json", "readiness_summary.md", "readiness_summary.pdf",
                    "executive_summary.json", "executive_summary.md", "executive_summary.pdf",
                    "follow_up_questions.json", "follow_up_questions.md", "follow_up_questions.pdf",
                    "inconsistency_report.json", "inconsistency_report.md"
                ],
                "retry_counts": retry_counts,
                "validation_status": "PASS",
                "pdf_generation_status": "PASS",
                "markdown_generation_status": "PASS"
            }
            
            with open(os.path.join(manifests_dir, "readiness_manifest.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

        DuelensLogger.log("Readiness", "END", f"Successfully completed readiness pipeline in {timer.elapsed_ms}ms")

        return {
            "company_id": company_id,
            "readiness_status": status,
            "readiness_score": score,
            "reports_generated": len(manifest["generated_files"]),
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "critical_issues": scoring["critical_issues_count"],
            "warnings": scoring["warning_issues_count"],
            "processing_time_ms": timer.elapsed_ms,
            "validation_status": "PASS"
        }
