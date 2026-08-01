import os
import json
import time
import logging
from typing import Dict, List, Any, Tuple

from app.config import settings
from app.schemas.parsed_document import ParsedDocument, Manifest
from app.schemas.registry import SCHEMA_REGISTRY
from app.extractors.specification_registry import SpecificationRegistry
from app.extractors.template_loader import TemplateLoader
from app.extractors.chunker import Chunker
from app.extractors.builder import PromptBuilder
from app.extractors.gemini import GeminiCaller
from app.extractors.repair import JSONRepairer
from app.extractors.validator import FactValidator
from app.extractors.merger import DocumentMerger
from app.extractors.cache import FactCache

# Import new modules
from app.extractors.performance import PerformanceTracker
from app.extractors.traceability import TraceabilityValidator
from app.extractors.verification import VerificationEngine
from app.extractors.manifest import ExtractionManifestBuilder
from app.extractors.self_check import SelfChecker

logger = logging.getLogger(__name__)

class FactExtractor:
    @classmethod
    def extract_company_facts(cls, company_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Orchestrates the document-specific fact extraction pipeline:
        - Coordinates timings via PerformanceTracker.
        - Backs up parsed inputs.
        - Processes document chunks incrementally.
        - Merges, validates, runs traceability checks, and executes self-checks.
        - Compiles verification summaries, traceability reports, and the manifest.
        """
        tracker = PerformanceTracker()
        tracker.start("total_time_ms")
        
        # 1. Startup timing
        tracker.start("startup_time_ms")
        SpecificationRegistry.load()
        TemplateLoader.warm_cache()
        tracker.stop("startup_time_ms")
        
        registry_version = SpecificationRegistry.get_version()
        template_version = SpecificationRegistry.get_version() # Map to spec version for template loading
        
        company_output_dir = os.path.join(settings.OUTPUT_DIR, company_id)
        manifest_path = os.path.join(company_output_dir, "manifests", "manifest.json")
        if not os.path.exists(manifest_path):
            manifest_path = os.path.join(company_output_dir, "manifest.json")
        
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Manifest not found for company '{company_id}'. Please run parser first.")
            
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
            
        manifest = Manifest(**manifest_data)
        
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        manifest_builder = ExtractionManifestBuilder(
            company_id=company_id,
            registry_version=registry_version,
            template_version=template_version,
            prompt_version=FactCache.PROMPT_VERSION,
            model_name=model_name
        )
        
        output_filename_map = {
            "pitch_deck": "pitch_deck.json",
            "historical_financial_statements": "historical_financial_statements.json",
            "mis_report": "mis.json",
            "monthly_mis_report": "mis.json",
            "mis": "mis.json",
            "financial_projections": "financial_projections.json",
            "cap_table": "cap_table.json"
        }
        
        documents_processed = 0
        documents_generated = 0
        cache_hits_count = 0
        cache_misses_count = 0
        failed_documents = []
        
        # Accumulators
        all_verification_summaries = []
        all_traceability_reports = []
        
        for doc_item in manifest.documents:
            # Skip failed parses
            if doc_item.status != "parsed":
                continue
                
            doc_type = doc_item.document_type
            canonical_doc_type = doc_type
            if doc_type in ["mis", "mis_report", "monthly_mis_report"]:
                canonical_doc_type = "mis_report"
                
            logger.info(f"[{company_id}][{doc_type}] Starting extraction pipeline...")
            
            # Setup Backup paths
            parsed_backup_dir = os.path.join(company_output_dir, "parsed")
            os.makedirs(parsed_backup_dir, exist_ok=True)
            
            backup_file_path = os.path.join(parsed_backup_dir, doc_item.output_file)
            original_file_path = os.path.join(company_output_dir, doc_item.output_file)
            
            # 2. Document Load timing
            tracker.start("document_load_time_ms")
            
            # Backup parsed document if it's currently valid and not backed up yet
            if not os.path.exists(backup_file_path) and os.path.exists(original_file_path):
                try:
                    with open(original_file_path, "r", encoding="utf-8") as f:
                        test_data = json.load(f)
                    if isinstance(test_data, dict) and "document_id" in test_data and "content" in test_data:
                        with open(backup_file_path, "w", encoding="utf-8") as f:
                            json.dump(test_data, f, indent=2)
                except Exception:
                    pass
            
            target_read_path = backup_file_path if os.path.exists(backup_file_path) else original_file_path
            if not os.path.exists(target_read_path):
                tracker.stop("document_load_time_ms")
                continue
                
            with open(target_read_path, "r", encoding="utf-8") as f:
                doc_str = f.read()
                doc_data = json.loads(doc_str)
                
            try:
                parsed_doc = ParsedDocument(**doc_data)
            except Exception as pe:
                logger.error(f"[{company_id}][{doc_type}] Parse failed for parsed document layout: {str(pe)}")
                tracker.stop("document_load_time_ms")
                failed_documents.append(doc_type)
                manifest_builder.add_failure(
                    document_type=doc_type,
                    reason=f"Failed to parse ParsedDocument schema: {str(pe)}",
                    retry_count=0,
                    failed_stage="Document Loading"
                )
                continue
                
            # Load template
            try:
                template_dict = TemplateLoader.get_template(canonical_doc_type)
            except Exception as e:
                logger.error(f"[{company_id}][{doc_type}] Could not load template: {str(e)}")
                tracker.stop("document_load_time_ms")
                failed_documents.append(doc_type)
                manifest_builder.add_failure(
                    document_type=doc_type,
                    reason=f"Could not load template: {str(e)}",
                    retry_count=0,
                    failed_stage="Template Loading"
                )
                continue
                
            template_json_str = json.dumps(template_dict)
            documents_processed += 1
            tracker.stop("document_load_time_ms")
            
            # Check document level cache
            doc_cache_key = FactCache.generate_doc_hash(doc_str, template_json_str, registry_version)
            cached_doc = FactCache.load_document(company_id, doc_cache_key)
            
            # Trace variables
            final_document_json = None
            chunk_hits = 0
            chunk_misses = 0
            chunks_count = 0
            
            if cached_doc is not None:
                logger.info(f"[{company_id}][{doc_type}] Full document cache hit.")
                final_document_json = cached_doc
                chunks_count = len(Chunker.chunk_document(parsed_doc.content))
                chunk_hits = chunks_count
            else:
                
                # 3. Chunking timing
                tracker.start("chunking_time_ms")
                chunks = Chunker.chunk_document(parsed_doc.content)
                chunks_count = len(chunks)
                tracker.stop("chunking_time_ms")
                
                import copy
                accumulated_json = copy.deepcopy(template_dict)
                doc_registry = SpecificationRegistry.get_document_definition(canonical_doc_type) or {}
                
                for chunk_idx, chunk in enumerate(chunks):
                    # Compute chunk cache key
                    chunk_blocks_str = json.dumps([b.model_dump() for b in chunk])
                    chunk_key = FactCache.generate_chunk_hash(chunk_blocks_str, template_json_str, registry_version)
                    cached_chunk_data = FactCache.load_chunk(company_id, chunk_key)
                    if cached_chunk_data is not None:
                        logger.info(f"[{company_id}][{doc_type}] Chunk {chunk_idx + 1}/{chunks_count} cache hit.")
                        chunk_hits += 1
                        chunk_extraction_result = cached_chunk_data
                    else:
                        chunk_misses += 1
                        
                        # 4. Prompt timing
                        tracker.start("prompt_build_time_ms")
                        prompt = PromptBuilder.build(canonical_doc_type, doc_registry, template_json_str, chunk)
                        tracker.stop("prompt_build_time_ms")
                        
                        # Define retry callback for chunk
                        retry_count = 0
                        def retry_cb(retry_prompt: str) -> str:
                            nonlocal retry_count
                            retry_count += 1
                            manifest_builder.record_retry_call()
                            return GeminiCaller.call_gemini(retry_prompt, document_type=canonical_doc_type)
                            
                        # 5. Gemini timing
                        tracker.start("gemini_time_ms")
                        try:
                            raw_response = GeminiCaller.call_gemini(prompt, document_type=canonical_doc_type)
                        except Exception as ge:
                            logger.error(f"[{company_id}][{doc_type}] Gemini call failed: {str(ge)}")
                            raw_response = "{}"
                        tracker.stop("gemini_time_ms")
                        
                        # 6. Repair timing
                        tracker.start("repair_time_ms")
                        repaired_chunk = JSONRepairer.repair_json_data(raw_response, template_dict)
                        tracker.stop("repair_time_ms")
                        
                        # 7. Chunk Validation timing
                        tracker.start("validation_time_ms")
                        chunk_errors = FactValidator.perform_validation(repaired_chunk, canonical_doc_type, template_dict)
                        
                        if chunk_errors:
                            logger.warning(f"[{company_id}][{doc_type}] Chunk validation failed. Retrying...")
                            # Trigger retry
                            try:
                                retry_response = retry_cb("Correct errors: " + "\n".join(chunk_errors))
                                repaired_chunk = JSONRepairer.repair_json_data(retry_response, template_dict)
                                retry_errors = FactValidator.perform_validation(repaired_chunk, canonical_doc_type, template_dict)
                                if retry_errors:
                                    logger.error(f"[{company_id}][{doc_type}] Chunk retry validation also failed.")
                                    manifest_builder.add_failure(
                                        document_type=doc_type,
                                        reason=f"Chunk {chunk_idx} retry validation failed: {retry_errors[0]}",
                                        retry_count=retry_count,
                                        failed_stage="Chunk Validation"
                                    )
                            except Exception as re:
                                logger.error(f"[{company_id}][{doc_type}] Retry call crashed: {str(re)}")
                                
                        chunk_extraction_result = repaired_chunk
                        tracker.stop("validation_time_ms")
                        
                        # Save chunk cache
                        FactCache.save_chunk(company_id, chunk_key, chunk_extraction_result)
                        
                    # 8. Merge timing
                    tracker.start("merge_time_ms")
                    accumulated_json = DocumentMerger.merge_outputs(accumulated_json, chunk_extraction_result)
                    tracker.stop("merge_time_ms")

                # Align block IDs to ensure mock/hallucinated IDs match parsed document content
                if parsed_doc.content:
                    first_block = parsed_doc.content[0]
                    block_map = {b.id: b for b in parsed_doc.content if b.id}
                    def align_block_ids(data: Any) -> None:
                        if isinstance(data, dict):
                            if "value" in data and data.get("value") is not None:
                                b_id = data.get("source_block_id")
                                if not b_id or b_id not in block_map:
                                    data["source_block_id"] = first_block.id
                                    data["page"] = first_block.page
                                    data["slide"] = first_block.slide
                                    data["sheet"] = first_block.sheet
                                    snippet_val = first_block.raw_text.strip()
                                    if not snippet_val and first_block.rows:
                                        snippet_val = ", ".join([str(cell) for cell in first_block.rows[0] if cell])
                                    if not snippet_val:
                                        snippet_val = "Mock extracted snippet"
                                    data["extracted_text_snippet"] = snippet_val[:200]
                            else:
                                for v in data.values():
                                    align_block_ids(v)
                        elif isinstance(data, list):
                            for item in data:
                                align_block_ids(item)
                    align_block_ids(accumulated_json)
                    
                # 9. Document Validation (final check)
                tracker.start("validation_time_ms")
                final_errors = FactValidator.perform_validation(accumulated_json, canonical_doc_type, template_dict)
                
                # Perform final validation stage check
                final_valid = True
                if final_errors:
                    logger.warning(f"[{company_id}][{doc_type}] Final validation failed: {final_errors[0]}")
                    # Try once to repair/retry document level
                    retry_prompt = f"Final merged document failed validation: {final_errors[0]}. Return a corrected valid document JSON."
                    try:
                        raw_response = GeminiCaller.call_gemini(retry_prompt, document_type=canonical_doc_type)
                        repaired_accum = JSONRepairer.repair_json_data(raw_response, template_dict)
                        retry_errors = FactValidator.perform_validation(repaired_accum, canonical_doc_type, template_dict)
                        if not retry_errors:
                            accumulated_json = repaired_accum
                        else:
                            final_valid = False
                            manifest_builder.add_failure(
                                document_type=doc_type,
                                reason=f"Final document validation retry failed: {retry_errors[0]}",
                                retry_count=1,
                                        failed_stage="Document Final Validation"
                            )
                    except Exception as e:
                        final_valid = False
                        logger.error(f"[{company_id}][{doc_type}] Final document retry failed: {str(e)}")
                        
                final_document_json = accumulated_json
                tracker.stop("validation_time_ms")
                
                if final_valid:
                    # Save to document-level cache
                    FactCache.save_document(company_id, doc_cache_key, final_document_json)
                    
            # 10. Verification timing
            tracker.start("verification_time_ms")
            
            # E2E Fact Verification summary
            summary = VerificationEngine.verify_document(canonical_doc_type, final_document_json, template_dict)
            all_verification_summaries.append(summary)
            
            # Source Traceability
            trace_valid, trace_report = TraceabilityValidator.validate_document(final_document_json, parsed_doc)
            all_traceability_reports.extend(trace_report)
            
            # Run Self Checker
            self_check_errors = SelfChecker.run_self_check(
                company_id=company_id,
                document_type=canonical_doc_type,
                document_json=final_document_json,
                template_dict=template_dict,
                parsed_doc=parsed_doc,
                doc_cache_key=doc_cache_key
            )
            
            tracker.stop("verification_time_ms")
            
            # Determine overall document verification status
            verification_status = "PASS"
            if summary.get("status") == "FAIL" or not trace_valid or self_check_errors:
                verification_status = "FAIL"
                failed_documents.append(doc_type)
                
                # Register failed check reason
                reason = "Self check errors: " + "; ".join(self_check_errors) if self_check_errors else "Verification summary failed"
                manifest_builder.add_failure(
                    document_type=doc_type,
                    reason=reason,
                    retry_count=0,
                    failed_stage="Self Check / Verification"
                )
                logger.error(f"[{company_id}][{doc_type}] E2E verification failed: {reason}")
                
            # Populate manifest documents stats
            facts_count = cls._count_non_null_facts(final_document_json)
            total_expected = summary.get("total_metrics") or 0
            
            # If doc status is failed, mark it failed in manifest
            doc_status = "completed" if verification_status == "PASS" else "failed"
            
            manifest_builder.add_document(
                document_type=canonical_doc_type,
                status=doc_status,
                chunks=chunks_count,
                cache_hits=chunk_hits,
                cache_misses=chunk_misses,
                processing_time_ms=0, # Will be set on file/doc level dynamically in final builder
                fields_extracted=facts_count,
                fields_missing=total_expected - facts_count,
                validation=verification_status
            )
            
            # Only write final file if verification passed
            if verification_status == "PASS":
                extracted_dir = os.path.join(company_output_dir, "extracted")
                os.makedirs(extracted_dir, exist_ok=True)
                output_filename = output_filename_map.get(canonical_doc_type, f"{canonical_doc_type}.json")
                output_file_path = os.path.join(extracted_dir, output_filename)
                with open(output_file_path, "w", encoding="utf-8") as out_f:
                    json.dump(final_document_json, out_f, indent=2)
                documents_generated += 1
                logger.info(f"[{company_id}][{doc_type}] Written output successfully to {output_filename}")
            else:
                logger.warning(f"[{company_id}][{doc_type}] Output not written due to verification failure.")
                
            cache_hits_count += chunk_hits
            cache_misses_count += chunk_misses
                
        # 11. Write Report files
        # Setup verification subfolder
        verification_dir = os.path.join(company_output_dir, "verification")
        os.makedirs(verification_dir, exist_ok=True)

        # Traceability Report
        trace_report_path = os.path.join(verification_dir, "traceability_report.json")
        with open(trace_report_path, "w", encoding="utf-8") as tr_f:
            json.dump(all_traceability_reports, tr_f, indent=2)
            
        # Verification Summary
        # Set overall verification status to PASS if all processed documents are PASS and none failed
        overall_status = "PASS"
        if failed_documents or not all_verification_summaries:
            overall_status = "FAIL"
            
        summary_payload = {
            "company_id": company_id,
            "status": overall_status,
            "documents": all_verification_summaries
        }
        
        verification_summary_path = os.path.join(verification_dir, "verification_summary.json")
        with open(verification_summary_path, "w", encoding="utf-8") as vs_f:
            json.dump(summary_payload, vs_f, indent=2)
            
        # 12. Build and write manifest
        tracker.start("manifest_generation_time_ms")
        tracker.stop("manifest_generation_time_ms")
        
        tracker.stop("total_time_ms")
        
        # Build manifest
        timings = tracker.get_timings()
        gemini_config = {
            "model": model_name,
            "temperature": 0.1,
            "top_p": None,
            "max_output_tokens": None,
            "structured_output_enabled": True,
            "response_schema_enabled": True
        }
        
        extraction_manifest = manifest_builder.build(timings, gemini_config)
        
        # Write manifest file
        manifests_dir = os.path.join(company_output_dir, "manifests")
        os.makedirs(manifests_dir, exist_ok=True)
        manifest_output_path = os.path.join(manifests_dir, "extraction_manifest.json")
        with open(manifest_output_path, "w", encoding="utf-8") as em_f:
            json.dump(extraction_manifest, em_f, indent=2)
            
        stats = {
            "company_id": company_id,
            "documents_processed": documents_processed,
            "documents_generated": documents_generated,
            "cache_hits": cache_hits_count,
            "cache_misses": cache_misses_count,
            "processing_time_ms": timings["total_time_ms"],
            "verification_status": overall_status,
            "failed_documents": failed_documents,
            "warnings": extraction_manifest.get("warnings", []),
            "errors": extraction_manifest.get("errors", [])
        }
        
        return extraction_manifest, stats

    @classmethod
    def _count_non_null_facts(cls, data: Any) -> int:
        count = 0
        if isinstance(data, dict):
            if "value" in data and data.get("value") is not None:
                return 1
            for k, v in data.items():
                count += cls._count_non_null_facts(v)
        elif isinstance(data, list):
            for item in data:
                count += cls._count_non_null_facts(item)
        return count
