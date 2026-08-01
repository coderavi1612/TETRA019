from fastapi import APIRouter, HTTPException
from app.readiness.orchestrator import ReadinessOrchestrator
from app.readiness.schemas.readiness import VerifyApiResponse

router = APIRouter()

@router.post("/{company_id}", response_model=VerifyApiResponse)
async def generate_report_stage(company_id: str):
    try:
        clean_company_id = company_id.strip()
        result_dict = ReadinessOrchestrator.run_readiness_pipeline(clean_company_id)
        return VerifyApiResponse(**result_dict)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Executive report generation failed: {str(e)}")
