import hashlib
import json
import os
from typing import List, Optional, Dict, Any, Tuple
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class FactCache:
    PROMPT_VERSION = "v1"

    @classmethod
    def get_cache_dir(cls, company_id: str) -> str:
        cache_dir = os.path.join(settings.OUTPUT_DIR, company_id, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    @classmethod
    def generate_chunk_hash(
        cls, 
        chunk_blocks_str: str, 
        template_json_str: str, 
        registry_version: str
    ) -> str:
        """
        Generates a compound chunk hash to ensure cache is invalidated
        if blocks, template, registry, or prompt versions change.
        """
        combined = (
            chunk_blocks_str + 
            template_json_str + 
            registry_version + 
            cls.PROMPT_VERSION
        )
        from app.core import sha256_string
        return sha256_string(combined)

    @classmethod
    def load_chunk(cls, company_id: str, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Loads the cached extraction result for a specific chunk.
        """
        cache_file = os.path.join(cls.get_cache_dir(company_id), f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading cached chunk {cache_key}: {str(e)}")
        return None

    @classmethod
    def save_chunk(cls, company_id: str, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Caches the extraction result for a specific chunk.
        """
        cache_file = os.path.join(cls.get_cache_dir(company_id), f"{cache_key}.json")
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving chunk cache {cache_key}: {str(e)}")

    @classmethod
    def generate_doc_hash(
        cls, 
        document_json_str: str, 
        template_json_str: str, 
        registry_version: str
    ) -> str:
        """
        Generates a compound document hash for full document caching.
        """
        combined = (
            document_json_str + 
            template_json_str + 
            registry_version + 
            cls.PROMPT_VERSION
        )
        from app.core import sha256_string
        return sha256_string(combined)

    @classmethod
    def load_document(cls, company_id: str, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Loads the full cached document JSON.
        """
        cache_file = os.path.join(cls.get_cache_dir(company_id), f"doc_{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading cached document {cache_key}: {str(e)}")
        return None

    @classmethod
    def save_document(cls, company_id: str, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Caches the fully extracted and validated document JSON.
        """
        cache_file = os.path.join(cls.get_cache_dir(company_id), f"doc_{cache_key}.json")
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving document cache {cache_key}: {str(e)}")
