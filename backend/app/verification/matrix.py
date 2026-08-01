import os
import json
from typing import Dict, List, Any
from app.verification.schemas.comparison import MappedValue, NormalizedValue, ComparisonMatrix
from app.verification.normalizer import FieldNormalizer
from app.verification.comparison_registry import ComparisonRegistry

class ComparisonMatrixBuilder:
    @staticmethod
    def build_matrix(mapped_values: List[MappedValue]) -> ComparisonMatrix:
        matrix_dict: Dict[str, Dict[str, NormalizedValue]] = {}
        for val in mapped_values:
            strategy = ComparisonRegistry.get_comparison_strategy(val.canonical_path) or "string"
            norm_val, norm_unit = FieldNormalizer.normalize_value(val.value, strategy, val.unit)
            norm_currency = FieldNormalizer.normalize_currency(val.currency)
            
            norm_obj = NormalizedValue(
                document_type=val.document_type,
                original_path=val.original_path,
                canonical_path=val.canonical_path,
                value=val.value,
                unit=val.unit,
                currency=val.currency,
                source_block_id=val.source_block_id,
                page=val.page,
                slide=val.slide,
                sheet=val.sheet,
                normalized_value=norm_val,
                normalized_unit=norm_unit,
                normalized_currency=norm_currency
            )
            
            if val.canonical_path not in matrix_dict:
                matrix_dict[val.canonical_path] = {}
            matrix_dict[val.canonical_path][val.document_type] = norm_obj
            
        return ComparisonMatrix(matrix=matrix_dict)

    @staticmethod
    def save_reports(matrix: ComparisonMatrix, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        
        matrix_path = os.path.join(output_dir, "comparison_matrix.json")
        with open(matrix_path, "w", encoding="utf-8") as f:
            json.dump(matrix.model_dump(), f, indent=2, default=str)
            
        canonical_fields = {}
        for canonical_path, docs in matrix.matrix.items():
            canonical_fields[canonical_path] = {
                doc_type: val.original_path
                for doc_type, val in docs.items()
            }
            
        fields_path = os.path.join(output_dir, "canonical_fields.json")
        with open(fields_path, "w", encoding="utf-8") as f:
            json.dump(canonical_fields, f, indent=2)
