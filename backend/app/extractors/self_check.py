import json
from typing import Dict, Any, List
import logging

from app.schemas.parsed_document import ParsedDocument
from app.schemas.registry import SCHEMA_REGISTRY
from app.extractors.validator import FactValidator
from app.extractors.traceability import TraceabilityValidator
from app.extractors.cache import FactCache

logger = logging.getLogger(__name__)

class SelfChecker:
    @classmethod
    def run_self_check(
        cls, 
        company_id: str,
        document_type: str, 
        document_json: Dict[str, Any], 
        template_dict: Dict[str, Any],
        parsed_doc: ParsedDocument,
        doc_cache_key: str
    ) -> List[str]:
        """
        Runs comprehensive post-extraction self-checks.
        Returns a list of failed check descriptions, or empty list if all PASS.
        """
        errors = []
        
        # 1. Output validates against Schema Registry (Pydantic validation)
        schema_cls = SCHEMA_REGISTRY.get(document_type)
        if not schema_cls:
            errors.append(f"No schema class registered for document type: {document_type}")
        else:
            try:
                schema_cls.model_validate(document_json)
            except Exception as ve:
                errors.append(f"Schema validation failed: {str(ve)}")
                
        # 2. Template unchanged & No extra keys
        key_errors = FactValidator.check_keys_match(template_dict, document_json)
        if key_errors:
            errors.extend(key_errors)
            
        # 3. Required fields check
        # Verify that we have some non-null facts extracted so the output isn't completely empty.
        non_null_count = 0
        def count_non_null(data: Any) -> None:
            nonlocal non_null_count
            if isinstance(data, dict):
                if "value" in data and data.get("value") is not None:
                    non_null_count += 1
                for v in data.values():
                    count_non_null(v)
            elif isinstance(data, list):
                for item in data:
                    count_non_null(item)
        count_non_null(document_json)
        if non_null_count == 0:
            errors.append("Required fields check failed: no non-null facts extracted from the document")
            
        # 4. Traceability validation
        try:
            trace_valid, report = TraceabilityValidator.validate_document(document_json, parsed_doc)
            if not trace_valid:
                errors.append("Traceability validation check failed: source references could not be resolved to evidence blocks")
        except Exception as e:
            errors.append(f"Traceability validation check crashed: {str(e)}")
            
        # 5. Cache consistency check
        try:
            cached = FactCache.load_document(company_id, doc_cache_key)
            if cached is None:
                errors.append("Cache consistency check failed: document was not saved to cache")
            else:
                if json.dumps(cached, sort_keys=True) != json.dumps(document_json, sort_keys=True):
                    errors.append("Cache consistency check failed: cached data does not match generated output data")
        except Exception as e:
            errors.append(f"Cache consistency check failed: {str(e)}")
            
        return errors
