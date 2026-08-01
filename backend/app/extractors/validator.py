from typing import Dict, Any, Callable, List, Type
from pydantic import BaseModel, ValidationError
import logging

from app.schemas.registry import SCHEMA_REGISTRY
from app.extractors.repair import JSONRepairer

logger = logging.getLogger(__name__)

class FactValidator:
    @staticmethod
    def validate_document_json(
        raw_response: str, 
        document_type: str, 
        template_dict: Dict[str, Any],
        retry_callback: Callable[[str], str] = None
    ) -> Dict[str, Any]:
        """
        Runs the full validation pipeline:
        Gemini Output -> JSON Repair -> Schema Validation -> Key Validation -> Business Validation -> Accept
        If validation fails, retries Gemini ONCE using the retry_callback.
        """
        # Step 1 & 2: JSON Repair
        repaired_dict = JSONRepairer.repair_json_data(raw_response, template_dict)
        
        # Perform all validation stages
        validation_errors = FactValidator.perform_validation(repaired_dict, document_type, template_dict)
        
        if not validation_errors:
            logger.info(f"Validation successful for document type: {document_type}")
            return repaired_dict
            
        logger.warning(f"Validation failed for document type: {document_type}. Errors found:\n" + "\n".join(validation_errors[:3]))
        
        # If failure, retry Gemini exactly ONCE
        if retry_callback:
            error_summary = "\n".join(validation_errors[:5])
            retry_prompt = (
                f"Your previous output failed validation. Correct the errors below:\n"
                f"Validation Errors:\n{error_summary}\n\n"
                f"Please output the corrected valid JSON structure matching the template exactly."
            )
            try:
                logger.info("Retrying Gemini extraction...")
                new_raw_response = retry_callback(retry_prompt)
                new_repaired_dict = JSONRepairer.repair_json_data(new_raw_response, template_dict)
                
                # Re-validate
                retry_errors = FactValidator.perform_validation(new_repaired_dict, document_type, template_dict)
                if not retry_errors:
                    logger.info("Retry validation successful.")
                    return new_repaired_dict
                else:
                    logger.warning("Retry validation also failed. Returning repaired dict.")
                    return new_repaired_dict
            except Exception as e:
                logger.error(f"Error during validation retry: {str(e)}")
                
        return repaired_dict

    @classmethod
    def perform_validation(cls, data: Dict[str, Any], document_type: str, template_dict: Dict[str, Any]) -> List[str]:
        """
        Runs the three explicit validation stages and aggregates errors.
        """
        errors = []
        errors.extend(cls.validate_schema(data, document_type))
        errors.extend(cls.validate_keys(data, template_dict))
        errors.extend(cls.validate_business(data, document_type))
        return errors

    @classmethod
    def validate_schema(cls, data: Dict[str, Any], document_type: str) -> List[str]:
        """
        Stage 1: Pydantic Schema Validation
        """
        errors = []
        schema_cls = SCHEMA_REGISTRY.get(document_type)
        if not schema_cls:
            errors.append(f"No schema class registered for document type: {document_type}")
            return errors
        try:
            schema_cls.model_validate(data)
        except ValidationError as ve:
            errors.append(f"Pydantic Schema Validation failed: {str(ve)}")
        return errors

    @classmethod
    def validate_keys(cls, data: Dict[str, Any], template_dict: Dict[str, Any]) -> List[str]:
        """
        Stage 2: Key Validation (Checks template structure is preserved)
        """
        return cls.check_keys_match(template_dict, data)

    @classmethod
    def validate_business(cls, data: Dict[str, Any], document_type: str) -> List[str]:
        """
        Stage 3: Business Validation (Required fields, enums, consistency checks)
        """
        errors = []
        
        # 1. Enums validation helper
        def check_enums(node: Any, path: str = "") -> None:
            if isinstance(node, dict):
                # holder_type enum check
                if "holder_type" in node and node["holder_type"] is not None:
                    allowed = {"founder", "investor", "employee", "other"}
                    val = str(node["holder_type"]).lower()
                    if val not in allowed and not any(a in val for a in allowed):
                        errors.append(f"Invalid holder_type '{node['holder_type']}' at '{path}'")
                # actual_vs_budget check
                if "actual_vs_budget" in node and node["actual_vs_budget"] is not None:
                    allowed = {"actual", "budget", "forecast"}
                    val = str(node["actual_vs_budget"]).lower()
                    if val not in allowed:
                        errors.append(f"Invalid actual_vs_budget value '{node['actual_vs_budget']}' at '{path}'")
                        
                for k, v in node.items():
                    check_enums(v, f"{path}.{k}" if path else k)
            elif isinstance(node, list):
                for idx, item in enumerate(node):
                    check_enums(item, f"{path}[{idx}]")
                    
        check_enums(data)

        # 2. Consistency validation check
        if document_type == "cap_table":
            # Cap table specific consistency check: Ownership percentage sum
            shareholders = data.get("shareholders") or []
            total_percentage = 0.0
            has_percentages = False
            for sh in shareholders:
                ownership = sh.get("ownership_percentage")
                if ownership and isinstance(ownership, dict) and ownership.get("value") is not None:
                    try:
                        total_percentage += float(ownership["value"])
                        has_percentages = True
                    except (ValueError, TypeError):
                        pass
            if has_percentages and (total_percentage < 90.0 or total_percentage > 110.0):
                logger.warning(f"Cap table consistency warning: Total ownership percentage is {total_percentage}% (expected ~100%)")
                
        return errors

    @classmethod
    def check_keys_match(cls, template: Any, output: Any, path: str = "") -> List[str]:
        """
        Ensures output structure preserves templates exactly (no extra/missing keys).
        Allows standard metric sub-fields/provenance keys inside metric value dicts.
        """
        errors = []
        if isinstance(template, dict):
            if not isinstance(output, dict):
                errors.append(f"Expected object at '{path}', got {type(output).__name__}")
                return errors
            # Check for missing keys
            for key in template.keys():
                if key not in output:
                    errors.append(f"Missing key '{key}' at '{path}'")
                else:
                    errors.extend(cls.check_keys_match(template[key], output[key], f"{path}.{key}" if path else key))
            
            # Check for extra keys
            is_metric_dict = "value" in template or "value" in output
            allowed_metric_keys = {
                "value", "unit", "period", "actual_vs_budget", "source_reference", 
                "source_block_id", "page", "slide", "sheet", "extracted_text_snippet",
                "confidence", "evidence"
            }
            for key in output.keys():
                if is_metric_dict and key in allowed_metric_keys:
                    continue
                if key not in template:
                    errors.append(f"Unexpected extra key '{key}' at '{path}'")
        elif isinstance(template, list):
            if not isinstance(output, list):
                errors.append(f"Expected list at '{path}', got {type(output).__name__}")
                return errors
            # Check items against the schema template (first element)
            if template and output:
                schema_item = template[0]
                for idx, item in enumerate(output):
                    errors.extend(cls.check_keys_match(schema_item, item, f"{path}[{idx}]"))
        return errors
