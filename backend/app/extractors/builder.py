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
        """
        Retrieves document-specific prompt instructions.
        """
        # Mapping to prompt templates
        if document_type == "pitch_deck":
            return PitchDeckPrompt.PROMPT
        elif document_type in ["historical_financial_statements", "financial_statement"]:
            return HistoricalFinancialsPrompt.PROMPT
        elif document_type in ["mis", "mis_report", "monthly_mis_report"]:
            return MISPrompt.PROMPT
        elif document_type == "financial_projections":
            return ProjectionsPrompt.PROMPT
        elif document_type == "cap_table":
            return CapTablePrompt.PROMPT
        return "DOCUMENT-SPECIFIC INSTRUCTIONS: Unknown Document Type. Extract any financial, traction, or fundraising facts."

    @classmethod
    def build(
        cls, 
        document_type: str, 
        registry_info: Dict[str, Any], 
        template_json_str: str, 
        chunk_blocks: List[ContentBlock]
    ) -> str:
        """
        Builds the structured extraction prompt combining:
        System Prompt -> Document Prompt -> Metric Registry -> JSON Template -> Chunk -> Output Rules
        """
        # Serialize block content for clarity
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
        
        system_instruction = BasePrompt.SYSTEM_INSTRUCTION
        
        output_rules = (
            "CRITICAL OUTPUT RULES:\n"
            "1. Output ONLY valid JSON. No markdown code fences (like ```json), no extra text. Just raw JSON.\n"
            "2. Fill the simple metadata fields (with raw text strings) and metric object keys inside the template.\n"
            "3. The template's keys, hierarchy, and array ordering must be preserved exactly.\n"
            "4. Standardize metric values to their full numeric representation "
            "(e.g., convert '1.8 Cr' to '18000000', '10 Lakhs' to '1000000'). "
            "Keep the original textual expression in 'extracted_text_snippet' for reference."
        )
        
        prompt = (
            f"SYSTEM INSTRUCTIONS:\n{system_instruction}\n\n"
            f"DOCUMENT-SPECIFIC INSTRUCTIONS:\n{doc_prompt}\n\n"
            f"SPECIFICATION REGISTRY DETAILS:\n{registry_json}\n\n"
            f"EMPTY JSON TEMPLATE (Fill simple metadata fields like company_legal_name, company_name, reporting_date, prepared_by, etc. with text strings, and fill metric objects by populating their value, source_reference, source_block_id, page, slide, sheet, extracted_text_snippet keys):\n"
            f"{template_json_str}\n\n"
            f"PARSED DOCUMENT BLOCKS FOR EXTRACTION:\n"
            f"{chunk_json}\n\n"
            f"OUTPUT RULES:\n{output_rules}"
        )
        return prompt
