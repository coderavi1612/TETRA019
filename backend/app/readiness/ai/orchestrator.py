import os
import json
import hashlib
import concurrent.futures
from typing import Dict, Any, List, Tuple, Optional
from pydantic import BaseModel

from app.readiness.prompt_builder import PromptBuilder
from app.readiness.ai.retry import ReadinessRetryPipeline
from app.readiness.schemas.readiness import ExecutiveSummary
from app.core.logging import DuelensLogger

class ReadinessAiOrchestrator:
    @staticmethod
    def get_cache_path(company_id: str, outputs_dir: str, category: str, key_hash: str) -> str:
        new_path = os.path.join(outputs_dir, company_id, "cache", "readiness", category, f"{key_hash}.json")
        if not os.path.exists(new_path):
            legacy_path = os.path.join(outputs_dir, company_id, "reports", "cache", category, f"{key_hash}.json")
            if os.path.exists(legacy_path):
                return legacy_path
        return new_path

    @staticmethod
    def check_cache(cache_file: str) -> Optional[Dict[str, Any]]:
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    @staticmethod
    def save_cache(cache_file: str, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def run_ai_pipeline(
        cls,
        company_id: str,
        report_context: Dict[str, Any],
        outputs_dir: str,
        calculated_score: int,
        calculated_status: str
    ) -> Tuple[Dict[str, Any], Dict[str, str], int, int, Dict[str, int]]:
        """
        Runs the 4-stage AI pipeline, checking cache and performing retries.
        Execution strategy is configurable via AI_EXECUTION_MODE environment setting.
        """
        execution_mode = os.getenv("AI_EXECUTION_MODE", "CONCURRENT")
        DuelensLogger.log("Readiness", "AI_START", f"Starting readiness AI orchestration mode={execution_mode}")

        cache_hits = 0
        cache_misses = 0
        retry_counts = {"impact": 0, "questions": 0, "executive": 0, "narrative": 0}
        prompt_hashes = {}

        inconsistency_narratives = {}
        questions_narratives = {}
        executive_narrative = {}
        narrative_summary = {}

        # Define individual processing callables
        def process_impact(issue):
            issue_id = issue["issue_id"]
            classification = issue["classification"]
            rec_action_type = "Reconcile values"
            if classification == "Missing Information":
                rec_action_type = "Provide missing document/metrics"
            elif classification == "Unresolved Inconsistency":
                rec_action_type = "Clarify authoritative values"

            issue_str = json.dumps(issue, sort_keys=True)
            issue_hash = hashlib.sha256(issue_str.encode("utf-8")).hexdigest()
            cache_file = cls.get_cache_path(company_id, outputs_dir, "impact", issue_hash)
            
            cached = cls.check_cache(cache_file)
            if cached:
                return "cache_hit", issue_id, cached, None, 0
                
            def build_impact_prompt(feedback: str) -> str:
                prompt, p_hash, _ = PromptBuilder.build_prompt("impact", {
                    "canonical_field": issue.get("field", ""),
                    "classification": classification,
                    "severity": issue.get("severity", ""),
                    "documents": ", ".join(issue.get("documents", [])),
                    "authoritative_document": "N/A",
                    "authoritative_value": "N/A",
                    "description": issue.get("description", ""),
                    "recommended_action_type": rec_action_type
                })
                return prompt, p_hash

            prompt_hash_val = [None]
            def prompt_func(feedback: str) -> str:
                p, ph = build_impact_prompt(feedback)
                prompt_hash_val[0] = ph
                return p
                
            class ImpactSchema(BaseModel):
                business_impact: str
                recommended_action: str

            validated_impact, retries = ReadinessRetryPipeline.execute_with_retry(
                "impact", prompt_func, ImpactSchema
            )
            impact_dict = validated_impact.model_dump()
            cls.save_cache(cache_file, impact_dict)
            return "cache_miss", issue_id, impact_dict, prompt_hash_val[0], retries

        def process_question(issue):
            issue_id = issue["issue_id"]
            issue_str = json.dumps(issue, sort_keys=True)
            issue_hash = hashlib.sha256(issue_str.encode("utf-8")).hexdigest()
            cache_file = cls.get_cache_path(company_id, outputs_dir, "questions", issue_hash)
            
            cached = cls.check_cache(cache_file)
            if cached:
                return "cache_hit", issue_id, cached, None, 0
                
            def build_questions_prompt(feedback: str) -> str:
                prompt, p_hash, _ = PromptBuilder.build_prompt("questions", {
                    "canonical_field": issue.get("field", ""),
                    "classification": issue.get("classification", ""),
                    "severity": issue.get("severity", ""),
                    "documents": ", ".join(issue.get("documents", [])),
                    "description": issue.get("description", "")
                })
                return prompt, p_hash

            prompt_hash_val = [None]
            def prompt_func(feedback: str) -> str:
                p, ph = build_questions_prompt(feedback)
                prompt_hash_val[0] = ph
                return p

            class QuestionSchema(BaseModel):
                question: str
                why_it_matters: str
                required_document: str
                expected_answer: str

            validated_question, retries = ReadinessRetryPipeline.execute_with_retry(
                "questions", prompt_func, QuestionSchema
            )
            question_dict = validated_question.model_dump()
            cls.save_cache(cache_file, question_dict)
            return "cache_miss", issue_id, question_dict, prompt_hash_val[0], retries

        def process_executive():
            context_str = json.dumps(report_context, sort_keys=True)
            context_hash = hashlib.sha256(context_str.encode("utf-8")).hexdigest()
            cache_file_exec = cls.get_cache_path(company_id, outputs_dir, "executive", context_hash)
            
            cached_exec = cls.check_cache(cache_file_exec)
            if cached_exec:
                return "cache_hit", cached_exec, None, 0
                
            def build_exec_prompt(feedback: str) -> str:
                prompt, p_hash, _ = PromptBuilder.build_prompt("executive", {
                    "report_context": json.dumps(report_context, indent=2),
                    "readiness_score": calculated_score,
                    "readiness_status": calculated_status
                })
                return prompt, p_hash

            prompt_hash_val = [None]
            def prompt_func(feedback: str) -> str:
                p, ph = build_exec_prompt(feedback)
                prompt_hash_val[0] = ph
                return p

            validated_exec, retries = ReadinessRetryPipeline.execute_with_retry(
                "executive", prompt_func, ExecutiveSummary
            )
            exec_dict = validated_exec.model_dump()
            cls.save_cache(cache_file_exec, exec_dict)
            return "cache_miss", exec_dict, prompt_hash_val[0], retries

        def process_narrative():
            context_str = json.dumps(report_context, sort_keys=True)
            context_hash = hashlib.sha256(context_str.encode("utf-8")).hexdigest()
            cache_file_narr = cls.get_cache_path(company_id, outputs_dir, "narrative", context_hash)
            
            cached_narr = cls.check_cache(cache_file_narr)
            if cached_narr:
                return "cache_hit", cached_narr, None, 0
                
            def build_narrative_prompt(feedback: str) -> str:
                prompt, p_hash, _ = PromptBuilder.build_prompt("narrative", {
                    "report_context": json.dumps(report_context, indent=2),
                    "readiness_score": calculated_score,
                    "readiness_status": calculated_status
                })
                return prompt, p_hash

            prompt_hash_val = [None]
            def prompt_func(feedback: str) -> str:
                p, ph = build_narrative_prompt(feedback)
                prompt_hash_val[0] = ph
                return p

            class NarrativeSchema(BaseModel):
                strengths: List[str]
                risks: List[str]
                next_steps: List[str]
                executive_summary: str

            validated_narrative, retries = ReadinessRetryPipeline.execute_with_retry(
                "narrative", prompt_func, NarrativeSchema
            )
            narr_dict = validated_narrative.model_dump()
            cls.save_cache(cache_file_narr, narr_dict)
            return "cache_miss", narr_dict, prompt_hash_val[0], retries

        # Execute tasks according to Strategy (Sequential vs Concurrent)
        issues = report_context.get("issues_summary", [])
        
        impact_results = []
        question_results = []
        exec_result = None
        narr_result = None

        if execution_mode == "CONCURRENT":
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit tasks
                impact_futures = [executor.submit(process_impact, issue) for issue in issues]
                question_futures = [executor.submit(process_question, issue) for issue in issues]
                exec_future = executor.submit(process_executive)
                narr_future = executor.submit(process_narrative)

                # Gather results
                impact_results = [f.result() for f in impact_futures]
                question_results = [f.result() for f in question_futures]
                exec_result = exec_future.result()
                narr_result = narr_future.result()
        else: # SEQUENTIAL
            impact_results = [process_impact(issue) for issue in issues]
            question_results = [process_question(issue) for issue in issues]
            exec_result = process_executive()
            narr_result = process_narrative()

        # Parse and aggregate impact results
        for item in impact_results:
            hit_or_miss, issue_id, data, p_hash, retries = item
            if hit_or_miss == "cache_hit":
                cache_hits += 1
            else:
                cache_misses += 1
                if p_hash:
                    prompt_hashes["impact"] = p_hash
                retry_counts["impact"] += retries
            inconsistency_narratives[issue_id] = data

        # Parse and aggregate question results
        for item in question_results:
            hit_or_miss, issue_id, data, p_hash, retries = item
            if hit_or_miss == "cache_hit":
                cache_hits += 1
            else:
                cache_misses += 1
                if p_hash:
                    prompt_hashes["questions"] = p_hash
                retry_counts["questions"] += retries
            questions_narratives[issue_id] = data

        # Parse and aggregate executive summary results
        exec_hit_or_miss, exec_data, exec_p_hash, exec_retries = exec_result
        if exec_hit_or_miss == "cache_hit":
            cache_hits += 1
        else:
            cache_misses += 1
            if exec_p_hash:
                prompt_hashes["executive"] = exec_p_hash
            retry_counts["executive"] += exec_retries
        executive_narrative = exec_data

        # Parse and aggregate narrative results
        narr_hit_or_miss, narr_data, narr_p_hash, narr_retries = narr_result
        if narr_hit_or_miss == "cache_hit":
            cache_hits += 1
        else:
            cache_misses += 1
            if narr_p_hash:
                prompt_hashes["narrative"] = narr_p_hash
            retry_counts["narrative"] += narr_retries
        narrative_summary = narr_data

        results = {
            "inconsistency_narratives": inconsistency_narratives,
            "questions_narratives": questions_narratives,
            "executive_narrative": executive_narrative,
            "narrative_summary": narrative_summary
        }
        
        DuelensLogger.log("Readiness", "AI_END", f"Completed readiness AI orchestration cache_hits={cache_hits} cache_misses={cache_misses}")
        return results, prompt_hashes, cache_hits, cache_misses, retry_counts
