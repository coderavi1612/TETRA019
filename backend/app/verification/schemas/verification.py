from pydantic import BaseModel
from typing import Dict, List, Optional

class ComparisonSummary(BaseModel):
    documents_compared: int
    canonical_fields: int
    matched: int
    close_matches: int
    verified_mismatches: int
    missing_information: int
    unresolved_inconsistencies: int

class VerificationManifest(BaseModel):
    pipeline_version: str
    generated_at: str
    registry_version: str
    comparison_rules_hash: str
    fields_compared: int
    matches: int
    close_matches: int
    verified_mismatches: int
    missing_information: int
    unresolved_inconsistencies: int
    processing_time_ms: int
    failures: List[Dict[str, str]]

class VerifyApiResponse(BaseModel):
    company_id: str
    documents_compared: int
    canonical_fields: int
    issues_generated: int
    verification_status: str # "PASS" | "FAIL"
    processing_time_ms: int
    failed_documents: List[str] = []
    warnings: List[str] = []
    errors: List[str] = []
