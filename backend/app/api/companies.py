import os
import json
from fastapi import APIRouter
from app.config import settings
from app.core import success_response, error_response
from app.pipeline import JobManager, PipelineStatusManager

router = APIRouter()

@router.get("")
async def list_all_companies():
    from app.core.db import get_all_companies_summary
    from app.core import get_utc_now_iso
    
    summary = get_all_companies_summary()
    
    # Fallback to filesystem if DB has no runs but outputs exist
    if not summary and os.path.exists(settings.OUTPUT_DIR):
        summary = []
        for item in os.listdir(settings.OUTPUT_DIR):
            item_path = os.path.join(settings.OUTPUT_DIR, item)
            if os.path.isdir(item_path):
                # Count files in parsed directory
                parsed_dir = os.path.join(item_path, "parsed")
                docs_count = 0
                if os.path.exists(parsed_dir) and os.path.isdir(parsed_dir):
                    docs_count = len([f for f in os.listdir(parsed_dir) if f.endswith(".json")])
                
                summary.append({
                    "company_id": item,
                    "job_id": "none",
                    "status": "COMPLETED",
                    "updated_at": get_utc_now_iso(),
                    "file_count": docs_count
                })
    
    return success_response(summary)


@router.get("/{company_id}")
async def get_company_metadata(company_id: str):
    clean_company_id = company_id.strip()
    if not clean_company_id:
        return error_response(["company_id cannot be empty."], status_code=400)

    company_dir = os.path.join(settings.OUTPUT_DIR, clean_company_id)
    if not os.path.exists(company_dir):
        return error_response([f"Company '{clean_company_id}' not found."], status_code=404)

    # 1. Counts of parsed files
    parsed_dir = os.path.join(company_dir, "parsed")
    docs_count = 0
    if os.path.exists(parsed_dir) and os.path.isdir(parsed_dir):
        docs_count = len([f for f in os.listdir(parsed_dir) if f.endswith(".json")])

    # 2. Count of artifacts
    manifest_path = os.path.join(company_dir, "manifests", "artifacts_manifest.json")
    artifacts_count = 0
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
                artifacts_count = len(manifest_data.get("artifacts", []))
        except Exception:
            pass

    # If manifest not found, scan directory manually
    if artifacts_count == 0:
        for root, dirs, files in os.walk(company_dir):
            for file in files:
                if file != "artifacts_manifest.json":
                    artifacts_count += 1

    # 3. Retrieve Pipeline job status details
    latest_job_id = "none"
    latest_status = "idle"
    latest_run = "never"
    
    # Try local job manager memory first
    latest_job = JobManager.get_jobs_by_company(clean_company_id)
    if latest_job:
        latest_job_id = latest_job.get("job_id")
        latest_status = latest_job.get("status")
        latest_run = latest_job.get("updated_at")
    else:
        # Check if pipeline_status.json exists on disk
        status_file = os.path.join(company_dir, "manifests", "pipeline_status.json")
        if os.path.exists(status_file):
            try:
                with open(status_file, "r", encoding="utf-8") as f:
                    status_data = json.load(f)
                    latest_job_id = status_data.get("job_id", "none")
                    latest_status = status_data.get("status", "idle")
                    latest_run = status_data.get("updated_at", "never")
            except Exception:
                pass

    return success_response({
        "company_id": clean_company_id,
        "pipeline_status": latest_status.lower(),
        "parsed": os.path.exists(parsed_dir) and docs_count > 0,
        "extracted": os.path.exists(os.path.join(company_dir, "extracted")),
        "verified": os.path.exists(os.path.join(company_dir, "verification")),
        "readiness": os.path.exists(os.path.join(company_dir, "readiness")),
        "documents": docs_count,
        "artifacts": artifacts_count,
        "latest_job": latest_job_id,
        "latest_status": latest_status,
        "latest_run": latest_run
    })
