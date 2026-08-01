from fastapi import APIRouter, BackgroundTasks, Query
from typing import Optional
from app.core import success_response, error_response
from app.pipeline import DuelensPipeline, JobManager, PipelineStatusManager, JobStatus

router = APIRouter()

@router.post("/{company_id}")
async def start_pipeline(company_id: str, background_tasks: BackgroundTasks):
    clean_company_id = company_id.strip()
    if not clean_company_id:
        return error_response(["company_id cannot be empty."], status_code=400)

    # Create Job and Init Status
    job_id = JobManager.create_job(clean_company_id)
    PipelineStatusManager.init_status(job_id, clean_company_id)

    # Spawn asynchronous runner
    background_tasks.add_task(
        DuelensPipeline.run,
        company_id=clean_company_id,
        job_id=job_id
    )

    return success_response({
        "job_id": job_id,
        "company_id": clean_company_id,
        "status": JobStatus.ACCEPTED
    }, meta={"detail": "Pipeline execution started in background."})

@router.get("/{company_id}/status")
async def get_pipeline_status(
    company_id: str,
    job_id: Optional[str] = Query(None, description="Optional specific job ID to check")
):
    clean_company_id = company_id.strip()
    if not clean_company_id:
        return error_response(["company_id cannot be empty."], status_code=400)

    target_job_id = job_id
    if not target_job_id:
        # Fallback: get latest job for this company
        latest_job = JobManager.get_jobs_by_company(clean_company_id)
        if latest_job:
            target_job_id = latest_job.get("job_id")

    if not target_job_id:
        # If no active jobs, check if there's a persistent pipeline status file
        # by building a mock idle state or scanning
        return success_response({
            "job_id": "none",
            "company_id": clean_company_id,
            "status": "idle",
            "current_stage": "none",
            "stages": [
                {"name": "parse", "status": "idle", "duration_ms": 0},
                {"name": "extract", "status": "idle", "duration_ms": 0},
                {"name": "verify", "status": "idle", "duration_ms": 0},
                {"name": "readiness", "status": "idle", "duration_ms": 0}
            ],
            "progress": 0
        })

    status_data = PipelineStatusManager.get_status(target_job_id)
    if not status_data:
        return error_response([f"Pipeline status not found for job_id '{target_job_id}'."], status_code=404)

    return success_response(status_data)
