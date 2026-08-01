from typing import Dict, Any, List, Tuple, Optional
import logging
from app.schemas.parsed_document import ParsedDocument

logger = logging.getLogger(__name__)

class TraceabilityValidator:
    @classmethod
    def validate_document(
        cls, 
        document_json: Dict[str, Any], 
        parsed_doc: ParsedDocument
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Recursively traverses the document JSON to validate source block IDs
        against actual parsed blocks, checking pages, slides, sheets, and snippets.
        Returns (is_valid, report_list).
        """
        report = []
        is_valid = True
        
        # Build block lookup map for O(1) checks
        block_map = {block.id: block for block in parsed_doc.content if block.id}
        
        # Helper traversal function
        def traverse(data: Any, path: str = "") -> None:
            nonlocal is_valid
            if isinstance(data, dict):
                # Check if it represents a metric value (contains 'value' key)
                if "value" in data:
                    val = data.get("value")
                    if val is not None:
                        # Value is extracted, validate traceability
                        source_block_id = data.get("source_block_id")
                        page = data.get("page")
                        slide = data.get("slide")
                        sheet = data.get("sheet")
                        snippet = data.get("extracted_text_snippet")
                        
                        error_reason = None
                        
                        # 1. source_block_id exists
                        if not source_block_id:
                            error_reason = f"Missing source_block_id at canonical path: {path}"
                        
                        # 2. belongs to parsed document content blocks
                        elif source_block_id not in block_map:
                            error_reason = f"source_block_id '{source_block_id}' not found in parsed blocks"
                            
                        # 3. page/slide/sheet matches block value
                        else:
                            block = block_map[source_block_id]
                            try:
                                if page is not None and block.page is not None and int(float(str(page))) != int(float(str(block.page))):
                                    error_reason = f"Page mismatch: expected {block.page}, got {page}"
                                elif slide is not None and block.slide is not None and int(float(str(slide))) != int(float(str(block.slide))):
                                    error_reason = f"Slide mismatch: expected {block.slide}, got {slide}"
                                elif sheet is not None and block.sheet is not None and str(sheet) != str(block.sheet):
                                    error_reason = f"Sheet mismatch: expected '{block.sheet}', got '{sheet}'"
                            except Exception as e:
                                error_reason = f"Property type conversion error: {str(e)}"
                                
                            # 4. source snippet exists
                            if not error_reason and not snippet:
                                error_reason = "Missing extracted_text_snippet"
                                
                        if error_reason:
                            is_valid = False
                            logger.error(f"[TRACEABILITY_ERROR] {error_reason} at path {path}")
                            
                        # Record in report
                        report.append({
                            "canonical_path": path,
                            "source_block_id": source_block_id or "",
                            "page": page,
                            "slide": slide,
                            "sheet": sheet,
                            "snippet": snippet or ""
                        })
                else:
                    for k, v in data.items():
                        current_path = f"{path}.{k}" if path else k
                        traverse(v, current_path)
            elif isinstance(data, list):
                for idx, item in enumerate(data):
                    current_path = f"{path}[{idx}]"
                    traverse(item, current_path)
                    
        traverse(document_json)
        return is_valid, report
