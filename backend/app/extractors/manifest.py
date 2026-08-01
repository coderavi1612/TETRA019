import json
from datetime import datetime, timezone
from typing import Dict, List, Any

class ExtractionManifestBuilder:
    def __init__(self, company_id: str, registry_version: str, template_version: str, prompt_version: str, model_name: str):
        self.company_id = company_id
        self.registry_version = registry_version
        self.template_version = template_version
        self.prompt_version = prompt_version
        self.model_name = model_name
        self.documents: List[Dict[str, Any]] = []
        self.failures: List[Dict[str, Any]] = []
        
        # Cache stats trackers
        self.chunks_processed = 0
        self.chunks_reused = 0
        self.gemini_calls = 0
        self.gemini_calls_saved = 0

    def add_document(
        self, 
        document_type: str, 
        status: str, 
        chunks: int, 
        cache_hits: int, 
        cache_misses: int, 
        processing_time_ms: int,
        fields_extracted: int, 
        fields_missing: int, 
        validation: str
    ) -> None:
        self.documents.append({
            "document_type": document_type,
            "status": status,
            "chunks": chunks,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "processing_time_ms": processing_time_ms,
            "fields_extracted": fields_extracted,
            "fields_missing": fields_missing,
            "validation": validation
        })
        self.chunks_processed += chunks
        self.chunks_reused += cache_hits
        self.gemini_calls += cache_misses
        self.gemini_calls_saved += cache_hits

    def add_failure(self, document_type: str, reason: str, retry_count: int, failed_stage: str) -> None:
        self.failures.append({
            "document_type": document_type,
            "reason": reason,
            "retry_count": retry_count,
            "failed_stage": failed_stage
        })

    def record_retry_call(self) -> None:
        self.gemini_calls += 1

    def build(self, performance_timings: Dict[str, int], gemini_config: Dict[str, Any] = None) -> Dict[str, Any]:
        total_chunks = self.chunks_processed
        efficiency = 0.0
        if total_chunks > 0:
            efficiency = (self.chunks_reused / total_chunks) * 100.0
            
        default_config = {
            "model": self.model_name,
            "temperature": 0.1,
            "top_p": None,
            "max_output_tokens": None,
            "structured_output_enabled": True,
            "response_schema_enabled": True
        }
        if gemini_config:
            default_config.update(gemini_config)

        manifest = {
            "company_id": self.company_id,
            "pipeline_version": "1.0",
            "model": self.model_name,
            "registry_version": self.registry_version,
            "template_version": self.template_version,
            "prompt_version": self.prompt_version,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "documents": self.documents,
            "cache_analytics": {
                "chunks_processed": self.chunks_processed,
                "chunks_reused": self.chunks_reused,
                "gemini_calls": self.gemini_calls,
                "gemini_calls_saved": self.gemini_calls_saved,
                "cache_efficiency": round(efficiency, 2)
            },
            "gemini_configuration": default_config,
            "performance_metrics": performance_timings,
            "failures": self.failures
        }
        return manifest
