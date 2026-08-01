import threading
import uuid
import datetime
from enum import Enum
from typing import Dict, Any, Optional

class JobStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class JobManager:
    _lock = threading.Lock()
    _jobs: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def create_job(cls, company_id: str) -> str:
        """
        Creates a new job with a unique UUIDv4.
        """
        job_id = str(uuid.uuid4())
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with cls._lock:
            cls._jobs[job_id] = {
                "job_id": job_id,
                "company_id": company_id,
                "status": JobStatus.ACCEPTED,
                "created_at": now,
                "updated_at": now
            }
        return job_id

    @classmethod
    def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a job by its unique ID.
        """
        with cls._lock:
            return cls._jobs.get(job_id)

    @classmethod
    def update_job_status(cls, job_id: str, status: JobStatus) -> None:
        """
        Updates the job status and records the updated timestamp.
        """
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with cls._lock:
            if job_id in cls._jobs:
                cls._jobs[job_id]["status"] = status
                cls._jobs[job_id]["updated_at"] = now

    @classmethod
    def get_jobs_by_company(cls, company_id: str) -> Dict[str, Any]:
        """
        Retrieves jobs list or active job details for a given company.
        """
        with cls._lock:
            company_jobs = [j for j in cls._jobs.values() if j["company_id"] == company_id]
            if not company_jobs:
                return {}
            # Sort by updated_at descending
            company_jobs.sort(key=lambda x: x["updated_at"], reverse=True)
            return company_jobs[0]
