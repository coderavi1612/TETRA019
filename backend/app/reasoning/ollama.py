import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.reasoning.client import BaseReasoningClient

logger = logging.getLogger(__name__)

# Pydantic schemas for Ollama Qwen3 output validation
class SemanticConflict(BaseModel):
    field: str
    concern: str

class OwnershipConflict(BaseModel):
    shareholder: str
    concern: str

class TimelineConflict(BaseModel):
    milestone: str
    concern: str

class MissingInfo(BaseModel):
    field: str
    notes: str

class ReportMetadata(BaseModel):
    schema_version: str = "1.0.0"
    pipeline_version: str = "1.0.0"
    created_by: str = "Duelens Reasoning Engine"
    generated_at: str = "2026-08-01T12:00:00Z"

class ComparisonReport(BaseModel):
    metadata: Optional[ReportMetadata] = None
    status: str = "COMPLETED" # COMPLETED or FAILED
    reasoning_available: bool = True
    semantic_conflicts: List[SemanticConflict] = Field(default_factory=list)
    ownership_conflicts: List[OwnershipConflict] = Field(default_factory=list)
    timeline_conflicts: List[TimelineConflict] = Field(default_factory=list)
    missing_information: List[MissingInfo] = Field(default_factory=list)
    investor_questions: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    business_risks: List[str] = Field(default_factory=list)

class OllamaReasoningClient(BaseReasoningClient):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "qwen3:8b")

    def generate_reasoning(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queries local Ollama reasoning model with aligned comparison context.
        Validates output using Pydantic. If Ollama is offline or returns error,
        it yields a failed report payload rather than fabricating mock reasoning.
        """
        import datetime
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "") + "Z"
        report_meta = ReportMetadata(generated_at=now_str)

        system_prompt = (
            "You are a Senior Investment Analyst at a top-tier Venture Capital fund.\n"
            "Your task is to analyze the following cross-document comparison context and identify "
            "semantic contradictions, narrative inconsistencies, risks, and missing information.\n\n"
            "Do NOT perform mathematical validation or calculate scores. Focus on semantic explanations, "
            "business impact, and recommendations.\n\n"
            "Provide your response strictly in JSON matching this schema:\n"
            "{\n"
            "  \"semantic_conflicts\": [{\"field\": \"field_name\", \"concern\": \"desc\"}],\n"
            "  \"ownership_conflicts\": [{\"shareholder\": \"founder_name\", \"concern\": \"desc\"}],\n"
            "  \"timeline_conflicts\": [{\"milestone\": \"milestone_name\", \"concern\": \"desc\"}],\n"
            "  \"missing_information\": [{\"field\": \"field_name\", \"notes\": \"desc\"}],\n"
            "  \"investor_questions\": [\"string\"],\n"
            "  \"recommendations\": [\"string\"],\n"
            "  \"business_risks\": [\"string\"]\n"
            "}"
        )

        user_content = f"Here is the aligned comparison context JSON:\n{json.dumps(context_data, indent=2)}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "options": {
                "temperature": 0.1
            },
            "stream": False,
            "format": "json"
        }

        try:
            logger.info(f"Connecting to Ollama model={self.model} at url={self.base_url}")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30.0
            )
            if response.status_code == 200:
                result_json = response.json()
                message_content = result_json.get("message", {}).get("content", "")
                parsed_content = json.loads(message_content)
                
                # Pydantic Validation Layer
                validated_report = ComparisonReport(**parsed_content)
                validated_report.metadata = report_meta
                logger.info("Ollama reasoning output successfully generated and validated.")
                return validated_report.model_dump()
            else:
                logger.warning(f"Ollama returned HTTP error code: {response.status_code}. Using failed report fallback.")
        except Exception as e:
            logger.warning(f"Ollama server connection failed ({str(e)}). Returning reasoning unavailable report.")

        # Fail stage and continue with a valid Pydantic envelope marked reasoning_available = False
        report = ComparisonReport(
            metadata=report_meta,
            status="FAILED",
            reasoning_available=False
        )
        return report.model_dump()


