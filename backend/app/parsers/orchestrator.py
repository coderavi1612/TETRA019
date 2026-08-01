import os
import datetime
import json
from typing import List, Dict, Any

from app.config import settings
from app.parsers.classifier import DocumentClassifier
from app.parsers.factory import ParserFactory
from app.schemas.parsed_document import (
    ParsedDocument, DocumentMetadata, ParserInfo, DocumentStatistics,
    ManifestDocument, Manifest
)
from app.core.logging import DuelensLogger
from app.core.timing import Timer

class DocumentParserOrchestrator:
    @staticmethod
    def run_parse(company_id: str) -> Dict[str, Any]:
        clean_company_id = company_id.strip()
        if not clean_company_id:
            raise ValueError("company_id cannot be empty or whitespace.")

        DuelensLogger.log("Parsing", "START", f"Starting document parsing for company: {clean_company_id}")
        
        with Timer() as timer:
            # 1. Locate upload folder
            company_upload_dir = os.path.join(settings.UPLOAD_DIR, clean_company_id)
            if not os.path.exists(company_upload_dir) or not os.path.isdir(company_upload_dir):
                raise FileNotFoundError(f"No upload directory found for company '{clean_company_id}'.")

            # Scan for uploaded files, ignoring hidden files
            files = [
                f for f in os.listdir(company_upload_dir)
                if os.path.isfile(os.path.join(company_upload_dir, f)) and not f.startswith(".")
            ]
            
            if not files:
                raise FileNotFoundError(f"No files found in the upload directory for company '{clean_company_id}'.")

            # 2. Establish target output folder
            # Note: We now support standardizing outputs under standard folders, but parsed goes under parsed/
            company_output_dir = os.path.join(settings.OUTPUT_DIR, clean_company_id)
            parsed_output_dir = os.path.join(company_output_dir, "parsed")
            manifests_output_dir = os.path.join(company_output_dir, "manifests")
            
            os.makedirs(parsed_output_dir, exist_ok=True)
            os.makedirs(manifests_output_dir, exist_ok=True)

            # Remove project_context.json if it exists to strictly follow architecture guidelines
            context_file_path = os.path.join(company_output_dir, "project_context.json")
            if os.path.exists(context_file_path):
                try:
                    os.remove(context_file_path)
                except Exception:
                    pass

            manifest_docs = []
            results = []

            for filename in files:
                file_path = os.path.join(company_upload_dir, filename)
                doc_type = DocumentClassifier.classify(filename)
                
                # Determine output filename based on classification
                if doc_type != "unknown":
                    out_filename = f"{doc_type}.json"
                else:
                    safe_name = "".join([c if c.isalnum() else "_" for c in filename]).lower()
                    out_filename = f"unknown_{safe_name}.json"

                output_file_path = os.path.join(parsed_output_dir, out_filename)
                
                parser_name = "unknown"
                errors = []
                warnings = []
                parsed_doc = None
                
                try:
                    parser = ParserFactory.get_parser(filename)
                    parser_name = parser.__class__.__name__
                    parsed_doc = parser.parse(file_path, clean_company_id, doc_type)
                except Exception as e:
                    err_str = str(e)
                    if "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower() or "429" in err_str:
                        raise ValueError(f"Gemini API Quota/Rate Limit Exhausted during parsing of '{filename}': {err_str}")
                    errors.append(err_str)
                    try:
                        f_size = os.path.getsize(file_path)
                    except Exception:
                        f_size = 0
                    
                    ext = os.path.splitext(filename)[1].lower()
                    
                    parsed_doc = ParsedDocument(
                        document_id=f"{clean_company_id}_{doc_type}",
                        document_name=filename,
                        document_type=doc_type,
                        status="failed",
                        metadata=DocumentMetadata(
                            company_id=clean_company_id,
                            file_size=f_size,
                            extension=ext,
                            mime_type="application/octet-stream",
                            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "") + "Z",
                            parser=ParserInfo(name="failed-parser", version="1.0"),
                            statistics=DocumentStatistics()
                        ),
                        content=[],
                        warnings=warnings,
                        errors=errors
                    )

                # Write parsed document JSON output
                try:
                    doc_json_content = parsed_doc.model_dump_json(indent=2)
                    with open(output_file_path, "w", encoding="utf-8") as out_f:
                        out_f.write(doc_json_content)
                    
                    # Generate and write canonical document/workbook
                    if parsed_doc.status == "parsed":
                        canonical_dir = os.path.join(company_output_dir, "canonical")
                        os.makedirs(canonical_dir, exist_ok=True)
                        canonical_output_path = os.path.join(canonical_dir, out_filename.replace(".json", ".canonical.json"))
                        
                        from app.parsers.canonical import CanonicalBuilder
                        if doc_type == "cap_table" or filename.lower().endswith((".xlsx", ".xls", ".csv")):
                            canonical_obj = CanonicalBuilder.build_workbook(parsed_doc, file_path)
                        else:
                            canonical_obj = CanonicalBuilder.build_document(parsed_doc)
                            
                        with open(canonical_output_path, "w", encoding="utf-8") as can_f:
                            json.dump(canonical_obj.model_dump(), can_f, indent=2)
                except Exception as e:
                    parsed_doc.status = "failed"
                    parsed_doc.errors.append(f"Failed to write output to file system: {str(e)}")
                    try:
                        parsed_doc.content = []
                        doc_json_content = parsed_doc.model_dump_json(indent=2)
                        with open(output_file_path, "w", encoding="utf-8") as out_f:
                            out_f.write(doc_json_content)
                    except Exception:
                        pass

                manifest_docs.append(
                    ManifestDocument(
                        document_id=parsed_doc.document_id,
                        file_name=filename,
                        document_type=doc_type,
                        status=parsed_doc.status,
                        parser=parser_name,
                        output_file=out_filename
                    )
                )

                results.append({
                    "file_name": filename,
                    "document_type": doc_type,
                    "status": parsed_doc.status,
                    "blocks": len(parsed_doc.content),
                    "errors": parsed_doc.errors
                })

            # Compile and write manifest.json
            manifest = Manifest(
                company_id=clean_company_id,
                documents=manifest_docs
            )
            
            manifest_path = os.path.join(manifests_output_dir, "manifest.json")
            manifest_json_content = manifest.model_dump_json(indent=2)
            with open(manifest_path, "w", encoding="utf-8") as manifest_f:
                manifest_f.write(manifest_json_content)

        DuelensLogger.log("Parsing", "END", f"Completed document parsing in {timer.elapsed_ms}ms")
        
        return {
            "company_id": clean_company_id,
            "documents_parsed": len(results),
            "files": results
        }
