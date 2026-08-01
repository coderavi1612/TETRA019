import unittest
import os
import json
import shutil
from app.readiness.orchestrator import ReadinessOrchestrator
from app.verification.orchestrator import VerificationOrchestrator
from app.config import settings

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

        # Synthesize readiness_summary.json inside golden verification directory if missing
        verification_dir = os.path.join(self.sample_company_dir, "verification")
        readiness_summary_path = os.path.join(verification_dir, "readiness_summary.json")
        if not os.path.exists(readiness_summary_path) and os.path.exists(verification_dir):
            with open(os.path.join(verification_dir, "issues.json"), "r", encoding="utf-8") as f:
                issues_data = json.load(f)
                issues = issues_data.get("issues", []) if isinstance(issues_data, dict) else issues_data
            with open(os.path.join(verification_dir, "comparison_summary.json"), "r", encoding="utf-8") as f:
                summary = json.load(f)
            
            from app.readiness.scoring import ReadinessScoringEngine
            scoring = ReadinessScoringEngine.calculate_score_and_status(issues, summary)
            
            import datetime
            now_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "") + "Z"
            
            readiness_payload = {
                "metadata": {
                    "schema_version": "1.0.0",
                    "pipeline_version": "1.0.0",
                    "created_by": "Duelens Golden Test Helper",
                    "generated_at": now_str
                },
                "company_id": "sample_company",
                "overall_status": scoring.get("overall_status", "READY"),
                "readiness_score": scoring.get("readiness_score", 88),
                "documents_reviewed": ["pitch_deck", "historical_financial_statements", "mis", "financial_projections", "cap_table"],
                "verified_matches": summary.get("matched", 0),
                "verified_mismatches": summary.get("verified_mismatches", 0),
                "missing_information": summary.get("missing_information", 0),
                "unresolved_inconsistencies": summary.get("unresolved_inconsistencies", 0),
                "strengths": [],
                "risks": [],
                "next_steps": [],
                "executive_summary": ""
            }
            with open(readiness_summary_path, "w", encoding="utf-8") as f:
                json.dump(readiness_payload, f, indent=2)

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
                gen_data.pop("metadata", None)
            if isinstance(exp_data, dict):
                exp_data.pop("metadata", None)
                
            if isinstance(gen_data, dict) and isinstance(exp_data, dict):
                self.assertEqual(gen_data.keys(), exp_data.keys(), f"Mismatch in schema keys for {file}")
            self.assertEqual(gen_data, exp_data, f"JSON content mismatch in golden file: {file}")

    def test_pipeline_orchestrator(self):
        from app.pipeline.orchestrator import DuelensPipeline, PipelineStage
        # Run PARSE stage of the pipeline E2E on comp_test_abc
        # Since upload dir is needed, we ensure we test stage execution triggers
        res = DuelensPipeline.run("comp_test_abc", stage=PipelineStage.PARSE)
        self.assertEqual(res["company_id"], "comp_test_abc")
        self.assertIn("parse", res["results"])
