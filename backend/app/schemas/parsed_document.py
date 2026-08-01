from pydantic import BaseModel, Field
from typing import List, Optional, Any

class SectionInfo(BaseModel):
    title: Optional[str] = None
    type: str = "unknown"
    confidence: float = 0.0

class BlockSource(BaseModel):
    file: str
    page: Optional[int] = None
    slide: Optional[int] = None
    sheet: Optional[str] = None

class ContentBlock(BaseModel):
    id: str
    sequence: int
    content_type: str = Field(..., description="'text' or 'table'")
    page: Optional[int] = None
    slide: Optional[int] = None
    sheet: Optional[str] = None
    section: SectionInfo = Field(default_factory=SectionInfo)
    raw_text: str
    rows: Optional[List[List[Any]]] = None
    source: BlockSource

class ParserInfo(BaseModel):
    name: str
    version: str

class DocumentStatistics(BaseModel):
    pages: int = 0
    slides: int = 0
    sheets: int = 0
    blocks: int = 0
    tables: int = 0
    words: int = 0

class DocumentMetadata(BaseModel):
    company_id: str
    file_size: int
    extension: str
    mime_type: str
    created_at: str
    parser: ParserInfo
    statistics: DocumentStatistics

class ParsedDocument(BaseModel):
    document_id: str
    document_name: str
    document_type: str
    status: str = "parsed"
    metadata: DocumentMetadata
    content: List[ContentBlock]
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

class ManifestDocument(BaseModel):
    document_id: str
    file_name: str
    document_type: str
    status: str
    parser: str
    output_file: str

class Manifest(BaseModel):
    company_id: str
    documents: List[ManifestDocument]
