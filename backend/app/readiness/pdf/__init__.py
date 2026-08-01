import os
from app.readiness.pdf.summary_pdf import SummaryPdfGenerator
from app.readiness.pdf.executive_pdf import ExecutivePdfGenerator
from app.readiness.pdf.questions_pdf import QuestionsPdfGenerator

class PdfReportAssembler:
    @staticmethod
    def generate_all_pdfs(company_id: str, reports_json: dict, output_dir: str) -> None:
        """
        Compiles the three PDF reports (summary, executive, and questions) to the outputs directory.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Summary PDF
        SummaryPdfGenerator.generate(
            company_id,
            reports_json["readiness_summary"],
            os.path.join(output_dir, "readiness_summary.pdf")
        )
        
        # 2. Executive PDF
        ExecutivePdfGenerator.generate(
            company_id,
            reports_json["executive_summary"],
            os.path.join(output_dir, "executive_summary.pdf")
        )
        
        # 3. Questions PDF
        QuestionsPdfGenerator.generate(
            company_id,
            reports_json["follow_up_questions"],
            os.path.join(output_dir, "follow_up_questions.pdf")
        )
