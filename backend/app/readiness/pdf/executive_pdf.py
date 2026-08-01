from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from app.readiness.pdf.base import NumberedCanvas, title_style, h1_style, body_style, bullet_style
from app.readiness.pdf.report_utils import PdfReportUtils

class ExecutivePdfGenerator:
    @staticmethod
    def generate(company_id: str, exec_data: dict, filepath: str) -> None:
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        story = []
        
        story.append(PdfReportUtils.wrap_p(f"DILIGENCE EXECUTIVE SUMMARY: {company_id.upper()}", title_style))
        story.append(PdfReportUtils.wrap_p("High-level Investment Evaluation Highlights", body_style))
        story.append(Spacer(1, 8))
        story.append(PdfReportUtils.build_divider())
        story.append(Spacer(1, 10))

        story.append(PdfReportUtils.wrap_p("Company Overview", h1_style))
        story.append(PdfReportUtils.wrap_p(exec_data.get("company_overview", "N/A"), body_style))
        story.append(Spacer(1, 10))

        story.append(PdfReportUtils.wrap_p("Overall Readiness Evaluation", h1_style))
        story.append(PdfReportUtils.wrap_p(exec_data.get("overall_readiness", "N/A"), body_style))
        story.append(Spacer(1, 10))

        story.append(PdfReportUtils.wrap_p("Key Findings Highlight", h1_style))
        
        story.append(PdfReportUtils.wrap_p("<b>Top Strengths:</b>", body_style))
        for strength in exec_data.get("top_strengths", []):
            story.append(Paragraph(f"&bull; {strength}", bullet_style))
        story.append(Spacer(1, 6))

        story.append(PdfReportUtils.wrap_p("<b>Top Risks:</b>", body_style))
        for risk in exec_data.get("top_risks", []):
            story.append(Paragraph(f"&bull; {risk}", bullet_style))
        story.append(Spacer(1, 10))

        story.append(PdfReportUtils.wrap_p("Diligence Critical Issues", h1_style))
        for issue in exec_data.get("critical_issues", []):
            story.append(Paragraph(f"&bull; {issue}", bullet_style))
        story.append(Spacer(1, 10))

        story.append(PdfReportUtils.wrap_p("Immediate Action Plan", h1_style))
        for action in exec_data.get("immediate_actions", []):
            story.append(Paragraph(f"&bull; {action}", bullet_style))
        story.append(Spacer(1, 10))

        story.append(PdfReportUtils.wrap_p("Principal's Deal Conclusion", h1_style))
        story.append(PdfReportUtils.wrap_p(exec_data.get("investor_readiness", "N/A"), body_style))

        doc.build(story, canvasmaker=NumberedCanvas)
