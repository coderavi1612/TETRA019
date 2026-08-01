import unittest
import os
import json
import shutil
from app.readiness.orchestrator import ReadinessOrchestrator

class TestGoldenReadiness(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.golden_dir = os.path.join(self.base_dir, "golden")
        self.sample_company_dir = os.path.join(self.golden_dir, "sample_company")
        self.expected_dir = os.path.join(self.sample_company_dir, "expected")
        self.reports_dir = os.path.join(self.sample_company_dir, "readiness")
        
        # Clean up old reports if they exist
        if os.path.exists(self.reports_dir):
            shutil.rmtree(self.reports_dir)

    def test_golden_run(self):
        # Run E2E pipeline targeting golden outputs directory
        res = ReadinessOrchestrator.run_readiness_pipeline("sample_company", outputs_dir=self.golden_dir)
        
        self.assertEqual(res["company_id"], "sample_company")
        self.assertEqual(res["validation_status"], "PASS")

        # Verify generated reports exist
        generated_json_files = [
            "readiness_summary.json",
            "executive_summary.json",
            "follow_up_questions.json",
            "inconsistency_report.json"
        ]
        
        for file in generated_json_files:
            path = os.path.join(self.reports_dir, file)
            self.assertTrue(os.path.exists(path), f"Generated file not found: {file}")

        # Populate expected directory on first run (bootstrapping)
        if not os.path.exists(self.expected_dir) or not os.listdir(self.expected_dir):
            os.makedirs(self.expected_dir, exist_ok=True)
            for file in generated_json_files:
                shutil.copy(os.path.join(self.reports_dir, file), os.path.join(self.expected_dir, file))
            print("\n[GOLDEN BOOTSTRAP] Expected directory populated with generated reports.")
            return

        # Assert outputs match expected goldens exactly
        for file in generated_json_files:
            gen_path = os.path.join(self.reports_dir, file)
            exp_path = os.path.join(self.expected_dir, file)
            
            with open(gen_path, "r", encoding="utf-8") as f:
                gen_data = json.load(f)
            with open(exp_path, "r", encoding="utf-8") as f:
                exp_data = json.load(f)
                
            if isinstance(gen_data, dict):
                self.assertEqual(gen_data.keys(), exp_data.keys(), f"Mismatch in schema keys for {file}")
            self.assertEqual(gen_data, exp_data, f"JSON content mismatch in golden file: {file}")

    def test_pipeline_orchestrator(self):
        from app.pipeline.orchestrator import DuelensPipeline, PipelineStage
        # Run PARSE stage of the pipeline E2E on comp_test_abc
        # Since upload dir is needed, we ensure we test stage execution triggers
        res = DuelensPipeline.run("comp_test_abc", stage=PipelineStage.PARSE)
        self.assertEqual(res["company_id"], "comp_test_abc")
        self.assertIn("parse", res["results"])
