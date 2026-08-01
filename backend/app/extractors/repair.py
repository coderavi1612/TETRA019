import json
import re
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class JSONRepairer:
    @staticmethod
    def clean_json_string(raw_response: str) -> str:
        """
        Removes markdown fences and fixes common syntax problems to make JSON loads reliable.
        """
        cleaned = raw_response.strip()
        
        # Remove markdown code blocks if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
            cleaned = re.sub(r"\n```$", "", cleaned).strip()
            
        # Balance quotes and clean up smart/invalid quotes
        cleaned = cleaned.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        
        # Handle trailing commas before closing brackets/braces
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
        
        # Balance unclosed brackets and braces
        open_brackets = cleaned.count("[")
        close_brackets = cleaned.count("]")
        if open_brackets > close_brackets:
            cleaned += "]" * (open_brackets - close_brackets)
            
        open_braces = cleaned.count("{")
        close_braces = cleaned.count("}")
        if open_braces > close_braces:
            cleaned += "}" * (open_braces - close_braces)
            
        return cleaned

    @classmethod
    def repair_json_data(cls, raw_response: str, template_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses the JSON response, then recursively walks the structure alongside
        the template to coerce types and fill in missing fields without fabricating data.
        """
        cleaned_str = cls.clean_json_string(raw_response)
        
        try:
            data = json.loads(cleaned_str)
        except Exception as e:
            logger.warning(f"JSON loads failed during repair: {str(e)}. Falling back to template structure.")
            import copy
            return copy.deepcopy(template_dict)
            
        if not isinstance(data, dict):
            import copy
            return copy.deepcopy(template_dict)
            
        import copy
        repaired = copy.deepcopy(template_dict)
        cls._recursive_repair(repaired, data)
        return repaired

    @classmethod
    def _recursive_repair(cls, target: Any, source: Any) -> None:
        if isinstance(target, dict) and isinstance(source, dict):
            for k in list(target.keys()):
                s_val = source.get(k)
                if s_val is None:
                    # Keep default template value (usually null or empty list)
                    continue
                    
                # If target field is a metric value structure (contains 'value')
                if isinstance(target[k], dict) and "value" in target[k]:
                    if isinstance(s_val, dict):
                        target[k]["value"] = cls.clean_value(s_val.get("value"))
                        target[k]["unit"] = s_val.get("unit") or target[k].get("unit")
                        target[k]["period"] = s_val.get("period") or target[k].get("period")
                        target[k]["actual_vs_budget"] = s_val.get("actual_vs_budget") or target[k].get("actual_vs_budget")
                        target[k]["source_reference"] = s_val.get("source_reference")
                        target[k]["source_block_id"] = s_val.get("source_block_id")
                        target[k]["page"] = cls.to_int_or_none(s_val.get("page"))
                        target[k]["slide"] = cls.to_int_or_none(s_val.get("slide"))
                        target[k]["sheet"] = s_val.get("sheet")
                        target[k]["extracted_text_snippet"] = s_val.get("extracted_text_snippet")
                    else:
                        target[k]["value"] = cls.clean_value(s_val)
                elif isinstance(target[k], dict) and isinstance(s_val, dict):
                    cls._recursive_repair(target[k], s_val)
                elif isinstance(target[k], list) and isinstance(s_val, list):
                    if target[k]:
                        template_item = target[k][0]
                        repaired_list = []
                        for s_item in s_val:
                            import copy
                            t_item_copy = copy.deepcopy(template_item)
                            if isinstance(t_item_copy, dict) and isinstance(s_item, dict):
                                cls._recursive_repair(t_item_copy, s_item)
                                repaired_list.append(t_item_copy)
                            else:
                                cleaned_item = cls.clean_value(s_item)
                                repaired_list.append(cleaned_item)
                        target[k] = repaired_list
                    else:
                        target[k] = s_val
                else:
                    # Simple fields
                    target[k] = cls.clean_value(s_val)

    @classmethod
    def clean_value(cls, val: Any) -> Any:
        if val is None:
            return None
        if isinstance(val, str):
            clean_str = val.strip().replace(",", "")
            if clean_str.lower() in ["null", "none", "n/a", ""]:
                return None
            if clean_str.lower() == "true":
                return True
            if clean_str.lower() == "false":
                return False
            # Check integer
            if re.match(r"^-?\d+$", clean_str):
                return int(clean_str)
            # Check float
            if re.match(r"^-?\d+\.\d+$", clean_str):
                return float(clean_str)
            return val
        return val

    @classmethod
    def to_int_or_none(cls, val: Any) -> Optional[int]:
        if val is None:
            return None
        try:
            return int(float(str(val).strip()))
        except Exception:
            return None
