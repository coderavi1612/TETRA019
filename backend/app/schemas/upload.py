from pydantic import BaseModel
from typing import List

class UploadedFileResponse(BaseModel):
    filename: str
    size_bytes: int
    file_type: str
    status: str

class UploadSuccessResponse(BaseModel):
    company_id: str
    files: List[UploadedFileResponse]
    message: str
