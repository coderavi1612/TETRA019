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

    clean_company_id = company_id.strip()
    if not clean_company_id:
        return error_response(["company_id cannot be empty."], status_code=400)

    readiness_dir = os.path.join(settings.OUTPUT_DIR, clean_company_id, "readiness")
    
    # Fallback to legacy path if standard doesn't exist
    if not os.path.exists(readiness_dir):
        readiness_dir = os.path.join(settings.OUTPUT_DIR, clean_company_id, "reports")

    if not os.path.exists(readiness_dir) or not os.path.isdir(readiness_dir):
        return error_response([f"Readiness reports not found for company '{clean_company_id}'."], status_code=404)

    summary = {}
    executive = {}
    questions = []

    # Helper function to load JSON files
    def load_json(filename):
        path = os.path.join(readiness_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    summary = load_json("readiness_summary.json")
    executive = load_json("executive_summary.json")
    questions_data = load_json("follow_up_questions.json")
    # Questions might be wrapped in a dict or direct list
    if isinstance(questions_data, dict):
        questions = questions_data.get("questions", [])
    elif isinstance(questions_data, list):
        questions = questions_data
    else:
        questions = []

    # Map dynamic downloads list
    downloads = []
    
    # Check what files exist to build downloads metadata dynamically
    downloadable_files = [
        ("executive_summary.pdf", "Executive Summary (PDF)", "pdf"),
        ("readiness_summary.pdf", "Readiness Summary (PDF)", "pdf"),
        ("follow_up_questions.pdf", "Follow-up Questions (PDF)", "pdf"),
        ("readiness_report.md", "Readiness Report (Markdown)", "md")
    ]
    
    for filename, display_name, file_type in downloadable_files:
        path = os.path.join(readiness_dir, filename)
        if os.path.exists(path):
            # Resolve category (either readiness or reports depending on folder lookup)
            category = "readiness" if "readiness" in readiness_dir else "logs" # fallback or standard
            if category == "logs":
                # Let's map it safely
                category = "readiness"
            
            downloads.append({
                "name": display_name,
                "type": file_type,
                "url": f"/api/v1/files/{clean_company_id}/{category}/{filename}"
            })

    return success_response({
        "summary": summary,
        "executive": executive,
        "questions": questions,
        "downloads": downloads,
        "status": "READY"
    })
