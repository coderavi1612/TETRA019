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
    warnings: List[str] = []
    errors: List[str] = []

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

@router.get("/{company_id}/documents")
async def get_all_extracted_documents(company_id: str):
    import os
    import json
    from app.config import settings
    from app.core import success_response, error_response

    clean_company_id = company_id.strip()
    if not clean_company_id:
        return error_response(["company_id cannot be empty."], status_code=400)

    extracted_dir = os.path.join(settings.OUTPUT_DIR, clean_company_id, "extracted")
    
    # Fallback to legacy path if standard doesn't exist
    if not os.path.exists(extracted_dir):
        extracted_dir = os.path.join(settings.OUTPUT_DIR, clean_company_id, "reports")

    if not os.path.exists(extracted_dir) or not os.path.isdir(extracted_dir):
        return error_response([f"Extracted documents not found for company '{clean_company_id}'."], status_code=404)

    documents = {}
    mapping = {
        "pitch_deck.json": "pitch_deck",
        "historical_financial_statements.json": "historical_financial_statements",
        "monthly_mis_report.json": "mis",
        "mis_report.json": "mis",
        "mis.json": "mis",
        "financial_projections.json": "financial_projections",
        "cap_table.json": "cap_table"
    }

    for filename in os.listdir(extracted_dir):
        if filename in mapping:
            key = mapping[filename]
            path = os.path.join(extracted_dir, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    documents[key] = json.load(f)
            except Exception:
                pass

    return success_response({"documents": documents})
