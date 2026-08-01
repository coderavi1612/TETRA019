from fastapi import APIRouter, HTTPException, status
from app.extractors.extractor import FactExtractor

router = APIRouter()

@router.post("/{company_id}")
async def extract_facts(company_id: str):
    clean_company_id = company_id.strip()
    if not clean_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="company_id cannot be empty or whitespace."
        )
        
    try:
        _, stats = FactExtractor.extract_company_facts(clean_company_id)
        return stats
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
