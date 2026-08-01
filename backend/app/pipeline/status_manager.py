import os
import json
import threading
import datetime
from typing import Dict, Any, Optional
from app.config import settings

class PipelineStatusManager:
    _lock = threading.Lock()
    _statuses: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def init_status(cls, job_id: str, company_id: str) -> None:
        """
        Initializes the status structure for a new pipeline job.
        """
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with cls._lock:
            cls._statuses[job_id] = {
                "job_id": job_id,
                "company_id": company_id,
                "status": "ACCEPTED",
                "current_stage": "none",
                "stages": [
                    {"name": "parse", "status": "idle", "duration_ms": 0},
                    {"name": "extract", "status": "idle", "duration_ms": 0},
                    {"name": "reason", "status": "idle", "duration_ms": 0},
                    {"name": "verify", "status": "idle", "duration_ms": 0},
                    {"name": "readiness", "status": "idle", "duration_ms": 0}
                ],
                "progress": 0,
                "started_at": now,
                "updated_at": now
            }

    @classmethod
    def update_stage(
        cls, 
        job_id: str, 
        stage_name: str, 
        stage_status: str, 
        duration_ms: int = 0,
        overall_status: str = None,
        error_msg: str = None
    ) -> None:
        """
        Updates the state and duration of a specific stage in the pipeline.
        Calculates and updates top-level progress.
        """
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with cls._lock:
            status_data = cls._statuses.get(job_id)
            if not status_data:
                return

            status_data["updated_at"] = now
            if overall_status:
                status_data["status"] = overall_status

            # Find and update specific stage
            stages = status_data["stages"]
            current_found = False
            for stage in stages:
                if stage["name"] == stage_name:
                    stage["status"] = stage_status
                    stage["duration_ms"] = duration_ms
                    current_found = True
            
            if not current_found:
                # Fallback appending new stage if it doesn't match defaults
                stages.append({
                    "name": stage_name,
                    "status": stage_status,
                    "duration_ms": duration_ms
                })

            if stage_status == "running":
                status_data["current_stage"] = stage_name
                status_data["status"] = "RUNNING"
            
            # Map progress based on completed stages count
            completed_count = sum(1 for s in stages if s["status"] == "completed")
            status_data["progress"] = int((completed_count / len(stages)) * 100)
            
            if error_msg:
                status_data["failed_stage"] = stage_name
                status_data["error"] = error_msg
                status_data["status"] = "FAILED"

    @classmethod
    def get_status(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves status details for a job.
        Checks memory registry first, then attempts disk read.
        """
        with cls._lock:
            if job_id in cls._statuses:
                return cls._statuses[job_id]

        # Scan filesystem for fallback lookup
        for company_id in os.listdir(settings.OUTPUT_DIR):
            company_dir = os.path.join(settings.OUTPUT_DIR, company_id)
            if not os.path.isdir(company_dir):
                continue
            
            status_path = os.path.join(company_dir, "manifests", "pipeline_status.json")
            if os.path.exists(status_path):
                try:
                    with open(status_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("job_id") == job_id:
                            # Cache back to memory
                            with cls._lock:
                                cls._statuses[job_id] = data
                            return data
                except Exception:
                    pass
        return None

    @classmethod
    def persist_status(cls, job_id: str, company_id: str) -> None:
        """
        Persists the current job status data to outputs/{company_id}/manifests/pipeline_status.json.
        """
        status_data = None
        with cls._lock:
            status_data = cls._statuses.get(job_id)
            if status_data:
                status_data_copy = json.loads(json.dumps(status_data))
            else:
                return

        manifests_dir = os.path.join(settings.OUTPUT_DIR, company_id, "manifests")
        os.makedirs(manifests_dir, exist_ok=True)
        status_file = os.path.join(manifests_dir, "pipeline_status.json")
        try:
            with open(status_file, "w", encoding="utf-8") as f:
                json.dump(status_data_copy, f, indent=2)
        except Exception:
            pass
