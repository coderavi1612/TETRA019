import os
import json
from typing import Dict, List, Any
from app.verification.schemas.issue import Issue, Evidence
from app.verification.schemas.verification import ComparisonSummary

class ReportBuilder:
    @staticmethod
    def save_reports(
        output_dir: str,
        summary: ComparisonSummary,
        issues: List[Issue],
        evidence_map: Dict[str, List[Evidence]],
        graph_data: Dict[str, Any]
    ) -> None:
        os.makedirs(output_dir, exist_ok=True)
        
        summary_path = os.path.join(output_dir, "comparison_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary.model_dump(), f, indent=2)

        issues_path = os.path.join(output_dir, "issues.json")
        with open(issues_path, "w", encoding="utf-8") as f:
            json.dump([issue.model_dump() for issue in issues], f, indent=2, default=str)

        serialized_evidence = {
            comp_id: [e.model_dump() for e in evs]
            for comp_id, evs in evidence_map.items()
        }
        evidence_path = os.path.join(output_dir, "evidence.json")
        with open(evidence_path, "w", encoding="utf-8") as f:
            json.dump(serialized_evidence, f, indent=2, default=str)

        graph_path = os.path.join(output_dir, "verification_graph.json")
        with open(graph_path, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2, default=str)
