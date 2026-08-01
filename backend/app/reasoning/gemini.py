import os
import json
import logging
from typing import Dict, Any
from google import genai
from google.genai import types

from app.reasoning.client import BaseReasoningClient
from app.reasoning.ollama import ComparisonReport, ReportMetadata

logger = logging.getLogger(__name__)

class GeminiReasoningClient(BaseReasoningClient):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = os.getenv("REASONING_GEMINI_MODEL", "gemini-2.5-flash-lite")

    def generate_reasoning(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queries Gemini API for reasoning over aligned comparison context.
        Validates output using Pydantic.
        """
        import datetime
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "") + "Z"
        report_meta = ReportMetadata(generated_at=now_str)

        system_instruction = (
            "You are a Senior Investment Analyst at a top-tier Venture Capital fund.\n"
            "Your task is to analyze the following cross-document comparison context and identify "
            "semantic contradictions, narrative inconsistencies, risks, and missing information.\n\n"
            "Do NOT perform mathematical validation or calculate scores. Focus on semantic explanations, "
            "business impact, and recommendations.\n\n"
            "Provide your response strictly in JSON matching the requested structure."
        )

        user_content = f"Here is the aligned comparison context JSON:\n{json.dumps(context_data, indent=2)}"

        is_mock = (
            not self.api_key or 
            self.api_key == "AIzaSyBTR-BXbSPun3rOHl1q59hSBVqSlKChBCE" or
            any(kw in self.api_key.lower() for kw in ["dummy", "mock", "test", "fake", "temp"])
        )

        if is_mock:
            logger.info("Using fallback offline report since Gemini API key is dummy/missing.")
            report = ComparisonReport(
                metadata=report_meta,
                status="FAILED",
                reasoning_available=False
            )
            return report.model_dump()

        try:
            client = genai.Client(api_key=self.api_key)
            
            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                system_instruction=system_instruction,
                response_schema=ComparisonReport
            )
            
            logger.info(f"Connecting to Gemini reasoning client model={self.model}")
            
            response = client.models.generate_content(
                model=self.model,
                contents=user_content,
                config=config
            )
            
            logger.info("Gemini reasoning output successfully generated.")
            parsed_content = json.loads(response.text.strip())
            
            # Pydantic Validation Layer
            validated_report = ComparisonReport(**parsed_content)
            validated_report.metadata = report_meta
            return validated_report.model_dump()
            
        except Exception as e:
            logger.error(f"Gemini reasoning client call failed: {str(e)}")
            report = ComparisonReport(
                metadata=report_meta,
                status="FAILED",
                reasoning_available=False
            )
            return report.model_dump()
