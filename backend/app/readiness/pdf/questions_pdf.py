from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from app.readiness.pdf.base import NumberedCanvas, title_style, body_style, LIGHT_BG, BORDER_COLOR
from app.readiness.pdf.report_utils import PdfReportUtils

class QuestionsPdfGenerator:
    @staticmethod
    def generate(company_id: str, questions_data: list, filepath: str) -> None:
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=54,
            bottomMargin=54
        )
        
        story = []
        
        story.append(PdfReportUtils.wrap_p(f"DILIGENCE FOLLOW-UP QUESTIONS: {company_id.upper()}", title_style))
        story.append(PdfReportUtils.wrap_p("Targeted diligence follow-ups to resolve metric inconsistencies", body_style))
        story.append(Spacer(1, 8))
        story.append(PdfReportUtils.build_divider())
        story.append(Spacer(1, 10))

        # Build Table Headers
        headers = [
            PdfReportUtils.wrap_p("<b>ID / Priority</b>", body_style),
            PdfReportUtils.wrap_p("<b>Related Issue</b>", body_style),
            PdfReportUtils.wrap_p("<b>Question & Diligence Rationale</b>", body_style),
            PdfReportUtils.wrap_p("<b>Required Update & Expected Answer</b>", body_style)
        ]
        
        table_rows = [headers]
        for q in questions_data:
            q_id = q.get("question_id")
            priority = q.get("priority")
            related = q.get("related_issue")
            question = q.get("question")
            why = q.get("why_it_matters")
            req_doc = q.get("required_document")
            expected = q.get("expected_answer")
            
            row = [
                PdfReportUtils.wrap_p(f"<b>{q_id}</b><br/>[{priority}]", body_style),
                PdfReportUtils.wrap_p(related, body_style),
                PdfReportUtils.wrap_p(f"<b>Q:</b> {question}<br/><b>Rationale:</b> {why}", body_style),
                PdfReportUtils.wrap_p(f"<b>Doc:</b> {req_doc}<br/><b>Expectation:</b> {expected}", body_style)
            ]
            table_rows.append(row)

        if len(table_rows) == 1:
            table_rows.append([
                PdfReportUtils.wrap_p("-", body_style),
                PdfReportUtils.wrap_p("-", body_style),
                PdfReportUtils.wrap_p("No follow-up questions generated.", body_style),
                PdfReportUtils.wrap_p("-", body_style)
            ])

        # Width of letter pages is 612. Margins are 36 on each side, so table width is 540.
        t = Table(table_rows, colWidths=[75, 80, 205, 180])
        
        t_styles = [
            ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]
        
        for i in range(1, len(table_rows)):
            if i % 2 == 0:
                t_styles.append(('BACKGROUND', (0,i), (-1,i), LIGHT_BG))
                
        t.setStyle(TableStyle(t_styles))
        story.append(t)

        doc.build(story, canvasmaker=NumberedCanvas)
