from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Cell(BaseModel):
    row: int
    col: int
    reference: str
    value: Optional[str] = None
    raw_value: Optional[Any] = None
    formula: Optional[str] = None
    number_format: Optional[str] = None
    currency: Optional[str] = None

class TableInfo(BaseModel):
    table_name: str
    cells: List[Cell] = []

class Sheet(BaseModel):
    sheet_name: str
    relationships: Dict[str, Any] = {}
    tables: List[TableInfo] = []

class WorkbookMetadata(BaseModel):
    sheet_count: int
    defined_names: List[str] = []
    hidden_sheets: List[str] = []
    active_sheet: Optional[str] = None

class CanonicalWorkbook(BaseModel):
    document_id: str
    metadata: Dict[str, Any]
    workbook_metadata: WorkbookMetadata
    sheets: List[Sheet] = []
