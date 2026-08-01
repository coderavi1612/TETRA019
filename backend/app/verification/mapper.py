import re
from typing import Any, Dict, List, Optional
from app.verification.schemas.comparison import MappedValue
from app.verification.normalizer import FieldNormalizer

class CanonicalFieldMapper:
    @staticmethod
    def map_document(doc_type: str, doc_json: Dict[str, Any], registry_rules: List[Dict[str, Any]]) -> List[MappedValue]:
        mapped_values = []
        for rule in registry_rules:
            canonical_name = rule["canonical_name"]
            mappings = rule.get("mappings", {})
            if doc_type not in mappings:
                continue
            path = mappings[doc_type]
            extracted = CanonicalFieldMapper.extract_values(doc_json, path, canonical_name, doc_type)
            mapped_values.extend(extracted)
        return mapped_values

    @staticmethod
    def extract_values(data: Any, path: str, canonical_name: str, doc_type: str) -> List[MappedValue]:
        results = []
        
        def get_nested(obj: Any, path_parts: List[str]) -> Any:
            curr = obj
            for part in path_parts:
                if not isinstance(curr, dict):
                    return None
                curr = curr.get(part)
            return curr

        parts = path.split(".")
        
        # Check if list expansion exists
        list_idx = -1
        for idx, part in enumerate(parts):
            if part.endswith("[]"):
                list_idx = idx
                break

        if list_idx != -1:
            parent_parts = [p.replace("[]", "") for p in parts[:list_idx+1]]
            child_parts = parts[list_idx+1:]
            
            list_data = get_nested(data, parent_parts)
            if not isinstance(list_data, list):
                return results

            for item in list_data:
                # 1. Cap table dynamic holder mapping
                if "<holder_name>" in canonical_name:
                    holder_name = item.get("holder_name") or item.get("founder_name")
                    if holder_name:
                        holder_clean = re.sub(r'[^a-zA-Z0-9]', '_', str(holder_name).strip())
                        dynamic_canonical = canonical_name.replace("<holder_name>", holder_clean)
                        val_node = get_nested(item, child_parts)
                        if val_node is not None:
                            results.append(CanonicalFieldMapper.build_mapped_value(
                                doc_type, path, dynamic_canonical, val_node
                            ))
                else:
                    # 2. Period dynamic mapping (e.g. FY24)
                    period_val = item.get("period_label") or item.get("period") or item.get("period_start_date")
                    if period_val:
                        norm_period = FieldNormalizer.normalize_period(str(period_val))
                        period_suffix = canonical_name.split(".")[-1]
                        if norm_period == period_suffix:
                            val_node = get_nested(item, child_parts)
                            if val_node is not None:
                                results.append(CanonicalFieldMapper.build_mapped_value(
                                    doc_type, path, canonical_name, val_node
                                ))
        else:
            val_node = get_nested(data, parts)
            if val_node is not None:
                results.append(CanonicalFieldMapper.build_mapped_value(
                    doc_type, path, canonical_name, val_node
                ))
                
        return results

    @staticmethod
    def build_mapped_value(doc_type: str, original_path: str, canonical_path: str, val_node: Any) -> MappedValue:
        if isinstance(val_node, dict) and ("value" in val_node or "source_reference" in val_node or "source_block_id" in val_node):
            val = val_node.get("value")
            unit = val_node.get("unit")
            currency = val_node.get("currency")
            source_block_id = val_node.get("source_reference") or val_node.get("source_block_id")
            page = val_node.get("page")
            slide = val_node.get("slide")
            sheet = val_node.get("sheet")
            snippet = val_node.get("extracted_text_snippet")
            return MappedValue(
                document_type=doc_type,
                original_path=original_path,
                canonical_path=canonical_path,
                value=val,
                unit=unit,
                currency=currency,
                source_block_id=source_block_id,
                page=page,
                slide=slide,
                sheet=sheet,
                extracted_text_snippet=snippet
            )
        else:
            return MappedValue(
                document_type=doc_type,
                original_path=original_path,
                canonical_path=canonical_path,
                value=val_node,
                unit=None,
                currency=None,
                source_block_id=None,
                page=None,
                slide=None,
                sheet=None
            )
