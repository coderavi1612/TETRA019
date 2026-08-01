import csv
import os
import datetime

from app.schemas.parsed_document import ParsedDocument, ContentBlock, BlockSource, SectionInfo, DocumentMetadata, ParserInfo, DocumentStatistics
from app.parsers.base import BaseParser

class CSVParser(BaseParser):
    def parse(self, file_path: str, company_id: str, document_type: str) -> ParsedDocument:
        doc_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        created_at = datetime.datetime.utcnow().isoformat() + "Z"
        
        rows = []
        words_count = 0
        
        # Open file with utf-8 encoding, replacing invalid characters instead of crashing
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
                words_count += sum(len(str(cell).split()) for cell in row if cell)
                
        content_blocks = []
        if rows:
            block_id = f"{document_type}_csv"
            block = ContentBlock(
                id=block_id,
                sequence=0,
                content_type="table",
                sheet="CSV",
                raw_text="",
                rows=rows,
                section=SectionInfo(),
                source=BlockSource(file=doc_name, sheet="CSV")
            )
            content_blocks.append(block)
            
        statistics = DocumentStatistics(
            pages=0,
            slides=0,
            sheets=1 if rows else 0,
            blocks=len(content_blocks),
            tables=1 if rows else 0,
            words=words_count
        )
        
        metadata = DocumentMetadata(
            company_id=company_id,
            file_size=file_size,
            extension=".csv",
            mime_type="text/csv",
            created_at=created_at,
            parser=ParserInfo(name="python-csv", version="standard-library"),
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
