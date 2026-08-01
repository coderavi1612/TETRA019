from pydantic import BaseModel
from typing import List

class ParseResultFile(BaseModel):
    file_name: str
    document_type: str
    status: str
    blocks: int
    errors: List[str]

class ParseResponse(BaseModel):
    company_id: str
    documents_parsed: int
    files: List[ParseResultFile]
