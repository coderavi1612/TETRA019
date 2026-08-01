import os
import json
import logging
from typing import Dict, Any, List

from app.config import settings
from app.verification.comparison_registry import ComparisonRegistry
from app.verification.mapper import CanonicalFieldMapper

logger = logging.getLogger(__name__)

class ComparisonContextBuilder:
    @staticmethod
    def build_context(company_id: str) -> Dict[str, Any]:
        """
        Loads extracted JSON documents, maps their fields, groups them by canonical parameters,
        and saves comparison_context.json inside context/ folder.
        """
        company_output_dir = os.path.join(settings.OUTPUT_DIR, company_id)
        if not os.path.exists(company_output_dir):
            raise FileNotFoundError(f"Outputs folder for company '{company_id}' not found.")

        # Load manifest to find extracted files
        manifest_path = os.path.join(company_output_dir, "manifests", "manifest.json")
        if not os.path.exists(manifest_path):
            manifest_path = os.path.join(company_output_dir, "manifest.json")
        
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Ingestion manifest not found for company '{company_id}'.")

        with open(manifest_path, "r", encoding="utf-8") as f:
            ingestion_manifest = json.load(f)

        documents_list = ingestion_manifest.get("documents", [])
        
        ComparisonRegistry.load()
        rules = ComparisonRegistry.get_rules()

        documents_present = []
        metrics_mapping: Dict[str, Dict[str, Any]] = {}
        missing_fields: List[Dict[str, Any]] = []
        global_entities = {}

        # 1. Load each extracted document and map values
        for doc_item in documents_list:
            doc_type = doc_item.get("document_type")
            output_file = doc_item.get("output_file")
            status = doc_item.get("status")

            if status != "parsed" or not output_file:
                continue

            extracted_path = os.path.join(company_output_dir, "extracted", output_file)
            if not os.path.exists(extracted_path):
                # Fallback to parsed if extraction was skipped, to keep pipeline resilient
                extracted_path = os.path.join(company_output_dir, "parsed", output_file)
            if not os.path.exists(extracted_path):
                extracted_path = os.path.join(company_output_dir, output_file)

            if not os.path.exists(extracted_path):
                continue

            documents_present.append(doc_type)

            with open(extracted_path, "r", encoding="utf-8") as f:
                doc_json = json.load(f)

            # Map values
            mapped = CanonicalFieldMapper.map_document(doc_type, doc_json, rules)
            
            # Group by canonical path
            for mapped_val in mapped:
                c_path = mapped_val.canonical_path
                if c_path not in metrics_mapping:
                    metrics_mapping[c_path] = {}

                # Check if raw value contains dict with confidence and embedded evidence
                val_raw = mapped_val.value
                confidence = 1.0
                evidence = {
                    "page": mapped_val.page,
                    "slide": mapped_val.slide,
                    "sheet": mapped_val.sheet,
                    "block_id": mapped_val.source_block_id
                }

                # Extract confidence from embedded schemas if structured
                if isinstance(val_raw, dict):
                    confidence = val_raw.get("confidence", 1.0)
                    evidence_embedded = val_raw.get("evidence")
                    if isinstance(evidence_embedded, dict):
                        evidence.update(evidence_embedded)
                    val_raw = val_raw.get("value")

                metrics_mapping[c_path][doc_type] = {
                    "value": val_raw,
                    "unit": mapped_val.unit,
                    "currency": mapped_val.currency,
                    "confidence": confidence,
                    "evidence": evidence
                }

        # 2. Identify candidate comparisons and missing fields
        candidate_comparisons = []
        for c_path, doc_vals in metrics_mapping.items():
            # If present in 2 or more documents, it is a candidate for cross-document comparison
            if len(doc_vals) >= 2:
                candidate_comparisons.append(c_path)

            # Check if any expected document in the rule registry mappings is missing
            rule_def = ComparisonRegistry.get_field(c_path)
            if rule_def:
                for expected_doc in rule_def.get("mappings", {}).keys():
                    if expected_doc in documents_present and expected_doc not in doc_vals:
                        missing_fields.append({
                            "field": c_path,
                            "missing_in_document": expected_doc,
                            "priority": rule_def.get("required", False)
                        })

        # Load global entities (like company name and currency) if available
        if "company_identity.company_name" in metrics_mapping:
            vals = metrics_mapping["company_identity.company_name"]
            global_entities["company_name"] = next((v["value"] for v in vals.values() if v.get("value")), None)
        if "company_identity.currency" in metrics_mapping:
            vals = metrics_mapping["company_identity.currency"]
            global_entities["currency"] = next((v["value"] for v in vals.values() if v.get("value")), None)

        # 3. Create context JSON
        import datetime
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "") + "Z"
        context_payload = {
            "metadata": {
                "schema_version": "1.0.0",
                "pipeline_version": "1.0.0",
                "created_by": "Duelens Context Builder",
                "generated_at": now_str
            },
            "company": {
                "company_name": global_entities.get("company_name"),
                "currency": global_entities.get("currency")
            },
            "documents": documents_present,
            "entities": global_entities,
            "metrics": metrics_mapping,
            "relationships": {},  # Can be expanded dynamically
            "candidate_comparisons": sorted(candidate_comparisons),
            "cross_references": {},
            "missing_fields": missing_fields,
            "reasoning_prompt": (
                "Review the mapped financial metrics and identify any discrepancies, narrative contradictions, "
                "or risk assumptions between the startup's pitch deck, financial statements, and projections."
            )
        }

        # Write to outputs/{company_id}/context/comparison_context.json
        context_dir = os.path.join(company_output_dir, "context")
        os.makedirs(context_dir, exist_ok=True)
        context_path = os.path.join(context_dir, "comparison_context.json")
        with open(context_path, "w", encoding="utf-8") as f:
            json.dump(context_payload, f, indent=2)

        logger.info(f"Comparison context built successfully under context/comparison_context.json")
        return context_payload
