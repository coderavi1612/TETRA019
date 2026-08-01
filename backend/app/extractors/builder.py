import json
from typing import List, Dict, Any
from app.prompts.base import BasePrompt
from app.prompts.pitch_deck import PitchDeckPrompt
from app.prompts.historical_financials import HistoricalFinancialsPrompt
from app.prompts.mis import MISPrompt
from app.prompts.projections import ProjectionsPrompt
from app.prompts.cap_table import CapTablePrompt
from app.schemas.parsed_document import ContentBlock

class PromptBuilder:
    @staticmethod
    def get_document_prompt(document_type: str) -> str:
        if document_type == "pitch_deck":
            return PitchDeckPrompt.PROMPT
        elif document_type == "historical_financial_statements":
            return HistoricalFinancialsPrompt.PROMPT
        elif document_type == "mis_report":
            return MISPrompt.PROMPT
        elif document_type == "financial_projections":
            return ProjectionsPrompt.PROMPT
        elif document_type == "cap_table":
            return CapTablePrompt.PROMPT
        else:
            return "DOCUMENT-SPECIFIC INSTRUCTIONS: Unknown Document Type. Extract any financial, traction, or fundraising facts."

    @classmethod
    def build(cls, document_type: str, registry_info: Dict[str, Any], chunk_blocks: List[ContentBlock]) -> str:
        # Serialize chunk blocks to list of dicts to preserve IDs and sequence
        chunk_data = []
        for block in chunk_blocks:
            block_dict = {
                "id": block.id,
                "sequence": block.sequence,
                "content_type": block.content_type,
                "page": block.page,
                "slide": block.slide,
                "sheet": block.sheet,
                "raw_text": block.raw_text,
                "rows": block.rows,
                "source": {
                    "file": block.source.file,
                    "page": block.source.page,
                    "slide": block.source.slide,
                    "sheet": block.source.sheet
                }
            }
            chunk_data.append(block_dict)
            
        chunk_json = json.dumps(chunk_data, indent=2)
        registry_json = json.dumps(registry_info, indent=2)
        
        doc_prompt = cls.get_document_prompt(document_type)
        
        return BasePrompt.build_extraction_prompt(doc_prompt, registry_json, chunk_json)
