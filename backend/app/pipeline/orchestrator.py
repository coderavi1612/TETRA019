from enum import Enum
from typing import Dict, Any, List

from app.core.logging import DuelensLogger
from app.core.timing import Timer
from app.parsers.orchestrator import DocumentParserOrchestrator
from app.extractors.extractor import FactExtractor
from app.verification.orchestrator import VerificationOrchestrator
from app.readiness.orchestrator import ReadinessOrchestrator

class PipelineStage(str, Enum):
    PARSE = "PARSE"
    EXTRACT = "EXTRACT"
    VERIFY = "VERIFY"
    READINESS = "READINESS"
    FULL = "FULL"

class DuelensPipeline:
    @staticmethod
    def run(company_id: str, stage: PipelineStage = PipelineStage.FULL) -> Dict[str, Any]:
        """
        Coordinates the complete, multi-stage E2E Duelens document ingestion, extraction, 
        verification, and readiness evaluation pipeline.
        """
        clean_company_id = company_id.strip()
        DuelensLogger.log("Pipeline", "START", f"Starting Duelens pipeline stage={stage} for company={clean_company_id}")
        
        stages_to_run: List[PipelineStage] = []
        if stage == PipelineStage.PARSE:
            stages_to_run = [PipelineStage.PARSE]
        elif stage == PipelineStage.EXTRACT:
            stages_to_run = [PipelineStage.PARSE, PipelineStage.EXTRACT]
        elif stage == PipelineStage.VERIFY:
            stages_to_run = [PipelineStage.PARSE, PipelineStage.EXTRACT, PipelineStage.VERIFY]
        else: # READINESS or FULL
            stages_to_run = [PipelineStage.PARSE, PipelineStage.EXTRACT, PipelineStage.VERIFY, PipelineStage.READINESS]

        results = {}
        errors = []
        warnings = []
        
        with Timer() as pipeline_timer:
            for s in stages_to_run:
                try:
                    DuelensLogger.log("Pipeline", "STAGE_START", f"Running stage: {s}")
                    if s == PipelineStage.PARSE:
                        res = DocumentParserOrchestrator.run_parse(clean_company_id)
                        results["parse"] = res
                    elif s == PipelineStage.EXTRACT:
                        _, stats = FactExtractor.extract_company_facts(clean_company_id)
                        results["extract"] = stats
                    elif s == PipelineStage.VERIFY:
                        res = VerificationOrchestrator.run_verification(clean_company_id)
                        results["verify"] = res
                    elif s == PipelineStage.READINESS:
                        res = ReadinessOrchestrator.run_readiness_pipeline(clean_company_id)
                        results["readiness"] = res
                    DuelensLogger.log("Pipeline", "STAGE_END", f"Successfully completed stage: {s}")
                except Exception as e:
                    err_msg = f"Pipeline failed at stage {s}: {str(e)}"
                    DuelensLogger.log("Pipeline", "ERROR", err_msg, error=e)
                    errors.append(err_msg)
                    break  # Stop execution of subsequent stages upon failure

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
