import os
from typing import Dict, Any, List
from app.readiness.schemas.readiness import (
    EvidenceEntry,
    InconsistencyReportEntry,
    FollowUpQuestion,
    ReadinessSummary,
    ExecutiveSummary
)

class ReportAssembler:
    @staticmethod
    def assemble_reports(
        company_id: str,
        verification_issues: List[Dict[str, Any]],
        documents_reviewed: List[str],
        stats: Dict[str, Any],
        scoring_results: Dict[str, Any],
        ai_narratives: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assembles report models from structured inputs and AI results.
        """
        # 1. Inconsistency Report Entries
        inconsistency_entries = []
        impact_narratives = ai_narratives.get("inconsistency_narratives", {})
        
        for issue in verification_issues:
            issue_id = issue.get("id")
            
            # Map evidence
            evidence_entries = []
            for ev in issue.get("evidence", []):
                evidence_entries.append(EvidenceEntry(
                    document=ev.get("document"),
                    value=ev.get("value"),
                    canonical_path=ev.get("canonical_path"),
                    source_block_id=ev.get("source_block_id"),
                    page=ev.get("page"),
                    slide=ev.get("slide"),
                    sheet=ev.get("sheet"),
                    snippet=ev.get("snippet")
                ))

            # Retrieve AI impacts
            ai_impact = impact_narratives.get(issue_id, {})
            business_impact = ai_impact.get(
                "business_impact", 
                "Discrepancy in metrics indicates potential accounting variances."
            )
            recommended_action = ai_impact.get(
                "recommended_action", 
                "Reconcile values across documents."
            )

            inconsistency_entries.append(InconsistencyReportEntry(
                issue_id=issue_id,
                classification=issue.get("classification"),
                severity=issue.get("severity"),
                canonical_field=issue.get("field"),
                documents=issue.get("documents", []),
                authoritative_document=issue.get("authoritative_document"),
                authoritative_value=issue.get("authoritative_value"),
                description=issue.get("description", ""),
                business_impact=business_impact,
                recommended_action=recommended_action,
                evidence=evidence_entries
            ))

        # 2. Follow-Up Questions
        question_entries = []
        question_narratives = ai_narratives.get("questions_narratives", {})
        
        for idx, issue in enumerate(verification_issues):
            issue_id = issue.get("id")
            ai_q = question_narratives.get(issue_id, {})
            
            q_text = ai_q.get("question", f"Please clarify discrepancy for {issue.get('field')}.")
            why = ai_q.get("why_it_matters", "Auditing consistency is required.")
            req_doc = ai_q.get("required_document", "historical_financial_statements")
            exp_ans = ai_q.get("expected_answer", "Aligned financial statements values.")

            question_entries.append(FollowUpQuestion(
                question_id=f"QST-{idx+1:06d}",
                priority=issue.get("severity", "MEDIUM"),
                related_issue=issue_id,
                question=q_text,
                why_it_matters=why,
                required_document=req_doc,
                expected_answer=exp_ans
            ))

        # 3. Executive Summary
        exec_data = ai_narratives.get("executive_narrative", {})
        exec_model = ExecutiveSummary(
            company_overview=exec_data.get("company_overview", "N/A"),
            overall_readiness=exec_data.get("overall_readiness", "N/A"),
            top_risks=exec_data.get("top_risks", []),
            top_strengths=exec_data.get("top_strengths", []),
            critical_issues=exec_data.get("critical_issues", []),
            immediate_actions=exec_data.get("immediate_actions", []),
            investor_readiness=exec_data.get("investor_readiness", "N/A")
        )

        # 4. Readiness Summary
        narrative_sum = ai_narratives.get("narrative_summary", {})
        
        # Calculate sub-scores dynamically based on stats
        missing_count = stats.get("missing_information", 0)
        mismatch_count = stats.get("verified_mismatches", 0)
        inconsistency_count = stats.get("unresolved_inconsistencies", 0)
        
        completeness = int(max(10, 100 - missing_count * 8))
        consistency = int(max(10, 100 - (mismatch_count * 15 + inconsistency_count * 8)))
        recency = 95
        factuality = int(max(10, 100 - mismatch_count * 20))
        
        from app.readiness.schemas.readiness import ScoringBreakdown
        breakdown = ScoringBreakdown(
            completeness=completeness,
            consistency=consistency,
            recency=recency,
            factuality=factuality
        )
        
        summary_model = ReadinessSummary(
            company_id=company_id,
            company_name=scoring_results.get("company_name"),
            overall_status=scoring_results.get("overall_status"),
            readiness_score=scoring_results.get("readiness_score"),
            overall_readiness_score=scoring_results.get("readiness_score"),
            scoring_breakdown=breakdown,
            documents_reviewed=documents_reviewed,
            verified_matches=stats.get("matched", 0),
            verified_mismatches=stats.get("verified_mismatches", 0),
            missing_information=stats.get("missing_information", 0),
            unresolved_inconsistencies=stats.get("unresolved_inconsistencies", 0),
            strengths=narrative_sum.get("strengths", []),
            risks=narrative_sum.get("risks", []),
            next_steps=narrative_sum.get("next_steps", []),
            executive_summary=narrative_sum.get("executive_summary", "")
        )

        return {
            "inconsistency_report": [entry.model_dump() for entry in inconsistency_entries],
            "follow_up_questions": [q.model_dump() for q in question_entries],
            "executive_summary": exec_model.model_dump(),
            "readiness_summary": summary_model.model_dump()
        }
    
    @staticmethod
    def get_documents_reviewed(outputs_dir: str, company_id: str) -> List[str]:
        # Scans outputs folder to see what templates/files were generated
        comp_dir = os.path.join(outputs_dir, company_id)
        if not os.path.exists(comp_dir):
            return []
        docs = []
        for file in os.listdir(comp_dir):
            if file.endswith(".json") and file not in (
                "extraction_manifest.json", "traceability_report.json",
                "verification_summary.json", "report_context.json", "readiness_manifest.json"
            ):
                docs.append(os.path.splitext(file)[0])
        return sorted(docs)
