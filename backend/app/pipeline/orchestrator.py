import os
import json
import time
from enum import Enum
from typing import Dict, Any, List

from app.core.logging import DuelensLogger
from app.core.timing import Timer
from app.core.version import PIPELINE_VERSION
from app.core.manifest import get_utc_now_iso
from app.config import settings

from app.parsers.orchestrator import DocumentParserOrchestrator
from app.extractors.extractor import FactExtractor
from app.verification.orchestrator import VerificationOrchestrator
from app.readiness.orchestrator import ReadinessOrchestrator

class PipelineStage(str, Enum):
    PARSE = "PARSE"
    EXTRACT = "EXTRACT"
    REASON = "REASON"
    VERIFY = "VERIFY"
    READINESS = "READINESS"
    FULL = "FULL"

class DuelensPipeline:
    @staticmethod
    def generate_artifacts_manifest(company_id: str) -> None:
        """
        Scans outputs directory for all available reports and artifacts, 
        and writes artifacts_manifest.json inside manifests/ folder.
        """
        company_dir = os.path.join(settings.OUTPUT_DIR, company_id)
        manifests_dir = os.path.join(company_dir, "manifests")
        os.makedirs(manifests_dir, exist_ok=True)
        
        categories = ["parsed", "extracted", "verification", "readiness", "manifests", "logs"]
        artifacts = []
        
        category_to_stage = {
            "parsed": "parse",
            "extracted": "extract",
            "verification": "verify",
            "readiness": "readiness",
            "manifests": "system",
            "logs": "system"
        }
        
        extension_to_mime = {
            ".json": "application/json",
            ".pdf": "application/pdf",
            ".md": "text/markdown",
            ".txt": "text/plain",
            ".log": "text/plain"
        }
        
        for cat in categories:
            cat_dir = os.path.join(company_dir, cat)
            if os.path.exists(cat_dir) and os.path.isdir(cat_dir):
                for filename in os.listdir(cat_dir):
                    file_path = os.path.join(cat_dir, filename)
                    if os.path.isfile(file_path):
                        # Avoid manifest recursive list
                        if filename == "artifacts_manifest.json":
                            continue
                            
                        stat_info = os.stat(file_path)
                        ext = os.path.splitext(filename)[1].lower()
                        mime = extension_to_mime.get(ext, "application/octet-stream")
                        mtime = stat_info.st_mtime
                        generated_at_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime))
                        
                        artifacts.append({
                            "name": filename,
                            "category": cat,
                            "mime_type": mime,
                            "size": stat_info.st_size,
                            "download_url": f"/api/v1/files/{company_id}/{cat}/{filename}",
                            "generated_at": generated_at_iso,
                            "stage": category_to_stage.get(cat, "system")
                        })
                        
        manifest_data = {
            "manifest_version": "1.0",
            "pipeline_version": PIPELINE_VERSION,
            "generated_at": get_utc_now_iso(),
            "company_id": company_id,
            "artifacts": artifacts
        }
        
        manifest_path = os.path.join(manifests_dir, "artifacts_manifest.json")
        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2)
        except Exception:
            pass

    @classmethod
    def run(
        cls, 
        company_id: str, 
        stage: PipelineStage = PipelineStage.FULL,
        job_id: str = None
    ) -> Dict[str, Any]:
        """
        Coordinates the complete, multi-stage E2E Duelens document ingestion, extraction, 
        verification, and readiness evaluation pipeline. Supports status updates via job_id.
        """
        from app.pipeline.job_manager import JobManager, JobStatus
        from app.pipeline.status_manager import PipelineStatusManager

        clean_company_id = company_id.strip()
        DuelensLogger.log("Pipeline", "START", f"Starting Duelens pipeline stage={stage} for company={clean_company_id} job_id={job_id}")
        
        if job_id:
            JobManager.update_job_status(job_id, JobStatus.RUNNING)
            PipelineStatusManager.update_stage(job_id, "parse", "idle", overall_status="RUNNING")

        stages_to_run: List[PipelineStage] = []
        if stage == PipelineStage.PARSE:
            stages_to_run = [PipelineStage.PARSE]
        elif stage == PipelineStage.EXTRACT:
            stages_to_run = [PipelineStage.PARSE, PipelineStage.EXTRACT]
        elif stage == PipelineStage.REASON:
            stages_to_run = [PipelineStage.PARSE, PipelineStage.EXTRACT, PipelineStage.REASON]
        elif stage == PipelineStage.VERIFY:
            stages_to_run = [PipelineStage.PARSE, PipelineStage.EXTRACT, PipelineStage.REASON, PipelineStage.VERIFY]
        else: # READINESS or FULL
            stages_to_run = [PipelineStage.PARSE, PipelineStage.EXTRACT, PipelineStage.REASON, PipelineStage.VERIFY, PipelineStage.READINESS]

        results = {}
        errors = []
        warnings = []
        
        with Timer() as pipeline_timer:
            for s in stages_to_run:
                stage_name = s.value.lower()
                if job_id:
                    PipelineStatusManager.update_stage(job_id, stage_name, "running")
                    PipelineStatusManager.persist_status(job_id, clean_company_id)

                with Timer() as stage_timer:
                    try:
                        DuelensLogger.log("Pipeline", "STAGE_START", f"Running stage: {s}")
                        if s == PipelineStage.PARSE:
                            res = DocumentParserOrchestrator.run_parse(clean_company_id)
                            results["parse"] = res
                        elif s == PipelineStage.EXTRACT:
                            _, stats = FactExtractor.extract_company_facts(clean_company_id)
                            results["extract"] = stats
                        elif s == PipelineStage.REASON:
                            from app.reasoning.orchestrator import ReasoningOrchestrator
                            res = ReasoningOrchestrator.run_reasoning(clean_company_id)
                            results["reason"] = res
                        elif s == PipelineStage.VERIFY:
                            res = VerificationOrchestrator.run_verification(clean_company_id)
                            results["verify"] = res
                        elif s == PipelineStage.READINESS:
                            res = ReadinessOrchestrator.run_readiness_pipeline(clean_company_id)
                            results["readiness"] = res
                        
                        DuelensLogger.log("Pipeline", "STAGE_END", f"Successfully completed stage: {s}")
                        
                        if job_id:
                            PipelineStatusManager.update_stage(job_id, stage_name, "completed", duration_ms=stage_timer.elapsed_ms)
                            PipelineStatusManager.persist_status(job_id, clean_company_id)

                    except Exception as e:
                        err_msg = f"Pipeline failed at stage {s}: {str(e)}"
                        DuelensLogger.log("Pipeline", "ERROR", err_msg, error=e)
                        errors.append(err_msg)
                        
                        if job_id:
                            PipelineStatusManager.update_stage(
                                job_id, 
                                stage_name, 
                                "failed", 
                                duration_ms=stage_timer.elapsed_ms,
                                error_msg=str(e)
                            )
                            PipelineStatusManager.persist_status(job_id, clean_company_id)
                            JobManager.update_job_status(job_id, JobStatus.FAILED)
                        break  # Stop execution of subsequent stages upon failure

        # Always generate artifacts manifest at completion of full runs or success
        if not errors:
            cls.generate_artifacts_manifest(clean_company_id)
            if job_id:
                JobManager.update_job_status(job_id, JobStatus.COMPLETED)
                PipelineStatusManager.update_stage(job_id, "readiness", "completed", overall_status="COMPLETED")
                PipelineStatusManager.persist_status(job_id, clean_company_id)

        DuelensLogger.log("Pipeline", "END", f"Completed Duelens pipeline in {pipeline_timer.elapsed_ms}ms")
        
        return {
            "company_id": clean_company_id,
            "target_stage": stage,
            "executed_stages": [s.value for s in stages_to_run[:len(results)]],
            "results": results,
            "errors": errors,
            "warnings": warnings,
            "processing_time_ms": pipeline_timer.elapsed_ms
        }
