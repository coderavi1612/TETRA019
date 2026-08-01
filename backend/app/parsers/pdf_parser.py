import fitz  # PyMuPDF
import os
import datetime
from app.schemas.parsed_document import ParsedDocument, ContentBlock, BlockSource, SectionInfo, DocumentMetadata, ParserInfo, DocumentStatistics
from app.parsers.base import BaseParser

class PDFParser(BaseParser):
    def parse(self, file_path: str, company_id: str, document_type: str) -> ParsedDocument:
        doc_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        from app.core import get_utc_now_iso
        created_at = get_utc_now_iso()
        
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
            
        from google import genai
        from google.genai import types
        from pydantic import BaseModel
        import json

        class PageText(BaseModel):
            page_number: int
            text: str

        class DocumentText(BaseModel):
            pages: list[PageText]

        model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        client = genai.Client(api_key=api_key)

        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        prompt = (
            "You are an expert document text extractor. Extract all text and tables from this document page by page. "
            "For tables, format them as markdown tables inside the text. Keep all numbers, names, and metrics exact. "
            "Return the content structured by page number."
        )

        res = client.models.generate_content(
            model=model_name,
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DocumentText,
            )
        )

        doc_text_data = json.loads(res.text)
        doc_text = DocumentText(**doc_text_data)

        content_blocks = []
        sequence = 0
        words_count = 0
        pages_count = len(doc_text.pages)

        for p in doc_text.pages:
            content_blocks.append(ContentBlock(
                id=f"{document_type}_page_{p.page_number:02d}_visual_block",
                sequence=sequence,
                content_type="text",
                page=p.page_number,
                raw_text=p.text,
                section=SectionInfo(),
                source=BlockSource(file=doc_name, page=p.page_number)
            ))
            sequence += 1
            words_count += len(p.text.split())

        statistics = DocumentStatistics(
            pages=pages_count,
            slides=0,
            sheets=0,
            blocks=len(content_blocks),
            tables=0,
            words=words_count
        )
        
        metadata = DocumentMetadata(
            company_id=company_id,
            file_size=file_size,
            extension=".pdf",
            mime_type="application/pdf",
            created_at=created_at,
            parser=ParserInfo(name="Gemini-PDF-Extractor", version="1.0"),
            statistics=statistics
        )
        
        document_id = f"{company_id}_{document_type}"
        
        return ParsedDocument(
            document_id=document_id,
            document_name=doc_name,
            document_type=document_type,
            status="parsed",
            metadata=metadata,
            content=content_blocks,
            warnings=[],
            errors=[]
        )
