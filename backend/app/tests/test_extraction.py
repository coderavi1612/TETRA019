import unittest
import json
import os
import shutil
import tempfile
import copy
from unittest.mock import patch, MagicMock

# Import schemas and extractors
from app.config import settings
from app.schemas.parsed_document import ParsedDocument, ContentBlock, BlockSource
from app.schemas.registry import SCHEMA_REGISTRY
from app.extractors.specification_registry import SpecificationRegistry
from app.extractors.template_loader import TemplateLoader
from app.extractors.chunker import Chunker
from app.extractors.repair import JSONRepairer
from app.extractors.validator import FactValidator
from app.extractors.merger import DocumentMerger
from app.extractors.cache import FactCache
from app.extractors.traceability import TraceabilityValidator
from app.extractors.verification import VerificationEngine
from app.extractors.self_check import SelfChecker
from app.extractors.extractor import FactExtractor

class TestFactExtractionPipeline(unittest.TestCase):
    def setUp(self):
        # Setup mockParsedDocument
        self.mock_blocks = [
            ContentBlock(
                id="block_01",
                sequence=1,
                content_type="text",
                page=1,
                slide=1,
                sheet=None,
                raw_text="Duelens Inc - Pitch Presentation",
                rows=None,
                source=BlockSource(file="investor_deck.pptx", page=1, slide=1, sheet=None)
            ),
            ContentBlock(
                id="block_02",
                sequence=2,
                content_type="text",
                page=2,
                slide=2,
                sheet=None,
                raw_text="Revenue: 1.2 Cr in FY25",
                rows=None,
                source=BlockSource(file="investor_deck.pptx", page=2, slide=2, sheet=None)
            )
        ]
        self.mock_metadata = {
            "company_id": "test_comp",
            "file_size": 1024,
            "extension": "pptx",
            "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "created_at": "2026-08-01T13:35:26Z",
            "parser": {
                "name": "PPTParser",
                "version": "1.0"
            },
            "statistics": {
                "pages": 0,
                "slides": 2,
                "sheets": 0,
                "blocks": 2,
                "tables": 0,
                "words": 50
            }
        }
        self.mock_parsed_doc = ParsedDocument(
            document_id="doc_test_pitch",
            document_name="investor_deck.pptx",
            document_type="pitch_deck",
            metadata=self.mock_metadata,
            content=self.mock_blocks
        )
        
        # Load pitch_deck template
        SpecificationRegistry.load()
        TemplateLoader.warm_cache()
        self.pitch_deck_template = copy.deepcopy(TemplateLoader.get_template("pitch_deck"))

    def test_successful_extraction_mock(self):
        """Test successful mock extraction mapping and schema validation."""
        mock_json_response = {
            "company_identity": {
                "company_name": {
                    "value": "Duelens Inc",
                    "unit": None,
                    "period": None,
                    "actual_vs_budget": None,
                    "source_reference": "investor_deck.pptx",
                    "source_block_id": "block_01",
                    "page": 1,
                    "slide": 1,
                    "sheet": None,
                    "extracted_text_snippet": "Duelens Inc - Pitch Presentation"
                }
            }
        }
        raw_response_str = json.dumps(mock_json_response)
        
        # Test JSON repair and Pydantic validation
        repaired = JSONRepairer.repair_json_data(raw_response_str, self.pitch_deck_template)
        self.assertEqual(repaired["company_identity"]["company_name"]["value"], "Duelens Inc")
        
        errors = FactValidator.perform_validation(repaired, "pitch_deck", self.pitch_deck_template)
        self.assertEqual(len(errors), 0, f"Validation failed: {errors}")

    def test_invalid_gemini_response(self):
        """Test how the JSONRepairer handles an invalid, empty, or corrupted Gemini response."""
        corrupt_response = "This is not JSON at all! {unbalanced: dict"
        repaired = JSONRepairer.repair_json_data(corrupt_response, self.pitch_deck_template)
        # Should gracefully fall back to the empty template structure
        self.assertIsNotNone(repaired)
        self.assertIsNone(repaired["company_identity"]["company_name"]["value"])

    def test_repair_success(self):
        """Test that types (like numeric strings) are successfully coerced and smart quotes are removed."""
        raw_response = """
        {
          "company_identity": {
            "company_name": {
              "value": "Smart \\\"Quotes\\\" Company"
            }
          },
          "traction": {
            "revenue": {
              "value": "12,000,000"
            }
          }
        }
        """
        repaired = JSONRepairer.repair_json_data(raw_response, self.pitch_deck_template)
        # Verify comma cleaning and conversion to integer
        self.assertEqual(repaired["traction"]["revenue"]["value"], 12000000)

    def test_repair_failure_fallback(self):
        """Test repair fallback when template keys are completely missing or value is empty."""
        raw_response = "{}"
        repaired = JSONRepairer.repair_json_data(raw_response, self.pitch_deck_template)
        self.assertIsNone(repaired["company_identity"]["company_name"]["value"])

    def test_traceability_verification_pass(self):
        """Test that valid block references correctly pass traceability checks."""
        doc_json = {
            "company_identity": {
                "company_name": {
                    "value": "Duelens Inc",
                    "unit": None,
                    "period": None,
                    "actual_vs_budget": None,
                    "source_reference": "investor_deck.pptx",
                    "source_block_id": "block_01",
                    "page": 1,
                    "slide": 1,
                    "sheet": None,
                    "extracted_text_snippet": "Duelens Inc"
                }
            }
        }
        is_valid, report = TraceabilityValidator.validate_document(doc_json, self.mock_parsed_doc)
        self.assertTrue(is_valid)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["source_block_id"], "block_01")

    def test_traceability_verification_fail(self):
        """Test that invalid, missing, or mismatched slide/page mappings trigger traceability failures."""
        doc_json = {
            "company_identity": {
                "company_name": {
                    "value": "Duelens Inc",
                    "unit": None,
                    "period": None,
                    "actual_vs_budget": None,
                    "source_reference": "investor_deck.pptx",
                    "source_block_id": "non_existent_block",
                    "page": 2,
                    "slide": 2,
                    "sheet": None,
                    "extracted_text_snippet": "Duelens Inc"
                }
            }
        }
        is_valid, report = TraceabilityValidator.validate_document(doc_json, self.mock_parsed_doc)
        self.assertFalse(is_valid)

    def test_schema_validation_pass(self):
        """Test schema validation on fully valid structured dictionary."""
        errors = FactValidator.validate_schema(self.pitch_deck_template, "pitch_deck")
        self.assertEqual(len(errors), 0)

    def test_schema_validation_fail(self):
        """Test schema validation fails when structure contains invalid primitive type or structure."""
        corrupted_doc = copy.deepcopy(self.pitch_deck_template)
        # Assign string to what should be a dict metric value structure
        corrupted_doc["company_identity"]["company_name"] = "NotADict"
        errors = FactValidator.validate_schema(corrupted_doc, "pitch_deck")
        self.assertTrue(len(errors) > 0)

    def test_corrupted_template(self):
        """Test that validator catches missing template sections during Key validation."""
        corrupted_doc = copy.deepcopy(self.pitch_deck_template)
        del corrupted_doc["company_identity"]
        errors = FactValidator.validate_keys(corrupted_doc, self.pitch_deck_template)
        self.assertTrue(len(errors) > 0)

    def test_corrupted_parsed_document(self):
        """Test that a corrupted parsed document structure throws descriptive parse error."""
        corrupt_parsed_doc_data = {"document_id": "doc123"} # Missing content blocks entirely
        with self.assertRaises(Exception):
            ParsedDocument(**corrupt_parsed_doc_data)

    @patch("app.extractors.gemini.GeminiCaller.call_gemini")
    def test_incremental_chunk_cache_hits(self, mock_gemini):
        """
        Incremental Cache Test: Verify that when only one chunk of a document changes,
        only the changed chunk triggers Gemini call, while the unchanged chunk is loaded from cache.
        """
        # Create temp folder to act as outputs directory
        temp_dir = tempfile.mkdtemp()
        original_output_dir = settings.OUTPUT_DIR
        settings.OUTPUT_DIR = temp_dir
        
        try:
            company_id = "test_inc_company"
            company_cache_dir = os.path.join(temp_dir, company_id, "cache")
            os.makedirs(company_cache_dir, exist_ok=True)
            
            # Setup two content blocks (chunks)
            b1 = ContentBlock(
                id="b1", sequence=1, content_type="text", page=1, slide=1, raw_text="First chunk",
                source=BlockSource(file="doc.pdf", page=1, slide=1, sheet=None)
            )
            b2 = ContentBlock(
                id="b2", sequence=2, content_type="text", page=2, slide=2, raw_text="Second chunk",
                source=BlockSource(file="doc.pdf", page=2, slide=2, sheet=None)
            )
            
            # 1. Warm chunk cache for the first chunk (b1)
            b1_blocks_str = json.dumps([b1.model_dump()])
            template_json_str = json.dumps(self.pitch_deck_template)
            registry_version = SpecificationRegistry.get_version()
            
            b1_hash = FactCache.generate_chunk_hash(b1_blocks_str, template_json_str, registry_version)
            mock_extracted_chunk_data = copy.deepcopy(self.pitch_deck_template)
            mock_extracted_chunk_data["company_identity"]["company_name"] = {
                "value": "Duelens", "unit": None, "period": None, "actual_vs_budget": None,
                "source_reference": "doc.pdf", "source_block_id": "b1", "page": 1, "slide": 1, "sheet": None,
                "extracted_text_snippet": "First chunk"
            }
            
            # Save b1 to chunk cache on disk
            FactCache.save_chunk(company_id, b1_hash, mock_extracted_chunk_data)
            
            # Setup mock Gemini return for the second chunk (b2)
            mock_gemini_payload = {
                "traction": {
                    "revenue": {
                        "value": 15000000, "unit": "INR", "period": "FY25", "actual_vs_budget": None,
                        "source_reference": "doc.pdf", "source_block_id": "b2", "page": 2, "slide": 2, "sheet": None,
                        "extracted_text_snippet": "Second chunk"
                    }
                }
            }
            mock_gemini.return_value = json.dumps(mock_gemini_payload)
            
            # Call extraction pipeline orchestrator with both blocks (b1 and b2)
            # Chunker will split them into chunks. Let's chunk manually or patch Chunker to return [[b1], [b2]]
            with patch("app.extractors.chunker.Chunker.chunk_document", return_value=[[b1], [b2]]):
                # Setup parsed document on disk
                parsed_doc_data = ParsedDocument(
                    document_id="doc1", document_name="doc.pdf", document_type="pitch_deck",
                    metadata=self.mock_metadata, content=[b1, b2]
                )
                
                doc_file_name = "doc.json"
                doc_path = os.path.join(temp_dir, company_id, doc_file_name)
                os.makedirs(os.path.dirname(doc_path), exist_ok=True)
                with open(doc_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_doc_data.model_dump(), f, indent=2)
                    
                # Create manifest
                manifest_data = {
                    "company_id": company_id,
                    "documents": [
                        {
                            "document_id": "doc1", "file_name": "doc.pdf", "document_type": "pitch_deck",
                            "status": "parsed", "parser": "PDFParser", "output_file": doc_file_name
                        }
                    ]
                }
                manifest_path = os.path.join(temp_dir, company_id, "manifest.json")
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest_data, f, indent=2)
                    
                # Run fact extraction
                manifest_res, stats = FactExtractor.extract_company_facts(company_id)
                
                # Check call counts: Gemini Caller should be called EXACTLY once (only for chunk b2, b1 hit cache!)
                self.assertEqual(mock_gemini.call_count, 1)
                self.assertEqual(stats["cache_hits"], 1) # Chunk cache hit
                self.assertEqual(stats["cache_misses"], 1) # Chunk cache miss
                
        finally:
            settings.OUTPUT_DIR = original_output_dir
            shutil.rmtree(temp_dir)
