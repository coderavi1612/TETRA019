import os
import json
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class TemplateLoader:
    _templates: Dict[str, Any] = {}
    _loaded: bool = False
    
    @classmethod
    def load_all_templates(cls):
        """
        Discovers and loads all template JSON files under backend/json-files/.
        Caches templates in memory.
        """
        if cls._loaded:
            return
            
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
        json_dir = os.path.join(base_dir, "json-files")
        
        if not os.path.exists(json_dir):
            # Fallback to workspace root json-files if directory structure is different
            workspace_dir = os.path.dirname(base_dir)
            json_dir = os.path.join(workspace_dir, "json-files")
            
        if not os.path.exists(json_dir):
            raise FileNotFoundError(f"Templates directory not found: {json_dir}")
            
        cls._templates = {}
        logger.info(f"Loading document templates from: {json_dir}")
        
        for filename in os.listdir(json_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(json_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        template_data = json.load(f)
                    
                    # Key by filename without extension
                    name_without_ext = os.path.splitext(filename)[0]
                    cls._templates[name_without_ext] = template_data
                    
                    # Also key by internal document_type if present
                    doc_metadata = template_data.get("document_metadata", {})
                    doc_type = doc_metadata.get("document_type")
                    if doc_type:
                        cls._templates[doc_type] = template_data
                        
                    logger.info(f"Loaded template: {filename} (keyed as: {name_without_ext}, {doc_type})")
                except Exception as e:
                    logger.error(f"Error loading template {filename}: {str(e)}")
                    
        cls._loaded = True
        
    @classmethod
    def get_template(cls, document_type: str) -> Dict[str, Any]:
        """
        Retrieves a cached JSON template dictionary by document type.
        """
        cls.load_all_templates()
        
        # Support aliases
        if document_type == "mis_report" and "monthly_mis_report" in cls._templates:
            return cls._templates["monthly_mis_report"]
        if document_type == "monthly_mis_report" and "mis_report" in cls._templates:
            return cls._templates["mis_report"]
            
        if document_type in cls._templates:
            return cls._templates[document_type]
            
        # Case insensitive/hyphen normalized checks
        normalized = document_type.lower().replace("-", "_")
        if normalized in cls._templates:
            return cls._templates[normalized]
            
        for key, val in cls._templates.items():
            if key.lower().replace("-", "_") == normalized:
                return val
                
        raise ValueError(f"Template for document type '{document_type}' not found.")
        
    @classmethod
    def list_templates(cls) -> List[str]:
        """
        Lists the names of all discovered templates.
        """
        cls.load_all_templates()
        return sorted(list(set(cls._templates.keys())))
        
    @classmethod
    def warm_cache(cls):
        """
        Startup helper to warm the template cache.
        """
        cls.load_all_templates()
