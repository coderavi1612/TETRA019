from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
from app.extractors.extractor import FactExtractor

router = APIRouter()

class ExtractionResponse(BaseModel):
    company_id: str
    documents_processed: int
    documents_generated: int
    cache_hits: int
    cache_misses: int
    processing_time_ms: int
    verification_status: str
    failed_documents: List[str]

@router.post("/{company_id}", response_model=ExtractionResponse)
async def extract_facts(company_id: str):
    clean_company_id = company_id.strip()
    if not clean_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="company_id cannot be empty or whitespace."
        )
        
    try:
        _, stats = FactExtractor.extract_company_facts(clean_company_id)
        return ExtractionResponse(**stats)
    except FileNotFoundError as fnf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fnf)
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during fact extraction: {str(e)}"
        )
