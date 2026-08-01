import json
import os
import uuid
import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.pipeline.job_manager import JobManager, JobStatus
from app.pipeline.status_manager import PipelineStatusManager
from app.pipeline.orchestrator import DuelensPipeline
from app.core import success_response, error_response, request_id_var

class TestMilestone6Backend(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.company_id = "comp_test_abc"

    def test_response_envelope_layout(self):
        # Directly test core helpers
        token = request_id_var.set("test-req-123")
        try:
            suc = success_response(data={"ok": True}, meta={"page": 1}, warnings=["warn-1"])
            self.assertTrue(suc["success"])
            self.assertEqual(suc["api_version"], "v1")
            self.assertEqual(suc["request_id"], "test-req-123")
            self.assertEqual(suc["data"], {"ok": True})
            self.assertEqual(suc["meta"], {"page": 1})
            self.assertEqual(suc["warnings"], ["warn-1"])
            self.assertEqual(suc["errors"], [])
            self.assertIn("timestamp", suc)
        finally:
            request_id_var.reset(token)

    def test_request_id_middleware(self):
        # Call root endpoint and check request ID injection
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
        # Check header
        req_id_header = response.headers.get("X-Request-ID")
        self.assertIsNotNone(req_id_header)
        # Assert is a valid UUIDv4
        val = uuid.UUID(req_id_header, version=4)
        self.assertEqual(str(val), req_id_header)

    def test_job_manager_lifecycle(self):
        # Create job
        job_id = JobManager.create_job("test-comp")
        self.assertIsNotNone(job_id)
        # Assert job_id is a valid UUIDv4
        val = uuid.UUID(job_id, version=4)
        self.assertEqual(str(val), job_id)

        # Get job
        job = JobManager.get_job(job_id)
        self.assertIsNotNone(job)
        self.assertEqual(job["status"], JobStatus.ACCEPTED)

        # Update status
        JobManager.update_job_status(job_id, JobStatus.RUNNING)
        job = JobManager.get_job(job_id)
        self.assertEqual(job["status"], JobStatus.RUNNING)

        # Get latest job by company
        latest = JobManager.get_jobs_by_company("test-comp")
        self.assertEqual(latest["job_id"], job_id)

    def test_pipeline_status_manager(self):
        job_id = "test-job-id"
        PipelineStatusManager.init_status(job_id, "test-comp")
        
        status = PipelineStatusManager.get_status(job_id)
        self.assertEqual(status["job_id"], job_id)
        self.assertEqual(status["status"], "ACCEPTED")

        PipelineStatusManager.update_stage(job_id, "parse", "completed", duration_ms=250)
        status = PipelineStatusManager.get_status(job_id)
        self.assertEqual(status["progress"], 20)  # 1/5 completed
        
        # Verify stages list contains updated parse stage
        stages_map = {s["name"]: s for s in status["stages"]}
        self.assertEqual(stages_map["parse"]["status"], "completed")
        self.assertEqual(stages_map["parse"]["duration_ms"], 250)

    def test_pipeline_async_execution_route(self):
        # Trigger POST /pipeline/{company_id}
        response = self.client.post(f"/api/v1/pipeline/{self.company_id}")
        self.assertEqual(response.status_code, 200)
        
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["status"], "ACCEPTED")
        job_id = body["data"]["job_id"]
        
        # Verify job_id is valid UUIDv4
        self.assertEqual(str(uuid.UUID(job_id, version=4)), job_id)

    def test_path_traversal_protection(self):
        # Inject path traversal into filename streaming
        response = self.client.get(f"/api/v1/files/{self.company_id}/parsed/../../main.py")
        # Assert access denied (Forbidden 403, Bad Request 400, or Not Found 404 depending on client URL resolution)
        self.assertIn(response.status_code, [403, 400, 404])

    def test_invalid_category_protection(self):
        response = self.client.get(f"/api/v1/files/{self.company_id}/invalid_cat/somefile.json")
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertFalse(body["success"])
        self.assertIn("Invalid artifact category requested.", body["errors"])

    def test_artifacts_manifest_generation(self):
        from app.pipeline.orchestrator import PipelineStage
        res = DuelensPipeline.run(self.company_id, stage=PipelineStage.PARSE) # target parse stage
        DuelensPipeline.generate_artifacts_manifest(self.company_id)

        # Retrieve artifacts metadata endpoint
        response = self.client.get(f"/api/v1/companies/{self.company_id}/artifacts")
        self.assertEqual(response.status_code, 200)
        
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["manifest_version"], "1.0")
        self.assertEqual(body["data"]["company_id"], self.company_id)
        
        artifacts_list = body["data"]["artifacts"]
        self.assertTrue(isinstance(artifacts_list, list))
        if len(artifacts_list) > 0:
            item = artifacts_list[0]
            self.assertIn("name", item)
            self.assertIn("category", item)
            self.assertIn("mime_type", item)
            self.assertIn("size", item)
            self.assertIn("download_url", item)
            self.assertIn("generated_at", item)
            self.assertIn("stage", item)
