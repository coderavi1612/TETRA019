import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawRightString(self._pagesize[0] - 54, 36, f"Page {self._pageNumber} of {page_count}")
        self.drawString(54, 36, "Confidential — For Internal Diligence Review Only")
        
        # Header for page 2+
        if self._pageNumber > 1:
            self.drawString(54, self._pagesize[1] - 36, "DUELENS Diligence Review Report")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, self._pagesize[1] - 42, self._pagesize[0] - 54, self._pagesize[1] - 42)

# Corporate Colors Config
NAVY = colors.HexColor("#1A365D")
SLATE = colors.HexColor("#2D3748")
GREY = colors.HexColor("#718096")
LIGHT_BG = colors.HexColor("#F7FAFC")
BORDER_COLOR = colors.HexColor("#E2E8F0")

# Global Styles Configuration
styles = getSampleStyleSheet()

# Create or retrieve styles safely
title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=26,
    textColor=NAVY,
    alignment=0,
    spaceAfter=15
)

h1_style = ParagraphStyle(
    "SectionHeader",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    textColor=NAVY,
    spaceBefore=14,
    spaceAfter=6,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    "SubSectionHeader",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    textColor=SLATE,
    spaceBefore=10,
    spaceAfter=4,
    keepWithNext=True
)

body_style = ParagraphStyle(
    "BodyTextCustom",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=13,
    textColor=SLATE,
    spaceAfter=6
)

bullet_style = ParagraphStyle(
    "BulletCustom",
    parent=body_style,
    leftIndent=15,
    bulletIndent=5,
    spaceAfter=4
)
