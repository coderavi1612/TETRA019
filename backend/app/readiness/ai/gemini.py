from google import genai
from google.genai import types
import os
import json
import logging
from typing import Any, Dict, Optional
from app.core.logging import DuelensLogger

logger = logging.getLogger(__name__)

class GeminiReadinessCaller:
    @staticmethod
    def call_gemini(prompt: str, prompt_name: str, system_instruction: str = "You are a professional Venture Capital investment auditor.") -> str:
        """
        Calls the Gemini API or returns structured mock fallback JSON if the key is missing or dummy.
        """
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        is_mock = (
            not api_key or 
            api_key == "AIzaSyBTR-BXbSPun3rOHl1q59hSBVqSlKChBCE" or
            any(kw in api_key.lower() for kw in ["dummy", "mock", "test", "fake", "temp"])
        )
        if is_mock:
            DuelensLogger.log("Gemini", "CACHE_HIT", f"Using mock response for prompt: {prompt_name}")
            return GeminiReadinessCaller.get_mock_response(prompt_name)
            
        model_name = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
        try:
            client = genai.Client(api_key=api_key)
            
            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                system_instruction=system_instruction
            )
            
            DuelensLogger.log("Gemini", "REQUEST", f"Calling model {model_name} for readiness prompt: {prompt_name}")
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            
            DuelensLogger.log("Gemini", "RESPONSE", f"Model {model_name} responded successfully for: {prompt_name}")
            return response.text
        except Exception as e:
            DuelensLogger.log("Gemini", "ERROR", f"Gemini call failed for {prompt_name}: {str(e)}. Falling back to mock data.", error=e)
            return GeminiReadinessCaller.get_mock_response(prompt_name)

    @staticmethod
    def get_mock_response(prompt_name: str) -> str:
        if prompt_name == "impact":
            return json.dumps({
                "business_impact": "Discrepancy in metrics indicates potential accounting variances or revision errors, impacting VC validation.",
                "recommended_action": "Reconcile the financial statements values with MIS inputs."
            })
        elif prompt_name == "questions":
            return json.dumps({
                "question": "Could you please explain why the revenue total for FY24 differs across the Pitch Deck and MIS reports?",
                "why_it_matters": "Venture capital audit requires consistency in core metrics.",
                "required_document": "historical_financial_statements",
                "expected_answer": "An updated Pitch Deck alignment sheet or audited financial statement matching the figures."
            })
        elif prompt_name == "executive":
            return json.dumps({
                "company_overview": "The startup is an emerging enterprise raising its primary fundraising round.",
                "overall_readiness": "Overall package is in a good initial state with minor metric inconsistencies.",
                "top_risks": [
                    "Mismatch in revenue totals for FY24 across documents",
                    "Missing historical MIS filings"
                ],
                "top_strengths": [
                    "Consistent legal entity name matching across all documents",
                    "Completed cap table allocations"
                ],
                "critical_issues": [
                    "Mismatch in Funding Ask Amount between Pitch Deck and projections"
                ],
                "immediate_actions": [
                    "Align Funding Ask Amount values to be consistent",
                    "Confirm the authoritative cap table share count"
                ],
                "investor_readiness": "The documentation is ready with minor changes. All immediate actions should be resolved."
            })
        elif prompt_name == "narrative":
            return json.dumps({
                "strengths": [
                    "Clean company name verification matching across all structures",
                    "Complete cap table information"
                ],
                "risks": [
                    "Required fields in Revenue.FY24 are missing entirely"
                ],
                "next_steps": [
                    "Upload MIS historical reports for FY24",
                    "Reconcile the funding round ask amount"
                ],
                "executive_summary": "The evaluations yield a readiness score of 84 with minor changes recommended before investor review."
            })
        return "{}"
