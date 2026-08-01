import unittest
import os
import json
import tempfile
from typing import Dict, Any

from app.readiness.scoring import ReadinessScoringEngine
from app.readiness.ai.repair import JSONReadinessRepairer
from app.readiness.ai.validator import JSONSchemaValidator
from app.readiness.schemas.readiness import ExecutiveSummary
from app.readiness.markdown import MarkdownReportGenerator
from app.readiness.pdf import PdfReportAssembler

class TestReadinessEngine(unittest.TestCase):
    def test_scoring_and_status(self):
        # 1. Test perfect score
        issues = []
        stats = {"matched": 10, "verified_mismatches": 0, "missing_information": 0, "unresolved_inconsistencies": 0}
        res = ReadinessScoringEngine.calculate_score_and_status(issues, stats)
        self.assertEqual(res["readiness_score"], 100)
        self.assertEqual(res["overall_status"], "READY")

        # 2. Test verified mismatch deductions (CRITICAL, HIGH, MEDIUM, LOW)
        issues = [
            {"classification": "Verified Mismatch", "severity": "CRITICAL", "field": "Ownership.FounderA"},
            {"classification": "Verified Mismatch", "severity": "HIGH", "field": "Revenue.FY24"},
            {"classification": "Verified Mismatch", "severity": "MEDIUM", "field": "EBITDA.FY24"},
            {"classification": "Verified Mismatch", "severity": "LOW", "field": "CashBalance.FY24"}
        ]
        res = ReadinessScoringEngine.calculate_score_and_status(issues, stats)
        # score = 100 - 20 (critical) - 10 (high) - 5 (medium) - 2 (low) = 63
        self.assertEqual(res["readiness_score"], 63)
        # Capped at NEEDS_MAJOR_REVIEW due to critical mismatch override
        self.assertEqual(res["overall_status"], "NEEDS_MAJOR_REVIEW")

        # 3. Test multiple critical issues -> NOT_READY status override
        issues = [
            {"classification": "Verified Mismatch", "severity": "CRITICAL", "field": "Ownership.FounderA"},
            {"classification": "Unresolved Inconsistency", "severity": "CRITICAL", "field": "CompanyLegalName"},
            {"classification": "Missing Information", "severity": "CRITICAL", "field": "FundingAskAmount"}
        ]
        res = ReadinessScoringEngine.calculate_score_and_status(issues, stats)
        self.assertEqual(res["overall_status"], "NOT_READY")

    def test_json_repair(self):
        # Valid JSON
        self.assertEqual(JSONReadinessRepairer.repair_json('{"test": 123}'), {"test": 123})
        # Wrapped in Markdown tags
        self.assertEqual(JSONReadinessRepairer.repair_json('```json\n{"test": 123}\n```'), {"test": 123})
        # Wrapped in raw text
        self.assertEqual(JSONReadinessRepairer.repair_json('Here is response: {"test": 123} in details.'), {"test": 123})

    def test_schema_validator(self):
        valid_data = {
            "company_overview": "Zestful Tech",
            "overall_readiness": "Minor changes required.",
            "top_risks": ["Revenue mismatch"],
            "top_strengths": ["Strong assets"],
            "critical_issues": [],
            "immediate_actions": ["Align values"],
            "investor_readiness": "Ready with minor changes."
        }
        validated = JSONSchemaValidator.validate_schema(valid_data, ExecutiveSummary)
        self.assertEqual(validated.company_overview, "Zestful Tech")

        # Missing field
        invalid_data = {
            "company_overview": "Zestful Tech"
        }
        with self.assertRaises(ValueError):
            JSONSchemaValidator.validate_schema(invalid_data, ExecutiveSummary)

    def test_markdown_and_pdf_generation(self):
        reports_json = {
            "executive_summary": {
                "company_overview": "Overview text",
                "overall_readiness": "Readiness text",
                "top_risks": ["Risk 1"],
                "top_strengths": ["Strength 1"],
                "critical_issues": [],
                "immediate_actions": [],
                "investor_readiness": "Readiness deal text"
            },
            "readiness_summary": {
                "company_id": "test_company",
                "overall_status": "READY_WITH_MINOR_CHANGES",
                "readiness_score": 85,
                "documents_reviewed": ["pitch_deck", "historical_financial_statements"],
                "verified_matches": 5,
                "verified_mismatches": 1,
                "missing_information": 1,
                "unresolved_inconsistencies": 0,
                "strengths": ["Matched legal names"],
                "risks": ["Mismatch in FY24 revenue"],
                "next_steps": ["Verify round size"],
                "executive_summary": "General evaluation summary."
            },
            "follow_up_questions": [
                {
                    "question_id": "QST-000001",
                    "priority": "HIGH",
                    "related_issue": "CMP-000001",
                    "question": "Why is the revenue different?",
                    "why_it_matters": "Core metrics are required to match.",
                    "required_document": "historical_financial_statements",
                    "expected_answer": "Reconciled accounts."
                }
            ],
            "inconsistency_report": [
                {
                    "issue_id": "CMP-000001",
                    "classification": "Verified Mismatch",
                    "severity": "HIGH",
                    "canonical_field": "Revenue.FY24",
                    "documents": ["pitch_deck", "historical_financial_statements"],
                    "authoritative_document": "historical_financial_statements",
                    "authoritative_value": 1000000,
                    "description": "Revenue difference detected.",
                    "business_impact": "Loss of VC confidence.",
                    "recommended_action": "Reconcile Pitch Deck values.",
                    "evidence": [
                        {
                            "document": "pitch_deck",
                            "value": 1200000,
                            "canonical_path": "Revenue.FY24",
                            "source_block_id": "pitch_deck_block_01",
                            "page": None,
                            "slide": 4,
                            "sheet": None,
                            "snippet": "Revenue: 1.2M"
                        }
                    ]
                }
            ]
        }

        # Generate Markdowns
        markdowns = MarkdownReportGenerator.generate_markdown("test_company", reports_json)
        self.assertIn("readiness_summary.md", markdowns)
        self.assertIn("executive_summary.md", markdowns)
        self.assertIn("follow_up_questions.md", markdowns)
        self.assertIn("inconsistency_report.md", markdowns)

        # Generate PDFs (using temp directory)
        with tempfile.TemporaryDirectory() as temp_dir:
            PdfReportAssembler.generate_all_pdfs("test_company", reports_json, temp_dir)
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "readiness_summary.pdf")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "executive_summary.pdf")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "follow_up_questions.pdf")))

    def test_gemini_reasoning_client(self):
        from app.reasoning.gemini import GeminiReasoningClient
        client = GeminiReasoningClient()
        self.assertEqual(client.model, "gemini-2.5-flash-lite")
        res = client.generate_reasoning({"test": "data"})
        self.assertEqual(res["status"], "FAILED")
        self.assertFalse(res["reasoning_available"])
