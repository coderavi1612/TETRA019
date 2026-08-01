from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from app.readiness.pdf.base import body_style, BORDER_COLOR, LIGHT_BG, h2_style

class PdfReportUtils:
    @staticmethod
    def wrap_p(text: str, style=body_style) -> Paragraph:
        """
        Wraps a plain text string into a flowable Paragraph, supporting newlines as line breaks.
        """
        escaped = str(text).replace("\n", "<br/>")
        return Paragraph(escaped, style)

    @staticmethod
    def build_divider() -> Table:
        """
        Generates a 1-pixel horizontal table divider spanning A4/Letter margins.
        """
        t = Table([[""]], colWidths=[504])
        t.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        return t

    @staticmethod
    def build_callout_box(title: str, text: str, border_color: colors.Color) -> Table:
        """
        Wraps content inside a stylized, shaded callout box with a colored left-accent border.
        """
        title_p = Paragraph(f"<b>{title}</b>", h2_style)
        text_p = PdfReportUtils.wrap_p(text)
        t = Table([[title_p], [text_p]], colWidths=[490])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
            ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('LINELEFT', (0,0), (-1,-1), 3.0, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        return t
