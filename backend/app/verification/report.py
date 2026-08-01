import os
import json
import datetime
from typing import Dict, List, Any
from app.verification.schemas.issue import Issue, Evidence
from app.verification.schemas.verification import ComparisonSummary
from app.verification.schemas.comparison import ComparisonMatrix

class ReportBuilder:
    @staticmethod
    def save_reports(
        output_dir: str,
        company_id: str,
        summary: ComparisonSummary,
        issues: List[Issue],
        evidence_map: Dict[str, List[Evidence]],
        graph_data: Dict[str, Any],
        matrix: ComparisonMatrix,
        canonical_fields: List[str],
        scoring: Dict[str, Any],
        documents_reviewed: List[str]
    ) -> None:
        os.makedirs(output_dir, exist_ok=True)
        
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "") + "Z"
        metadata = {
            "schema_version": "1.0.0",
            "pipeline_version": "1.0.0",
            "created_by": "Duelens Verification Engine",
            "generated_at": now_str
        }

        # 1. Save comparison_summary.json
        summary_data = summary.model_dump()
        summary_data["metadata"] = metadata
        summary_path = os.path.join(output_dir, "comparison_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)

        # 2. Save issues.json
        issues_data = {
            "metadata": metadata,
            "issues": [issue.model_dump() for issue in issues]
        }
        issues_path = os.path.join(output_dir, "issues.json")
        with open(issues_path, "w", encoding="utf-8") as f:
            json.dump(issues_data, f, indent=2, default=str)

        # 3. Save evidence.json
        serialized_evidence = {
            comp_id: [e.model_dump() for e in evs]
            for comp_id, evs in evidence_map.items()
        }
        evidence_payload = {
            "metadata": metadata,
            "evidence": serialized_evidence
        }
        evidence_path = os.path.join(output_dir, "evidence.json")
        with open(evidence_path, "w", encoding="utf-8") as f:
            json.dump(evidence_payload, f, indent=2, default=str)

        # 4. Save verification_graph.json
        graph_payload = {
            "metadata": metadata,
            "graph": graph_data
        }
        graph_path = os.path.join(output_dir, "verification_graph.json")
        with open(graph_path, "w", encoding="utf-8") as f:
            json.dump(graph_payload, f, indent=2, default=str)

        # 5. Save comparison_matrix.json
        matrix_data = matrix.model_dump()
        matrix_data["metadata"] = metadata
        matrix_path = os.path.join(output_dir, "comparison_matrix.json")
        with open(matrix_path, "w", encoding="utf-8") as f:
            json.dump(matrix_data, f, indent=2, default=str)

        # 6. Save canonical_fields.json
        fields_payload = {
            "metadata": metadata,
            "canonical_fields": canonical_fields
        }
        fields_path = os.path.join(output_dir, "canonical_fields.json")
        with open(fields_path, "w", encoding="utf-8") as f:
            json.dump(fields_payload, f, indent=2)

        # 7. Save readiness_summary.json
        readiness_payload = {
            "metadata": metadata,
            "company_id": company_id,
            "overall_status": scoring.get("overall_status", "NOT_READY"),
            "readiness_score": scoring.get("readiness_score", 0),
            "documents_reviewed": documents_reviewed,
            "verified_matches": summary.matched,
            "verified_mismatches": summary.verified_mismatches,
            "missing_information": summary.missing_information,
            "unresolved_inconsistencies": summary.unresolved_inconsistencies,
            "strengths": [],
            "risks": [],
            "next_steps": [],
            "executive_summary": ""
        }
        readiness_path = os.path.join(output_dir, "readiness_summary.json")
        with open(readiness_path, "w", encoding="utf-8") as f:
            json.dump(readiness_payload, f, indent=2)
