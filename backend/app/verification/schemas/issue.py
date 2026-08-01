from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class Evidence(BaseModel):
    document: str
    value: Any
    canonical_path: str
    source_block_id: Optional[str] = None
    page: Optional[int] = None
    slide: Optional[int] = None
    sheet: Optional[str] = None
    snippet: Optional[str] = None

class Issue(BaseModel):
    id: str
    classification: str # 'Verified Mismatch' | 'Unresolved Inconsistency' | 'Missing Information'
    severity: str # 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
    field: str # Canonical field name
    description: str
    documents: List[str]
    evidence: List[Evidence]
