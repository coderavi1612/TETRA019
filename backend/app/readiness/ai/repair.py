import json
import re
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class JSONReadinessRepairer:
    @staticmethod
    def repair_json(raw_text: str) -> Dict[str, Any]:
        """
        Attempts to parse JSON from the raw response. If it fails, extracts JSON structures via regex.
        """
        text = raw_text.strip()
        try:
            return json.loads(text)
        except Exception:
            pass

        # Match markdown block
        match_block = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match_block:
            try:
                return json.loads(match_block.group(1).strip())
            except Exception:
                pass

        # Match curly braces range
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1].strip())
            except Exception:
                pass

        raise ValueError("Could not extract or repair valid JSON from model response text")
