from fastapi import APIRouter, HTTPException
from app.verification.orchestrator import VerificationOrchestrator
from app.verification.schemas import VerifyApiResponse

router = APIRouter()

@router.post("/{company_id}", response_model=VerifyApiResponse)
async def verify_company(company_id: str):
    try:
        clean_company_id = company_id.strip()
        result = VerificationOrchestrator.run_verification(clean_company_id)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification run failed: {str(e)}")
