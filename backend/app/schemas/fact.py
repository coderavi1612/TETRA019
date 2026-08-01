from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Literal

class FactContext(BaseModel):
    section: str = ""
    sentence: str = ""

class ExtractedFact(BaseModel):
    fact_id: str
    category: str
    metric_name: str
    value: Optional[Any] = None
    display_value: str = ""
    unit: str = ""
    currency: str = ""
    period: str = ""
    fiscal_year: str = ""
    document_type: str
    source_document: str
    source_block_id: str
    page: Optional[int] = None
    confidence: float = 0.0
    confidence_reason: Literal[
        "Structured Table",
        "Explicit Sentence",
        "Heading",
        "Bullet List",
        "Repeated Across Blocks"
    ]
    extraction_method: Literal["text", "table", "heading", "list"]
    status: str = "extracted"
    context: FactContext = Field(default_factory=FactContext)

class DocumentFacts(BaseModel):
    document_type: str
    categories: Dict[str, List[ExtractedFact]] = Field(default_factory=dict)

class CompanyFacts(BaseModel):
    schema_version: str = "1.0"
    registry_version: str = ""
    prompt_version: str = ""
    company_id: str
    documents: List[DocumentFacts] = Field(default_factory=list)
