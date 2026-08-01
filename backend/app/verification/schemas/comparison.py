from pydantic import BaseModel
from typing import Any, Dict, Optional

class MappedValue(BaseModel):
    document_type: str
    original_path: str
    canonical_path: str
    value: Any
    unit: Optional[str] = None
    currency: Optional[str] = None
    source_block_id: Optional[str] = None
    page: Optional[int] = None
    slide: Optional[int] = None
    sheet: Optional[str] = None
    extracted_text_snippet: Optional[str] = None

class NormalizedValue(MappedValue):
    normalized_value: Any
    normalized_unit: Optional[str] = None
    normalized_currency: Optional[str] = None

class ComparisonMatrix(BaseModel):
    matrix: Dict[str, Dict[str, NormalizedValue]]
