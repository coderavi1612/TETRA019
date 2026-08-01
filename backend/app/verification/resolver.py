from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.verification.comparison_registry import ComparisonRegistry
from app.verification.comparator import Comparator
from app.verification.schemas.comparison import NormalizedValue

class ResolvedComparison(BaseModel):
    authoritative_document: Optional[str] = None
    authoritative_value: Any = None
    comparison_result: str # "Verified Match" | "Within Tolerance" | "Mismatch" | "Missing Information"
    is_resolvable: bool

class ConflictResolver:
    @staticmethod
    def resolve_field(canonical_field: str, docs: Dict[str, NormalizedValue]) -> ResolvedComparison:
        # 1. Filter out missing values (None)
        available_docs = {
            doc_type: val_obj
            for doc_type, val_obj in docs.items()
                if val_obj.normalized_value is not None
        }

        # 2. Check if no values or only 1 value exists
        total_registered_docs = len(ComparisonRegistry.get_authoritative_order(canonical_field) or docs.keys())
        
        if not available_docs:
            return ResolvedComparison(
                authoritative_document=None,
                authoritative_value=None,
                comparison_result="Missing Information",
                is_resolvable=False
            )

        # 3. Determine Authoritative Source
        auth_order = ComparisonRegistry.get_authoritative_order(canonical_field) or []
        auth_doc = None
        for doc in auth_order:
            if doc in available_docs:
                auth_doc = doc
                break

        is_resolvable = auth_doc is not None
        if not auth_doc:
            # Fallback to first available document
            auth_doc = list(available_docs.keys())[0]

        auth_value = available_docs[auth_doc].normalized_value

        # 4. Compare all other documents to authoritative
        comparison_results = []
        for doc_type, val_obj in available_docs.items():
            if doc_type == auth_doc:
                continue
            res = Comparator.compare_values(canonical_field, auth_value, val_obj.normalized_value)
            comparison_results.append(res)

        # Determine overall result
        if len(available_docs) < total_registered_docs and not comparison_results:
            overall_res = "Missing Information"
        elif "Mismatch" in comparison_results:
            overall_res = "Mismatch"
        elif "Within Tolerance" in comparison_results:
            overall_res = "Within Tolerance"
        else:
            overall_res = "Verified Match"

        # If only 1 document is present but there are multiple mapped sources, mark as Missing Information
        if len(available_docs) < 2 and total_registered_docs > 1:
            overall_res = "Missing Information"

        return ResolvedComparison(
            authoritative_document=auth_doc,
            authoritative_value=auth_value,
            comparison_result=overall_res,
            is_resolvable=is_resolvable
        )
