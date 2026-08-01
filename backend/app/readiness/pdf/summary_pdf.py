from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from app.readiness.pdf.base import NumberedCanvas, title_style, h1_style, body_style, bullet_style, LIGHT_BG, BORDER_COLOR
from app.readiness.pdf.report_utils import PdfReportUtils

class SummaryPdfGenerator:
    @staticmethod
    def generate(company_id: str, summary_data: dict, filepath: str) -> None:
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        story = []
        
        # Title Header
        story.append(PdfReportUtils.wrap_p(f"INVESTMENT READINESS REPORT: {company_id.upper()}", title_style))
        story.append(PdfReportUtils.wrap_p("Diligence Metrics & E2E Verification Summary", body_style))
        story.append(Spacer(1, 8))
        story.append(PdfReportUtils.build_divider())
        story.append(Spacer(1, 10))

        # Overall Status Callout
        status = summary_data.get("overall_status", "N/A")
        score = summary_data.get("readiness_score", 0)
        
        status_color = colors.HexColor("#48BB78")
        if "MINOR" in status:
            status_color = colors.HexColor("#ECC94B")
        elif "MAJOR" in status:
            status_color = colors.HexColor("#ED8936")
        elif "NOT" in status:
            status_color = colors.HexColor("#F56565")

        status_box = PdfReportUtils.build_callout_box(
            f"Readiness Verdict: {status} (Score: {score}/100)",
            "The fundraising documents package was evaluated across 11 canonical investment fields. "
            "Calculated readiness classification is strictly determined by deterministic verification results.",
            status_color
        )
        story.append(status_box)
        story.append(Spacer(1, 12))

        # Metrics Table
        story.append(PdfReportUtils.wrap_p("Diligence Verification Metrics", h1_style))
        metrics_data = [
            [PdfReportUtils.wrap_p("<b>Metric Type</b>", body_style), PdfReportUtils.wrap_p("<b>Count</b>", body_style)],
            [PdfReportUtils.wrap_p("Verified Matches", body_style), PdfReportUtils.wrap_p(str(summary_data.get("verified_matches", 0)), body_style)],
            [PdfReportUtils.wrap_p("Verified Mismatches", body_style), PdfReportUtils.wrap_p(str(summary_data.get("verified_mismatches", 0)), body_style)],
            [PdfReportUtils.wrap_p("Missing Information", body_style), PdfReportUtils.wrap_p(str(summary_data.get("missing_information", 0)), body_style)],
            [PdfReportUtils.wrap_p("Unresolved Inconsistencies", body_style), PdfReportUtils.wrap_p(str(summary_data.get("unresolved_inconsistencies", 0)), body_style)]
        ]
        
        t = Table(metrics_data, colWidths=[252, 252])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        # Overview Narrative
        story.append(PdfReportUtils.wrap_p("Deal Diligence Overview", h1_style))
        story.append(PdfReportUtils.wrap_p(summary_data.get("executive_summary", "N/A"), body_style))
        story.append(Spacer(1, 10))

        # Strengths & Risks lists
        story.append(PdfReportUtils.wrap_p("Key Diligence Strengths", h1_style))
        for strength in summary_data.get("strengths", []):
            story.append(Paragraph(f"&bull; {strength}", bullet_style))
        story.append(Spacer(1, 10))

        story.append(PdfReportUtils.wrap_p("Identified Risks & Inconsistencies", h1_style))
        for risk in summary_data.get("risks", []):
            story.append(Paragraph(f"&bull; {risk}", bullet_style))
        story.append(Spacer(1, 10))

        story.append(PdfReportUtils.wrap_p("Recommended Next Steps Action Plan", h1_style))
        for step in summary_data.get("next_steps", []):
            story.append(Paragraph(f"&bull; {step}", bullet_style))

        doc.build(story, canvasmaker=NumberedCanvas)
