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
        
        system_instruction = (
            "You are a strict fact extraction engine. Your task is to extract facts from the provided document chunks "
            "and fill the values in the JSON template according to the Specification Registry. Do NOT perform any calculations, "
            "comparisons, or reconciliations. Populate only values that explicitly exist in the text."
        )
        
        output_rules = (
            "CRITICAL EXTRACTION RULES:\n"
            "1. You are extracting facts.\n"
            "2. You are NOT analysing.\n"
            "3. You are NOT comparing.\n"
            "4. You are NOT calculating.\n"
            "5. You are NOT estimating.\n"
            "6. You are NOT reconciling.\n"
            "7. You are NOT deriving.\n"
            "8. You are NOT annualizing.\n"
            "9. You are NOT inferring.\n"
            "10. If information does not explicitly exist in the chunk, leave the field or the 'value' field as null.\n"
            "11. Never invent data.\n"
            "12. Never remove, rename, or delete any keys or sections from the template.\n"
            "13. Fill the simple metadata fields (with raw text strings) and metric object keys inside the template. The template's keys and hierarchy must be preserved exactly.\n"
            "14. Preserve unknown placeholder fields exactly as they appear in the template. Never remove optional sections.\n"
            "15. You must preserve the exact ordering of arrays defined in the JSON template.\n"
            "16. Never reorder sections or fields. Never omit placeholders.\n"
            "17. For every metric field you extract (where key contains 'value'), you MUST populate:\n"
            "    - 'source_reference': the filename containing the fact.\n"
            "    - 'source_block_id': the exact block ID containing the fact.\n"
            "    - 'page' / 'slide' / 'sheet' / 'extracted_text_snippet' if available.\n"
            "18. Standardize metric values to their full numeric representation (e.g., convert '1.8 Cr' or '1.8 Crore' to '18000000', '10 Lakhs' to '1000000', '5 Mn' or '5 Million' to '5000000'). Do not write textual abbreviations directly in numeric value fields. Keep the original textual expression in 'extracted_text_snippet' for reference.\n"
            "19. Output ONLY valid JSON. No markdown code fences (like ```json), no extra text. Just raw JSON."
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
