import os
import json
from typing import Dict, Any, List

class ReportContextBuilder:
    @staticmethod
    def build_and_save_context(company_id: str, outputs_dir: str) -> Dict[str, Any]:
        """
        Loads Milestone 4 outputs, compiles report_context.json, and saves it.
        """
        verification_dir = os.path.join(outputs_dir, company_id, "verification")
        
        # Default structures if files do not exist
        summary = {}
        issues = []
        matrix = {"matrix": {}}
        
        summary_path = os.path.join(verification_dir, "comparison_summary.json")
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)
                
        issues_path = os.path.join(verification_dir, "issues.json")
        if os.path.exists(issues_path):
            with open(issues_path, "r", encoding="utf-8") as f:
                issues_data = json.load(f)
                issues = issues_data.get("issues", []) if isinstance(issues_data, dict) else issues_data
                
        matrix_path = os.path.join(verification_dir, "comparison_matrix.json")
        if os.path.exists(matrix_path):
            with open(matrix_path, "r", encoding="utf-8") as f:
                matrix = json.load(f)

        # Get list of fields with issues
        issue_fields = {issue.get("field") for issue in issues if issue.get("field")}
        
        # Identify matched fields
        matched_fields = []
        matrix_data = matrix.get("matrix", {})
        for field, doc_vals in matrix_data.items():
            if field not in issue_fields:
                # Compile values for matched fields
                values = {dtype: val_obj.get("value") for dtype, val_obj in doc_vals.items()}
                matched_fields.append({
                    "field": field,
                    "documents": list(doc_vals.keys()),
                    "values": values
                })

        # Build clean issues summary
        issues_summary = []
        for issue in issues:
            issues_summary.append({
                "issue_id": issue.get("id"),
                "field": issue.get("field"),
                "classification": issue.get("classification"),
                "severity": issue.get("severity"),
                "description": issue.get("description"),
                "documents": issue.get("documents", [])
            })

        # Try to find the company name from matrix
        company_name = None
        company_legal_name_data = matrix.get("matrix", {}).get("CompanyLegalName", {})
        if company_legal_name_data:
            for doc_name, val_obj in company_legal_name_data.items():
                if val_obj and val_obj.get("value"):
                    company_name = val_obj.get("value")
                    break

        context_obj = {
            "company_id": company_id,
            "company_name": company_name,
            "statistics": {
                "documents_compared": summary.get("documents_compared", 0),
                "canonical_fields": summary.get("canonical_fields", 0),
                "matched": summary.get("matched", 0),
                "close_matches": summary.get("close_matches", 0),
                "verified_mismatches": summary.get("verified_mismatches", 0),
                "missing_information": summary.get("missing_information", 0),
                "unresolved_inconsistencies": summary.get("unresolved_inconsistencies", 0)
            },
            "issues_summary": issues_summary,
            "matched_fields": matched_fields
        }

        # Save to outputs/{company_id}/readiness/report_context.json
        company_outputs_dir = os.path.join(outputs_dir, company_id)
        readiness_dir = os.path.join(company_outputs_dir, "readiness")
        os.makedirs(readiness_dir, exist_ok=True)
        context_path = os.path.join(readiness_dir, "report_context.json")
        with open(context_path, "w", encoding="utf-8") as f:
            json.dump(context_obj, f, indent=2)

        return context_obj
