import os
import json
from typing import Any, Dict, List, Optional
from app.core import sha256_string

class ComparisonRegistry:
    _rules: List[Dict[str, Any]] = []
    _rules_by_name: Dict[str, Dict[str, Any]] = {}
    _hash: str = ""
    _loaded: bool = False

    @classmethod
    def load(cls) -> None:
        if cls._loaded:
            return

        rules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comparison_rules.json")
        if not os.path.exists(rules_path):
            raise FileNotFoundError(f"Comparison rules file not found: {rules_path}")

        with open(rules_path, "r", encoding="utf-8") as f:
            content = f.read()
            cls._hash = sha256_string(content)
            data = json.loads(content)

        rules = data.get("rules", [])
        
        # Validation checks
        seen_canonical = set()
        from app.extractors.template_loader import TemplateLoader
        # Make sure TemplateLoader has loaded templates
        TemplateLoader.load_all_templates()

        for rule in rules:
            name = rule.get("canonical_name")
            if not name:
                raise ValueError("Registry rule missing 'canonical_name'")
            if name in seen_canonical:
                raise ValueError(f"Duplicate canonical field found in registry: {name}")
            seen_canonical.add(name)

            # Duplicate priorities check
            auth_order = rule.get("authoritative_order", [])
            if len(auth_order) != len(set(auth_order)):
                raise ValueError(f"Duplicate document priorities in authoritative_order for field: {name}")

            # Check mappings structure
            mappings = rule.get("mappings", {})
            if not isinstance(mappings, dict):
                raise ValueError(f"Mappings for field {name} must be a dictionary")

            # Check strategies
            strategy = rule.get("strategy")
            allowed_strategies = {"numeric", "string", "date", "currency", "boolean", "ownership"}
            if strategy not in allowed_strategies:
                raise ValueError(f"Invalid strategy '{strategy}' for field {name}. Allowed: {allowed_strategies}")

            # Check tolerance definitions
            tolerance = rule.get("tolerance")
            if tolerance:
                tol_str = str(tolerance).strip().lower()
                if tol_str != "exact":
                    if not tol_str.endswith("%"):
                        raise ValueError(f"Invalid tolerance '{tolerance}' for field {name}. Must be 'Exact' or end with '%'")
                    try:
                        float(tol_str.replace("%", "").strip())
                    except ValueError:
                        raise ValueError(f"Invalid tolerance number format in '{tolerance}' for field {name}")

            # Check template paths validation
            for doc_type, path in mappings.items():
                try:
                    template = TemplateLoader.get_template(doc_type)
                except Exception as e:
                    raise ValueError(f"Invalid mapping document type '{doc_type}' for field {name}: {str(e)}")
                
                parts = path.split(".")
                curr = template
                for part in parts:
                    if part.endswith("[]"):
                        clean_part = part.replace("[]", "")
                        if not isinstance(curr, dict) or clean_part not in curr:
                            raise ValueError(f"Invalid path segment '{part}' in path '{path}' for field {name} under template '{doc_type}'")
                        list_val = curr[clean_part]
                        if isinstance(list_val, list) and len(list_val) > 0:
                            curr = list_val[0]
                        else:
                            curr = None
                            break
                    else:
                        if curr is not None:
                            if not isinstance(curr, dict) or part not in curr:
                                raise ValueError(f"Invalid path segment '{part}' in path '{path}' for field {name} under template '{doc_type}'")
                            curr = curr[part]

        cls._rules = rules
        cls._rules_by_name = {rule["canonical_name"]: rule for rule in rules}
        cls._loaded = True

    @classmethod
    def get_hash(cls) -> str:
        cls._ensure_loaded()
        return cls._hash

    @classmethod
    def get_rules(cls) -> List[Dict[str, Any]]:
        cls._ensure_loaded()
        return cls._rules

    @classmethod
    def get_field(cls, canonical_name: str) -> Optional[Dict[str, Any]]:
        cls._ensure_loaded()
        # Direct lookup or pattern match for dynamic keys (like Ownership.<holder_name>)
        if canonical_name in cls._rules_by_name:
            return cls._rules_by_name[canonical_name]
        
        for name, rule in cls._rules_by_name.items():
            if "<" in name and ">" in name:
                # Dynamic matching, e.g., Ownership.<holder_name> matches Ownership.FounderA
                prefix = name.split("<")[0]
                if canonical_name.startswith(prefix):
                    return rule
        return None

    @classmethod
    def get_document_mapping(cls, document_type: str) -> Dict[str, str]:
        cls._ensure_loaded()
        mappings = {}
        for name, rule in cls._rules_by_name.items():
            if document_type in rule.get("mappings", {}):
                mappings[name] = rule["mappings"][document_type]
        return mappings

    @classmethod
    def get_authoritative_order(cls, canonical_name: str) -> List[str]:
        field = cls.get_field(canonical_name)
        return field.get("authoritative_order", []) if field else []

    @classmethod
    def get_tolerance(cls, canonical_name: str) -> Optional[str]:
        field = cls.get_field(canonical_name)
        return field.get("tolerance") if field else None

    @classmethod
    def get_comparison_strategy(cls, canonical_name: str) -> Optional[str]:
        field = cls.get_field(canonical_name)
        return field.get("strategy") if field else None

    @classmethod
    def get_required_fields(cls) -> List[str]:
        cls._ensure_loaded()
        return [name for name, rule in cls._rules_by_name.items() if rule.get("required")]

    @classmethod
    def list_all_fields(cls) -> List[str]:
        cls._ensure_loaded()
        return list(cls._rules_by_name.keys())

    @classmethod
    def _ensure_loaded(cls) -> None:
        if not cls._loaded:
            cls.load()
