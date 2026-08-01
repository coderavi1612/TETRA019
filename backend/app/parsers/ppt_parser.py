# pyrefly: ignore [missing-import]
from pptx import Presentation
import os
import datetime
# pyrefly: ignore [missing-import]
import pptx

from app.schemas.parsed_document import ParsedDocument, ContentBlock, BlockSource, SectionInfo, DocumentMetadata, ParserInfo, DocumentStatistics
from app.parsers.base import BaseParser

class PPTParser(BaseParser):
    def parse(self, file_path: str, company_id: str, document_type: str) -> ParsedDocument:
        doc_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        from app.core import get_utc_now_iso
        created_at = get_utc_now_iso()
        
        prs = Presentation(file_path)
        slides_count = len(prs.slides)
        
        content_blocks = []
        sequence = 0
        tables_count = 0
        words_count = 0
        
        for slide_idx, slide in enumerate(prs.slides):
            slide_num = slide_idx + 1
            
            for shape_idx, shape in enumerate(slide.shapes):
                # 1. Handle Table shapes
                if shape.has_table:
                    table = shape.table
                    rows = []
                    table_words = 0
                    for r in range(len(table.rows)):
                        row_data = []
                        for c in range(len(table.columns)):
                            cell = table.cell(r, c)
                            cell_text = cell.text
                            row_data.append(cell_text)
                            table_words += len(cell_text.split())
                        rows.append(row_data)
                        
                    words_count += table_words
                    block_id = f"{document_type}_slide_{slide_num:02d}_table_{tables_count:03d}"
                    
                    block = ContentBlock(
                        id=block_id,
                        sequence=sequence,
                        content_type="table",
                        slide=slide_num,
                        raw_text="",
                        rows=rows,
                        section=SectionInfo(),
                        source=BlockSource(file=doc_name, slide=slide_num)
                    )
                    content_blocks.append(block)
                    sequence += 1
                    tables_count += 1
                    
                # 2. Handle Text shapes
                elif shape.has_text_frame:
                    raw_text = shape.text.strip()
                    if not raw_text:
                        continue
                        
                    words_count += len(raw_text.split())
                    block_id = f"{document_type}_slide_{slide_num:02d}_block_{shape_idx:03d}"
                    
                    block = ContentBlock(
                        id=block_id,
                        sequence=sequence,
                        content_type="text",
                        slide=slide_num,
                        raw_text=shape.text,
                        section=SectionInfo(),
                        source=BlockSource(file=doc_name, slide=slide_num)
                    )
                    content_blocks.append(block)
                    sequence += 1
                    
        statistics = DocumentStatistics(
            pages=0,
            slides=slides_count,
            sheets=0,
            blocks=len(content_blocks),
            tables=tables_count,
            words=words_count
        )
        
        metadata = DocumentMetadata(
            company_id=company_id,
            file_size=file_size,
            extension=".pptx",
            mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            created_at=created_at,
            parser=ParserInfo(name="python-pptx", version=getattr(pptx, "__version__", "unknown")),
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
