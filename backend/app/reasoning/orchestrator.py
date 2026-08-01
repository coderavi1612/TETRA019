import os
import json
import logging
import hashlib
from typing import Dict, Any

from app.config import settings
from app.verification.context.builder import ComparisonContextBuilder
from app.reasoning.ollama import OllamaReasoningClient

logger = logging.getLogger(__name__)

class ReasoningOrchestrator:
    @staticmethod
    def run_reasoning(company_id: str, outputs_dir: str = None) -> Dict[str, Any]:
        """
        Coordinates E2E local model consistency reasoning (Stage 3):
        - Builds comparison_context.json (Stage 2.5).
        - Generates hash check of the context to check cache boundaries.
        - Invokes the abstract reasoning client (Ollama).
        - Saves comparison_report.json.
        """
        if outputs_dir is None:
            outputs_dir = settings.OUTPUT_DIR
            
        company_output_dir = os.path.join(outputs_dir, company_id)
        os.makedirs(company_output_dir, exist_ok=True)
        
        reasoning_dir = os.path.join(company_output_dir, "reasoning")
        os.makedirs(reasoning_dir, exist_ok=True)

        # 1. Trigger Comparison Context Builder (Stage 2.5)
        context_data = ComparisonContextBuilder.build_context(company_id)
        
        # 2. Check Cache boundary
        context_str = json.dumps(context_data, sort_keys=True)
        context_hash = hashlib.sha256(context_str.encode("utf-8")).hexdigest()
        
        report_output_path = os.path.join(reasoning_dir, "comparison_report.json")
        cache_manifest_path = os.path.join(company_output_dir, "manifests", "reasoning_cache.json")
        os.makedirs(os.path.join(company_output_dir, "manifests"), exist_ok=True)
        
        is_cache_valid = False
        if os.path.exists(report_output_path) and os.path.exists(cache_manifest_path):
            try:
                with open(cache_manifest_path, "r", encoding="utf-8") as f:
                    cache_manifest = json.load(f)
                if cache_manifest.get("context_hash") == context_hash:
                    is_cache_valid = True
                    logger.info(f"[Reasoning][{company_id}] Cache Hit. Loading cached comparison report.")
            except Exception:
                pass
                
        if is_cache_valid:
            try:
                with open(report_output_path, "r", encoding="utf-8") as f:
                    report_data = json.load(f)
                return {
                    "company_id": company_id,
                    "status": "completed",
                    "cache_hit": True,
                    "report": report_data
                }
            except Exception:
                pass

        # 3. Call Reasoning Client (Ollama or Gemini)
        provider = os.getenv("REASONING_PROVIDER", "local").strip().lower()
        if provider == "gemini":
            from app.reasoning.gemini import GeminiReasoningClient
            client = GeminiReasoningClient()
            logger.info(f"[Reasoning][{company_id}] Cache Miss. Running Gemini reasoning model={client.model}...")
        else:
            from app.reasoning.ollama import OllamaReasoningClient
            client = OllamaReasoningClient()
            logger.info(f"[Reasoning][{company_id}] Cache Miss. Running local reasoning model={client.model}...")
        
        report_data = client.generate_reasoning(context_data)
        
        # 4. Save output and write cache manifest
        with open(report_output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
            
        try:
            with open(cache_manifest_path, "w", encoding="utf-8") as f:
                json.dump({
                    "context_hash": context_hash,
                    "model": client.model,
                    "generated_at": os.getenv("CURRENT_TIME", "2026-08-01T12:00:00Z")
                }, f, indent=2)
        except Exception:
            pass

        return {
            "company_id": company_id,
            "status": "completed",
            "cache_hit": False,
            "report": report_data
        }
