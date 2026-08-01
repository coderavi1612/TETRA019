import logging
from typing import Type, Any, Dict, Callable, Tuple
from pydantic import BaseModel
from app.readiness.ai.gemini import GeminiReadinessCaller
from app.readiness.ai.repair import JSONReadinessRepairer
from app.readiness.ai.validator import JSONSchemaValidator

logger = logging.getLogger(__name__)

class ReadinessRetryPipeline:
    @staticmethod
    def execute_with_retry(
        prompt_name: str,
        prompt_func: Callable[[str], str],
        schema_model: Type[BaseModel]
    ) -> Tuple[BaseModel, int]:
        """
        Executes a Gemini call with schema-validation checking and a single feedback-retry loop.
        Returns a tuple of (validated_model_instance, retry_count).
        """
        prompt_text = prompt_func("")
        
        # Attempt 1
        raw_text = GeminiReadinessCaller.call_gemini(prompt_text, prompt_name)
        try:
            parsed_data = JSONReadinessRepairer.repair_json(raw_text)
            validated = JSONSchemaValidator.validate_schema(parsed_data, schema_model)
            return validated, 0
        except Exception as e:
            logger.warning(f"First attempt failed validation for prompt '{prompt_name}': {str(e)}")
            
        # Attempt 2: Retry with validation error feedback
        feedback = f"\n\nCRITICAL ERROR: Your previous response was invalid. Details: {str(e)}. Please correct the JSON schema format."
        retry_prompt_text = prompt_func(feedback)
        
        raw_text_retry = GeminiReadinessCaller.call_gemini(retry_prompt_text, prompt_name)
        try:
            parsed_data_retry = JSONReadinessRepairer.repair_json(raw_text_retry)
            validated_retry = JSONSchemaValidator.validate_schema(parsed_data_retry, schema_model)
            return validated_retry, 1
        except Exception as e_retry:
            logger.error(f"Second attempt failed validation for prompt '{prompt_name}': {str(e_retry)}")
            raise ValueError(f"Prompt '{prompt_name}' failed validation after retry: {str(e_retry)}")
