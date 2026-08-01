from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Coord(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float

class Block(BaseModel):
    block_id: str
    type: str  # text | heading | list | table_header
    content: str
    analysis_source: str = "native"  # native | ocr | gemini_multimodal
    coordinates: Optional[Coord] = None

class Table(BaseModel):
    table_id: str
    grid: List[List[Any]]
    analysis_source: str = "native"  # native | ocr | gemini_multimodal
    coordinates: Optional[Coord] = None

class ImageInfo(BaseModel):
    image_id: str
    type: str  # chart | screenshot | diagram
    extracted_ocr_text: Optional[str] = None
    has_visual_analysis: bool = False

class Page(BaseModel):
    page_index: int
    dimensions: Optional[Dict[str, float]] = None
    ocr_confidence: Optional[float] = None
    text: str
    blocks: List[Block] = []
    tables: List[Table] = []
    images: List[ImageInfo] = []

class CanonicalDocument(BaseModel):
    document_id: str
    document_type: str
    metadata: Dict[str, Any]
    pages: List[Page] = []
