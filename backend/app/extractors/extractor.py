import os
import json
import time
from typing import Dict, List, Any, Tuple

from app.config import settings
from app.schemas.parsed_document import ParsedDocument, Manifest
from app.schemas.fact import CompanyFacts, DocumentFacts, ExtractedFact
from app.extractors.registry import MetricRegistryLoader
from app.extractors.chunker import Chunker
from app.extractors.builder import PromptBuilder
from app.extractors.gemini import GeminiCaller
from app.extractors.validator import FactValidator
from app.extractors.cache import FactCache
from app.prompts.base import BasePrompt

class FactExtractor:
    @classmethod
    def extract_company_facts(cls, company_id: str) -> Tuple[CompanyFacts, Dict[str, Any]]:
        """
        Orchestrates the fact extraction pipeline:
        - Loads manifest & parsed documents.
        - Loads spec sheets dynamically from md-files/.
        - Handles cache checks (checking document + prompt + registry versions).
        - Chunks documents, formats specific prompt templates, calls Gemini.
        - Repairs JSON responses and validates outputs.
        - Group facts by category, and writes facts.json.
        """
        start_time = time.time()
        
        company_output_dir = os.path.join(settings.OUTPUT_DIR, company_id)
        manifest_path = os.path.join(company_output_dir, "manifest.json")
        
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Manifest not found for company '{company_id}'. Please run parser first.")
            
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
            
        manifest = Manifest(**manifest_data)
        
        # Load registry dynamically from the md-files directory in the root of the project
        md_files_dir = os.path.join(os.path.dirname(settings.APP_DIR), "md-files")
        registry = MetricRegistryLoader.load_registry(md_files_dir)
        
        cache_hits = 0
        cache_misses = 0
        total_facts_count = 0
        document_facts_list = []
        
        for doc_item in manifest.documents:
            # Skip failed parses
            if doc_item.status != "parsed":
                continue
                
            doc_file_path = os.path.join(company_output_dir, doc_item.output_file)
            if not os.path.exists(doc_file_path):
                continue
                
            with open(doc_file_path, "r", encoding="utf-8") as f:
                doc_str = f.read()
                doc_data = json.loads(doc_str)
                
            parsed_doc = ParsedDocument(**doc_data)
            
            # Check cache
            cached_data, is_hit = FactCache.load(company_id, doc_str)
            
            extracted_facts = []
            
            if is_hit and cached_data is not None:
                cache_hits += 1
                for f_dict in cached_data:
                    try:
                        extracted_facts.append(ExtractedFact(**f_dict))
                    except Exception:
                        pass
            else:
                cache_misses += 1
                # Split content into manageable chunks preserving boundaries
                chunks = Chunker.chunk_document(parsed_doc.content)
                doc_registry = registry.get(parsed_doc.document_type) or {}
                
                for chunk in chunks:
                    prompt = PromptBuilder.build(parsed_doc.document_type, doc_registry, chunk)
                    
                    # Define a single-retry call
                    retry_cb = lambda retry_prompt: GeminiCaller.call_gemini(retry_prompt, BasePrompt.SYSTEM_INSTRUCTION)
                    
                    try:
                        response_text = GeminiCaller.call_gemini(prompt, BasePrompt.SYSTEM_INSTRUCTION)
                        chunk_facts = FactValidator.validate_facts(response_text, parsed_doc.document_type, retry_cb)
                        extracted_facts.extend(chunk_facts)
                    except Exception:
                        # Log error internally and continue
                        pass
                        
                # Persist to disk cache
                FactCache.save(company_id, doc_str, extracted_facts)
                
            # Restructure flat list of facts into categories
            categories = {
                "financial": [],
                "traction": [],
                "customers": [],
                "fundraising": [],
                "market": [],
                "team": []
            }
            
            for fact in extracted_facts:
                cat = fact.category if fact.category in categories else "financial"
                categories[cat].append(fact)
                total_facts_count += 1
                
            document_facts_list.append(
                DocumentFacts(
                    document_type=parsed_doc.document_type,
                    categories=categories
                )
            )
            
        company_facts = CompanyFacts(
            schema_version="1.0",
            registry_version=FactCache.REGISTRY_VERSION,
            prompt_version=FactCache.PROMPT_VERSION,
            company_id=company_id,
            documents=document_facts_list
        )
        
        # Save output to outputs/{company_id}/facts.json
        facts_path = os.path.join(company_output_dir, "facts.json")
        with open(facts_path, "w", encoding="utf-8") as facts_f:
            facts_f.write(company_facts.model_dump_json(indent=2))
            
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        stats = {
            "company_id": company_id,
            "documents_processed": len(document_facts_list),
            "facts_extracted": total_facts_count,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "processing_time_ms": processing_time_ms
        }
        
        return company_facts, stats
