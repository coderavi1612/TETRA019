from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class EvidenceEntry(BaseModel):
    document: str
    value: Any
    canonical_path: str
    source_block_id: Optional[str] = None
    page: Optional[int] = None
    slide: Optional[int] = None
    sheet: Optional[str] = None
    snippet: Optional[str] = None

class InconsistencyReportEntry(BaseModel):
    issue_id: str
    classification: str
    severity: str
    canonical_field: str
    documents: List[str]
    authoritative_document: Optional[str] = None
    authoritative_value: Optional[Any] = None
    description: str
    business_impact: str
    recommended_action: str
    evidence: List[EvidenceEntry]

class FollowUpQuestion(BaseModel):
    question_id: str
    priority: str
    related_issue: str
    question: str
    why_it_matters: str
    required_document: str
    expected_answer: str

class ScoringBreakdown(BaseModel):
    completeness: int
    consistency: int
    recency: int
    factuality: int

class ReadinessSummary(BaseModel):
    company_id: str
    company_name: Optional[str] = None
    overall_status: str
    readiness_score: int
    overall_readiness_score: Optional[int] = None
    scoring_breakdown: Optional[ScoringBreakdown] = None
    documents_reviewed: List[str]
    verified_matches: int
    verified_mismatches: int
    missing_information: int
    unresolved_inconsistencies: int
    strengths: List[str]
    risks: List[str]
    next_steps: List[str]
    executive_summary: str

class ExecutiveSummary(BaseModel):
    company_overview: str
    overall_readiness: str
    top_risks: List[str]
    top_strengths: List[str]
    critical_issues: List[str]
    immediate_actions: List[str]
    investor_readiness: str

class ReadinessManifest(BaseModel):
    schema_version: str = "1.0"
    pipeline_version: str = "1.0"
    comparison_version: str = "1.0"
    registry_version: str
    prompt_version: str
    prompt_hashes: Dict[str, str]
    model: str
    temperature: float = 0.1
    cache_hits: int
    cache_misses: int
    processing_times: Dict[str, float]
    report_hashes: Dict[str, str]
    generated_files: List[str]
    retry_counts: Dict[str, int]
    validation_status: str
    pdf_generation_status: str
    markdown_generation_status: str

class VerifyApiResponse(BaseModel):
    company_id: str
    readiness_status: str
    readiness_score: int
    reports_generated: int
    cache_hits: int
    cache_misses: int
    critical_issues: int
    warnings: int
    processing_time_ms: int
    validation_status: str
    failed_documents: List[str] = []
    errors: List[str] = []
