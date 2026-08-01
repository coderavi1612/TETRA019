from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DocumentMerger:
    @classmethod
    def merge_outputs(cls, target: Any, source: Any, path: str = "") -> Any:
        """
        Recursively merges source filled template into target filled template.
        Uses canonical paths to match nested keys and list items.
        """
        if isinstance(target, dict) and isinstance(source, dict):
            merged = dict(target)
            for k, val_s in source.items():
                current_path = f"{path}.{k}" if path else k
                val_t = target.get(k)
                
                if val_t is None:
                    # If target doesn't have it, copy from source
                    merged[k] = val_s
                elif isinstance(val_t, dict) and isinstance(val_s, dict):
                    # Check if it is a metric value structure (contains 'value')
                    if "value" in val_t and "value" in val_s:
                        # Merge metric value fields using canonical path
                        t_val = val_t.get("value")
                        s_val = val_s.get("value")
                        
                        if s_val is not None and t_val is None:
                            # Overwrite null with extracted value
                            merged[k] = val_s
                            logger.debug(f"Merged field value at {current_path}: {s_val}")
                        else:
                            # Keep target but make sure metadata is preserved if target had it
                            merged[k] = val_t
                    else:
                        merged[k] = cls.merge_outputs(val_t, val_s, current_path)
                elif isinstance(val_t, list) and isinstance(val_s, list):
                    merged[k] = cls.merge_lists(val_t, val_s, current_path)
                else:
                    # Simple fields
                    if val_s is not None and val_t is None:
                        merged[k] = val_s
                        logger.debug(f"Merged simple field at {current_path}: {val_s}")
                    else:
                        merged[k] = val_t
            return merged
            
        elif isinstance(target, list) and isinstance(source, list):
            return cls.merge_lists(target, source, path)
            
        else:
            if source is not None and target is None:
                return source
            return target

    @classmethod
    def merge_lists(cls, target_list: List[Any], source_list: List[Any], path: str) -> List[Any]:
        """
        Merges two lists by identifying unique canonical paths for dictionary items
        (e.g., using holder_name for shareholders) or falls back to concatenation.
        """
        if not target_list:
            return list(source_list)
        if not source_list:
            return list(target_list)
            
        first_item = target_list[0]
        if not isinstance(first_item, dict):
            # Fallback to deduplicated list concatenation for primitives
            combined = list(target_list)
            for item in source_list:
                if item not in combined:
                    combined.append(item)
            return combined

        # It's a list of dictionaries (e.g. lists of shareholders, founders, summaries)
        # Identify the primary key attribute for canonical path matching
        match_keys = [
            "holder_name", "founder_name", "investor_name", "safe_holder_name",
            "note_holder_name", "warrant_holder_name", "round_name", "class_name",
            "assumption_name", "period", "period_label", "scenario_name", "title"
        ]
        
        match_key = None
        for mk in match_keys:
            if mk in first_item:
                match_key = mk
                break
                
        if not match_key:
            # If no unique identifier key is found, concatenate and deduplicate
            combined = list(target_list)
            for item in source_list:
                if item not in combined:
                    combined.append(item)
            return combined

        # Merge matching items using key values
        if len(target_list) == 1 and target_list[0].get(match_key) is None:
            merged_list = []
        else:
            merged_list = list(target_list)
            
        for s_item in source_list:
            s_id = s_item.get(match_key)
            if s_id is None:
                merged_list.append(s_item)
                continue
                
            # Find matching item in target list
            found = False
            for idx, t_item in enumerate(merged_list):
                t_id = t_item.get(match_key)
                if t_id == s_id:
                    canonical_path = f"{path}[{match_key}={s_id}]"
                    merged_list[idx] = cls.merge_outputs(t_item, s_item, canonical_path)
                    found = True
                    break
                    
            if not found:
                merged_list.append(s_item)
                
        return merged_list
