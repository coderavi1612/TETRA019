import json
import re
from typing import List, Dict, Any

class JSONRepairer:
    @staticmethod
    def clean_json_string(raw_response: str) -> str:
        """
        Removes markdown code fences and cleans up common JSON syntax issues.
        """
        cleaned = raw_response.strip()
        
        # Remove markdown code blocks if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
            cleaned = re.sub(r"\n```$", "", cleaned).strip()
            
        # Basic syntax cleaning: remove trailing commas before closing braces/brackets
        cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
        
        # Try to balance unclosed array brackets or object braces
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
    def repair_facts_list(cls, raw_response: str, document_type: str) -> List[Dict[str, Any]]:
        """
        Loads the JSON and repairs syntax, missing optional fields, numerical formatting,
        and enforces strict enums for confidence reasons and extraction methods.
        """
        cleaned_str = cls.clean_json_string(raw_response)
        
        try:
            data = json.loads(cleaned_str)
        except Exception:
            data = []
            matches = re.findall(r"\{[\s\S]*?\}", cleaned_str)
            for match in matches:
                try:
                    obj = json.loads(match)
                    data.append(obj)
                except Exception:
                    pass
                    
        if not isinstance(data, list):
            if isinstance(data, dict):
                data = [data]
            else:
                data = []

        repaired_list = []
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                continue
            
            repaired = {}
            
            # Document trace details
            repaired["document_type"] = str(item.get("document_type") or document_type)
            repaired["source_document"] = str(item.get("source_document") or "")
            repaired["source_block_id"] = str(item.get("source_block_id") or "")
            
            # Unique stable ID
            repaired["fact_id"] = str(item.get("fact_id") or f"fact_{repaired['document_type']}_{idx}")
            
            # Category and Metric details
            repaired["category"] = str(item.get("category") or "financial")
            repaired["metric_name"] = str(item.get("metric_name") or "unknown")
            
            # Display value
            repaired["display_value"] = str(item.get("display_value") or "")
            
            # Try to convert numerical strings to float or int for proper validation
            raw_val = item.get("value")
            if raw_val is not None:
                if isinstance(raw_val, str):
                    clean_str_val = raw_val.strip().replace(",", "")
                    if clean_str_val.lower() in ["null", "none", "n/a", ""]:
                        repaired["value"] = None
                    elif re.match(r"^-?\d+$", clean_str_val):
                        repaired["value"] = int(clean_str_val)
                    elif re.match(r"^-?\d+\.\d+$", clean_str_val):
                        repaired["value"] = float(clean_str_val)
                    else:
                        repaired["value"] = raw_val
                else:
                    repaired["value"] = raw_val
            else:
                repaired["value"] = None
                
            # If display value is empty, fallback to value string
            if not repaired["display_value"] and repaired["value"] is not None:
                repaired["display_value"] = str(repaired["value"])

            repaired["unit"] = str(item.get("unit") or "")
            repaired["currency"] = str(item.get("currency") or "")
            repaired["period"] = str(item.get("period") or "")
            
            f_year = item.get("fiscal_year")
            repaired["fiscal_year"] = str(f_year) if f_year is not None else ""
            
            # Page number
            page_val = item.get("page")
            if page_val is not None:
                try:
                    repaired["page"] = int(page_val)
                except Exception:
                    repaired["page"] = None
            else:
                repaired["page"] = None

            # Confidence float parsing
            conf_val = item.get("confidence")
            if conf_val is not None:
                try:
                    if isinstance(conf_val, str):
                        conf_val = conf_val.replace("%", "").strip()
                    repaired["confidence"] = float(conf_val)
                except Exception:
                    repaired["confidence"] = 90.0
            else:
                repaired["confidence"] = 90.0
                
            # Map confidence reasons strictly to allowed enum strings
            raw_reason = str(item.get("confidence_reason") or "").lower()
            if "table" in raw_reason or "sheet" in raw_reason or "grid" in raw_reason:
                repaired["confidence_reason"] = "Structured Table"
            elif "sentence" in raw_reason or "explicit" in raw_reason or "text" in raw_reason or "stated" in raw_reason:
                repaired["confidence_reason"] = "Explicit Sentence"
            elif "heading" in raw_reason or "title" in raw_reason or "header" in raw_reason:
                repaired["confidence_reason"] = "Heading"
            elif "list" in raw_reason or "bullet" in raw_reason or "item" in raw_reason:
                repaired["confidence_reason"] = "Bullet List"
            elif "repeat" in raw_reason or "cross" in raw_reason:
                repaired["confidence_reason"] = "Repeated Across Blocks"
            else:
                repaired["confidence_reason"] = "Explicit Sentence"

            # Map extraction methods strictly to allowed enum strings
            raw_method = str(item.get("extraction_method") or "").lower()
            if "table" in raw_method:
                repaired["extraction_method"] = "table"
            elif "heading" in raw_method or "title" in raw_method:
                repaired["extraction_method"] = "heading"
            elif "list" in raw_method or "bullet" in raw_method:
                repaired["extraction_method"] = "list"
            else:
                if repaired["confidence_reason"] == "Structured Table":
                    repaired["extraction_method"] = "table"
                elif repaired["confidence_reason"] == "Heading":
                    repaired["extraction_method"] = "heading"
                elif repaired["confidence_reason"] == "Bullet List":
                    repaired["extraction_method"] = "list"
                else:
                    repaired["extraction_method"] = "text"

            repaired["status"] = "extracted"
            
            # Map context structure
            context_data = item.get("context") or {}
            if isinstance(context_data, str):
                repaired["context"] = {"section": "", "sentence": context_data}
            elif isinstance(context_data, dict):
                repaired["context"] = {
                    "section": str(context_data.get("section") or ""),
                    "sentence": str(context_data.get("sentence") or "")
                }
            else:
                repaired["context"] = {"section": "", "sentence": ""}
                
            repaired_list.append(repaired)
            
        return repaired_list
