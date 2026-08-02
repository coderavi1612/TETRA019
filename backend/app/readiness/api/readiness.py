from fastapi import APIRouter, HTTPException
from app.readiness.orchestrator import ReadinessOrchestrator
from app.readiness.schemas.readiness import VerifyApiResponse

router = APIRouter()

@router.post("/{company_id}", response_model=VerifyApiResponse)
async def generate_readiness_report(company_id: str):
    try:
        clean_company_id = company_id.strip()
        result = ReadinessOrchestrator.run_readiness_pipeline(clean_company_id)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Readiness reporting run failed: {str(e)}")

@router.get("/{company_id}/results")
async def get_readiness_results(company_id: str):
    import os
    import json
    from app.config import settings
    from app.core import success_response, error_response

    from app.core.db import get_pipeline_outputs_from_db

    clean_company_id = company_id.strip()
    if not clean_company_id:
        return error_response(["company_id cannot be empty."], status_code=400)

    db_outputs = get_pipeline_outputs_from_db(clean_company_id)
    readiness_dir = os.path.join(settings.OUTPUT_DIR, clean_company_id, "readiness")
    if not os.path.exists(readiness_dir):
        readiness_dir = os.path.join(settings.OUTPUT_DIR, clean_company_id, "reports")

    # If neither disk folder nor DB records exist, return 404
    has_db_readiness = any(cat == "readiness" for cat, _ in db_outputs.keys())
    if not os.path.exists(readiness_dir) and not has_db_readiness:
        return error_response([f"Readiness reports not found for company '{clean_company_id}'."], status_code=404)

    summary = {}
    executive = {}
    questions = []

    # Helper function to load JSON files from disk or DB
    def load_json(filename):
        path = os.path.join(readiness_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Fallback to DB
        db_item = db_outputs.get(("readiness", filename.lower()))
        if db_item and db_item.get("text_content"):
            try:
                return json.loads(db_item["text_content"])
            except Exception:
                pass
        return {}

    summary = load_json("readiness_summary.json")
    executive = load_json("executive_summary.json")
    questions_data = load_json("follow_up_questions.json")
    
    if isinstance(questions_data, dict):
        questions = questions_data.get("questions", [])
    elif isinstance(questions_data, list):
        questions = questions_data
    else:
        questions = []

    # Map dynamic downloads list
    downloads = []
    
    downloadable_files = [
        ("executive_summary.pdf", "Executive Summary (PDF)", "pdf"),
        ("readiness_summary.pdf", "Readiness Summary (PDF)", "pdf"),
        ("follow_up_questions.pdf", "Follow-up Questions (PDF)", "pdf"),
        ("readiness_report.md", "Readiness Report (Markdown)", "md")
    ]
    
    for filename, display_name, file_type in downloadable_files:
        path = os.path.join(readiness_dir, filename)
        has_file = os.path.exists(path) or ("readiness", filename.lower()) in db_outputs
        if has_file:
            downloads.append({
                "name": display_name,
                "type": file_type,
                "url": f"/api/v1/files/{clean_company_id}/readiness/{filename}"
            })

    return success_response({
        "summary": summary,
        "executive": executive,
        "questions": questions,
        "downloads": downloads,
        "status": "READY"
    })
