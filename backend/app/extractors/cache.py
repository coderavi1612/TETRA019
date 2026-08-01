import hashlib
import json
import os
from typing import List, Optional, Dict, Any, Tuple
from app.schemas.fact import ExtractedFact
from app.config import settings

class FactCache:
    PROMPT_VERSION = "v1"
    REGISTRY_VERSION = "2026-08-01"

    @classmethod
    def generate_hash(cls, document_json_str: str) -> str:
        # Compound key ensures prompt or registry changes invalidate cache
        combined_string = document_json_str + cls.PROMPT_VERSION + cls.REGISTRY_VERSION
        return hashlib.sha256(combined_string.encode("utf-8")).hexdigest()

    @classmethod
    def get_cache_dir(cls, company_id: str) -> str:
        cache_dir = os.path.join(settings.OUTPUT_DIR, company_id, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    @classmethod
    def load(cls, company_id: str, document_json_str: str) -> Tuple[Optional[List[Dict[str, Any]]], bool]:
        """
        Retrieves cached facts.
        Returns a tuple of (list of raw dicts, is_cache_hit).
        """
        cache_key = cls.generate_hash(document_json_str)
        cache_file = os.path.join(cls.get_cache_dir(company_id), f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return data, True
            except Exception:
                pass
        return None, False

    @classmethod
    def save(cls, company_id: str, document_json_str: str, facts: List[ExtractedFact]) -> None:
        """
        Persists a list of ExtractedFact objects as JSON.
        """
        cache_key = cls.generate_hash(document_json_str)
        cache_file = os.path.join(cls.get_cache_dir(company_id), f"{cache_key}.json")
        
        try:
            facts_dicts = [fact.model_dump() for fact in facts]
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(facts_dicts, f, indent=2)
        except Exception:
            pass
