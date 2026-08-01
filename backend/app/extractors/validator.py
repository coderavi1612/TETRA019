from typing import List, Dict, Any, Callable
from pydantic import ValidationError

from app.schemas.fact import ExtractedFact
from app.extractors.repair import JSONRepairer

class FactValidator:
    @staticmethod
    def validate_facts(
        raw_response: str, 
        document_type: str, 
        retry_callback: Callable[[str], str] = None
    ) -> List[ExtractedFact]:
        """
        Parses raw Gemini responses, applies JSON repairs, and validates against the ExtractedFact schema.
        If validation errors are detected, it invokes retry_callback exactly once with corrective feedback.
        """
        # Parse and repair JSON from response
        repaired_dicts = JSONRepairer.repair_facts_list(raw_response, document_type)
        
        valid_facts = []
        validation_errors = []
        
        for idx, r_dict in enumerate(repaired_dicts):
            try:
                fact = ExtractedFact(**r_dict)
                valid_facts.append(fact)
            except ValidationError as ve:
                validation_errors.append(f"Index {idx} (block {r_dict.get('source_block_id')}): {str(ve)}")
        
        # Trigger single retry if validation failed and callback is provided
        if validation_errors and retry_callback:
            error_summary = "\n".join(validation_errors[:5]) # limit error text size
            retry_prompt_mod = (
                f"Your previous output failed Pydantic schema validation. Correct the errors below:\n"
                f"- confidence_reason MUST be strictly one of: 'Structured Table', 'Explicit Sentence', 'Heading', 'Bullet List', 'Repeated Across Blocks'.\n"
                f"- extraction_method MUST be strictly one of: 'text', 'table', 'heading', 'list'.\n"
                f"- status MUST be 'extracted'.\n"
                f"Pydantic Validation Errors:\n{error_summary}\n\n"
                f"Please correct the fields and output the valid JSON array."
            )
            try:
                new_raw_response = retry_callback(retry_prompt_mod)
                repaired_dicts_retry = JSONRepairer.repair_facts_list(new_raw_response, document_type)
                
                valid_facts_retry = []
                for r_dict in repaired_dicts_retry:
                    try:
                        fact = ExtractedFact(**r_dict)
                        valid_facts_retry.append(fact)
                    except ValidationError:
                        pass
                
                if valid_facts_retry:
                    return valid_facts_retry
            except Exception:
                # If retry fails, fallback to first-pass valid facts
                pass
                
        return valid_facts
