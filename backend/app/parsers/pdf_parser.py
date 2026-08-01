import fitz  # PyMuPDF
import os
import datetime
from app.schemas.parsed_document import ParsedDocument, ContentBlock, BlockSource, SectionInfo, DocumentMetadata, ParserInfo, DocumentStatistics
from app.parsers.base import BaseParser

class PDFParser(BaseParser):
    def parse(self, file_path: str, company_id: str, document_type: str) -> ParsedDocument:
        doc_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        created_at = datetime.datetime.utcnow().isoformat() + "Z"
        
        doc = fitz.open(file_path)
        pages_count = doc.page_count
        
        content_blocks = []
        sequence = 0
        tables_count = 0
        words_count = 0
        
        for page_idx in range(pages_count):
            page_num = page_idx + 1
            page = doc[page_idx]
            
            # 1. Detect and extract tables to avoid duplicate text extraction
            table_bboxes = []
            try:
                tables = page.find_tables()
                for table in tables:
                    table_bbox = table.bbox  # (x0, y0, x1, y1)
                    table_bboxes.append(table_bbox)
                    
                    rows = table.extract()
                    # Calculate words in table cells
                    table_words = sum(len(str(cell).split()) for row in rows for cell in row if cell)
                    words_count += table_words
                    
                    block_id = f"{document_type}_page_{page_num:02d}_table_{tables_count:03d}"
                    
                    block = ContentBlock(
                        id=block_id,
                        sequence=sequence,
                        content_type="table",
                        page=page_num,
                        raw_text="",
                        rows=rows,
                        section=SectionInfo(),
                        source=BlockSource(file=doc_name, page=page_num)
                    )
                    content_blocks.append(block)
                    sequence += 1
                    tables_count += 1
            except Exception:
                # If table parsing fails or is unsupported, fallback and extract all as raw text
                pass
                
            # 2. Extract layout-preserving text blocks
            text_blocks = page.get_text("blocks")
            for block_idx, tb in enumerate(text_blocks):
                x0, y0, x1, y1, text, block_no, block_type = tb
                
                # Skip image blocks
                if block_type != 0:
                    continue
                    
                # Skip if text is empty/whitespace
                raw_text = text.strip()
                if not raw_text:
                    continue
                    
                # Skip if text centroid lies inside table bounding boxes
                cx = (x0 + x1) / 2
                cy = (y0 + y1) / 2
                in_table = False
                for bbox in table_bboxes:
                    tx0, ty0, tx1, ty1 = bbox
                    if tx0 <= cx <= tx1 and ty0 <= cy <= ty1:
                        in_table = True
                        break
                if in_table:
                    continue
                    
                # Count words
                words_count += len(raw_text.split())
                
                block_id = f"{document_type}_page_{page_num:02d}_block_{block_idx:03d}"
                
                block = ContentBlock(
                    id=block_id,
                    sequence=sequence,
                    content_type="text",
                    page=page_num,
                    raw_text=text,
                    section=SectionInfo(),
                    source=BlockSource(file=doc_name, page=page_num)
                )
                content_blocks.append(block)
                sequence += 1
                
        doc.close()
        
        statistics = DocumentStatistics(
            pages=pages_count,
            slides=0,
            sheets=0,
            blocks=len(content_blocks),
            tables=tables_count,
            words=words_count
        )
        
        metadata = DocumentMetadata(
            company_id=company_id,
            file_size=file_size,
            extension=".pdf",
            mime_type="application/pdf",
            created_at=created_at,
            parser=ParserInfo(name="PyMuPDF", version=fitz.__version__),
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
