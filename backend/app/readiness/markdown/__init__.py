import os

class MarkdownReportGenerator:
    @staticmethod
    def get_template_content(name: str) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "templates", f"{name}.md")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    def generate_markdown(cls, company_id: str, reports_json: dict) -> dict:
        """
        Processes reports JSON and outputs formatted markdown strings.
        Returns a dict: {report_filename: markdown_string}
        """
        header_tmpl = cls.get_template_content("header")
        footer_tmpl = cls.get_template_content("footer")
        
        header = header_tmpl.format(company_id=company_id)
        footer = footer_tmpl.format(company_id=company_id)

        # 1. Executive Summary Markdown
        exec_data = reports_json["executive_summary"]
        exec_tmpl = cls.get_template_content("executive")
        
        top_strengths = "\n".join([f"- {s}" for s in exec_data.get("top_strengths", [])]) or "- None identified"
        top_risks = "\n".join([f"- {r}" for r in exec_data.get("top_risks", [])]) or "- None identified"
        critical_issues = "\n".join([f"- {c}" for c in exec_data.get("critical_issues", [])]) or "- None identified"
        immediate_actions = "\n".join([f"- {a}" for a in exec_data.get("immediate_actions", [])]) or "- None identified"

        exec_md = exec_tmpl.format(
            header=header,
            company_overview=exec_data.get("company_overview", "N/A"),
            overall_readiness=exec_data.get("overall_readiness", "N/A"),
            top_strengths=top_strengths,
            top_risks=top_risks,
            critical_issues=critical_issues,
            immediate_actions=immediate_actions,
            investor_readiness=exec_data.get("investor_readiness", "N/A"),
            footer=footer
        )

        # 2. Readiness Summary Markdown
        sum_data = reports_json["readiness_summary"]
        sum_tmpl = cls.get_template_content("summary")
        
        strengths = "\n".join([f"- {s}" for s in sum_data.get("strengths", [])]) or "- None identified"
        risks = "\n".join([f"- {r}" for r in sum_data.get("risks", [])]) or "- None identified"
        next_steps = "\n".join([f"- {n}" for n in sum_data.get("next_steps", [])]) or "- None identified"

        sum_md = sum_tmpl.format(
            header=header,
            overall_status=sum_data.get("overall_status", "N/A"),
            readiness_score=sum_data.get("readiness_score", 0),
            documents_reviewed=", ".join([f"`{d}`" for d in sum_data.get("documents_reviewed", [])]),
            verified_matches=sum_data.get("verified_matches", 0),
            verified_mismatches=sum_data.get("verified_mismatches", 0),
            missing_information=sum_data.get("missing_information", 0),
            unresolved_inconsistencies=sum_data.get("unresolved_inconsistencies", 0),
            executive_summary=sum_data.get("executive_summary", ""),
            strengths=strengths,
            risks=risks,
            next_steps=next_steps,
            footer=footer
        )

        # 3. Follow-Up Questions Markdown
        q_data = reports_json["follow_up_questions"]
        q_tmpl = cls.get_template_content("questions")
        
        q_rows = []
        for q in q_data:
            q_rows.append(
                f"| {q['question_id']} | {q['priority']} | {q['related_issue']} | "
                f"**Question:** {q['question']}<br>**Rationale:** {q['why_it_matters']} | "
                f"**Required Doc:** {q['required_document']}<br>**Expected Answer:** {q['expected_answer']} |"
            )
        q_rows_str = "\n".join(q_rows) if q_rows else "| - | - | - | No follow-up questions generated. | - |"

        q_md = q_tmpl.format(
            header=header,
            questions_rows=q_rows_str,
            footer=footer
        )

        # 4. Inconsistency Report Markdown
        inc_data = reports_json["inconsistency_report"]
        inc_tmpl = cls.get_template_content("report")
        
        blocks = []
        for entry in inc_data:
            ev_rows = []
            for ev in entry.get("evidence", []):
                val_display = str(ev.get("value"))
                locs = []
                if ev.get("page"):
                    locs.append(f"Page {ev['page']}")
                if ev.get("slide"):
                    locs.append(f"Slide {ev['slide']}")
                if ev.get("sheet"):
                    locs.append(f"Sheet {ev['sheet']}")
                locs_str = ", ".join(locs) if locs else "N/A"
                snippet = ev.get("snippet") or "N/A"
                
                ev_rows.append(
                    f"| {ev.get('document')} | `{val_display}` | {ev.get('source_block_id')} | {locs_str} | {snippet} |"
                )
            
            ev_table = (
                "| Document | Extracted Value | Source Block ID | Location | Snippet |\n"
                "|---|---|---|---|---|\n" + "\n".join(ev_rows)
            ) if ev_rows else "*No evidence mapped.*"

            blocks.append(
                f"### Issue {entry.get('issue_id')}: {entry.get('canonical_field')}\n"
                f"- **Classification:** {entry.get('classification')}\n"
                f"- **Severity:** `{entry.get('severity')}`\n"
                f"- **Documents Involved:** {', '.join(entry.get('documents', []))}\n"
                f"- **Authoritative Source:** {entry.get('authoritative_document')} (Value: `{entry.get('authoritative_value')}`)\n"
                f"- **Description:** {entry.get('description', '')}\n\n"
                f"#### Business Impact\n{entry.get('business_impact', '')}\n\n"
                f"#### Recommended Action\n{entry.get('recommended_action', '')}\n\n"
                f"#### Evidence Mapped\n{ev_table}\n\n"
                f"---\n"
            )
        
        blocks_str = "\n".join(blocks) if blocks else "*No inconsistencies detected.*"
        
        inc_md = inc_tmpl.format(
            header=header,
            inconsistency_blocks=blocks_str,
            footer=footer
        )

        return {
            "readiness_summary.md": sum_md,
            "executive_summary.md": exec_md,
            "follow_up_questions.md": q_md,
            "inconsistency_report.md": inc_md
        }
