from fastapi import APIRouter, HTTPException
from app.reasoning.orchestrator import ReasoningOrchestrator

router = APIRouter()

@router.post("/{company_id}")
async def run_reasoning_stage(company_id: str):
    try:
        clean_company_id = company_id.strip()
        result = ReasoningOrchestrator.run_reasoning(clean_company_id)
        return {
            "company_id": result["company_id"],
            "status": result["status"],
            "cache_hit": result["cache_hit"],
            "report_summary": {
                "semantic_conflicts_count": len(result["report"].get("semantic_conflicts", [])),
                "ownership_conflicts_count": len(result["report"].get("ownership_conflicts", [])),
                "investor_questions_count": len(result["report"].get("investor_questions", []))
            }
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Local consistency reasoning failed: {str(e)}")
