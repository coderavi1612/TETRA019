import json
from typing import Dict, Any, List, Optional
import logging

from app.extractors.specification_registry import SpecificationRegistry

logger = logging.getLogger(__name__)

class VerificationEngine:
    @classmethod
    def verify_document(
        cls, 
        document_type: str, 
        document_json: Dict[str, Any], 
        template_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Runs completeness and template hierarchy checks.
        Returns a verification status dictionary.
        """
        # 1. Check template hierarchy and unexpected keys
        unexpected_keys = []
        missing_keys = []
        
        def compare_keys(t_dict: Any, d_dict: Any, path: str = "") -> None:
            if isinstance(t_dict, dict) and isinstance(d_dict, dict):
                # Check missing keys
                for k in t_dict:
                    if k not in d_dict:
                        missing_keys.append(f"{path}.{k}" if path else k)
                    else:
                        compare_keys(t_dict[k], d_dict[k], f"{path}.{k}" if path else k)
                # Check unexpected keys
                allowed_metric_keys = {
                    "value", "unit", "period", "actual_vs_budget", "source_reference", 
                    "source_block_id", "page", "slide", "sheet", "extracted_text_snippet"
                }
                is_metric = "value" in t_dict or "value" in d_dict
                for k in d_dict:
                    if is_metric and k in allowed_metric_keys:
                        continue
                    if k not in t_dict:
                        unexpected_keys.append(f"{path}.{k}" if path else k)
            elif isinstance(t_dict, list) and isinstance(d_dict, list):
                if t_dict and d_dict:
                    for idx, item in enumerate(d_dict):
                        compare_keys(t_dict[0], item, f"{path}[{idx}]")
        
        compare_keys(template_dict, document_json)
        
        # 2. Check required sections (e.g. top-level keys in template must exist)
        missing_sections = []
        for section in template_dict.keys():
            if section not in document_json:
                missing_sections.append(section)
                
        # 3. Check expected fields from Specification Registry
        expected_fields = SpecificationRegistry.get_expected_fields(document_type) or []
        checked_fields_count = len(expected_fields)
        found_fields_count = 0
        missing_fields = []
        
        # Helper to find values recursively
        def find_field_value(data: Any, field_name: str) -> Optional[Any]:
            if isinstance(data, dict):
                if "value" in data and data.get("value") is not None:
                    return data.get("value")
                for k, v in data.items():
                    if k.lower() == field_name.replace(" ", "_").lower():
                        if isinstance(v, dict) and "value" in v:
                            return v.get("value")
                    res = find_field_value(v, field_name)
                    if res is not None:
                        return res
            elif isinstance(data, list):
                for item in data:
                    res = find_field_value(item, field_name)
                    if res is not None:
                        return res
            return None

        # Check expected fields count
        if not expected_fields:
            expected_fields = [k for k in template_dict.keys() if k != "document_metadata"]
            checked_fields_count = len(expected_fields)
            
        for field in expected_fields:
            val = find_field_value(document_json, field)
            if val is not None:
                found_fields_count += 1
            else:
                missing_fields.append(field)
                
        # 4. Check if extracted values are not unexpectedly all null
        total_metrics = 0
        non_null_metrics = 0
        
        def count_metrics(data: Any) -> None:
            nonlocal total_metrics, non_null_metrics
            if isinstance(data, dict):
                if "value" in data:
                    total_metrics += 1
                    if data.get("value") is not None:
                        non_null_metrics += 1
                else:
                    for v in data.values():
                        count_metrics(v)
            elif isinstance(data, list):
                for item in data:
                    count_metrics(item)
                    
        count_metrics(document_json)
        
        # Determine status
        status = "PASS"
        if unexpected_keys or missing_sections:
            status = "FAIL"
        if total_metrics > 0 and non_null_metrics == 0:
            status = "FAIL"
        if checked_fields_count > 0 and found_fields_count == 0:
            status = "FAIL"
            
        return {
            "document": document_type,
            "status": status,
            "required_fields_checked": checked_fields_count,
            "required_fields_found": found_fields_count,
            "missing_required_fields": len(missing_fields),
            "unexpected_keys_found": len(unexpected_keys),
            "missing_sections": len(missing_sections),
            "total_metrics": total_metrics,
            "non_null_metrics": non_null_metrics
        }
