import os
import json
import time
import logging
from typing import Dict, List, Any
from app.config import settings
from app.verification.comparison_registry import ComparisonRegistry
from app.verification.mapper import CanonicalFieldMapper
from app.verification.matrix import ComparisonMatrixBuilder
from app.verification.resolver import ConflictResolver
from app.verification.classifier import FieldClassifier
from app.verification.evidence import EvidenceBuilder
from app.verification.report import ReportBuilder
from app.verification.manifest import ManifestBuilder
from app.verification.schemas import (
    ComparisonMatrix,
    ComparisonSummary,
    Issue,
    Evidence,
    VerificationManifest,
    VerifyApiResponse
)

logger = logging.getLogger(__name__)

class VerificationOrchestrator:
    @staticmethod
    def run_verification(company_id: str) -> VerifyApiResponse:
        start_time = time.perf_counter()
        
        company_output_dir = os.path.join(settings.OUTPUT_DIR, company_id)
        if not os.path.exists(company_output_dir):
            raise FileNotFoundError(f"Outputs directory for company '{company_id}' not found.")

        manifest_path = os.path.join(company_output_dir, "manifests", "manifest.json")
        if not os.path.exists(manifest_path):
            manifest_path = os.path.join(company_output_dir, "manifest.json")
            
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Ingestion manifest not found for company '{company_id}'.")

        with open(manifest_path, "r", encoding="utf-8") as f:
            ingestion_manifest = json.load(f)

        documents_list = ingestion_manifest.get("documents", [])
        documents_compared_count = len(documents_list)

        # 1. Map canonical fields across all parsed/extracted documents
        all_mapped_values = []
        for doc_item in documents_list:
            doc_type = doc_item.get("document_type")
            output_file = doc_item.get("output_file")
            status = doc_item.get("status")

            if status != "parsed" or not output_file:
                continue

            # Check extracted first, then parsed, then legacy root folder
            doc_path = os.path.join(company_output_dir, "extracted", output_file)
            if not os.path.exists(doc_path):
                doc_path = os.path.join(company_output_dir, "parsed", output_file)
            if not os.path.exists(doc_path):
                doc_path = os.path.join(company_output_dir, output_file)
                
            if not os.path.exists(doc_path):
                logger.warning(f"Expected parsed/extracted document file not found: {doc_path}")
                continue

            with open(doc_path, "r", encoding="utf-8") as f:
                doc_json = json.load(f)

            # Map values
            mapped = CanonicalFieldMapper.map_document(doc_type, doc_json, ComparisonRegistry.get_rules())
            all_mapped_values.extend(mapped)

        # 2. Build Comparison Matrix (in-memory)
        matrix = ComparisonMatrixBuilder.build_matrix(all_mapped_values)

        # 3. Save Matrix and Mappings
        verification_output_dir = os.path.join(company_output_dir, "verification")
        ComparisonMatrixBuilder.save_reports(matrix, verification_output_dir)

        # 4. Compare, Resolve and Classify
        issues: List[Issue] = []
        evidence_map: Dict[str, List[Evidence]] = {}
        graph_data: Dict[str, Any] = {}
        failures: List[Dict[str, str]] = []

        matches = 0
        close_matches = 0
        verified_mismatches = 0
        missing_information = 0
        unresolved_inconsistencies = 0

        # Gather all rules to compare (including dynamically expanded dynamic rules)
        fields_to_compare = set()
        for name in ComparisonRegistry.list_all_fields():
            if "<" not in name and ">" not in name:
                fields_to_compare.add(name)
        # Add dynamic ones present in the matrix
        for m_key in matrix.matrix.keys():
            if "<" not in m_key and ">" not in m_key:
                fields_to_compare.add(m_key)

        sorted_fields = sorted(list(fields_to_compare))
        
        for idx, field_name in enumerate(sorted_fields):
            try:
                comp_id = f"CMP-{idx+1:06d}"
                docs_dict = matrix.matrix.get(field_name, {})

                # Available documents having a non-null value
                available_docs = [
                    d_type for d_type, val in docs_dict.items()
                        if val.normalized_value is not None
                ]

                # Resolve Conflict
                resolved = ConflictResolver.resolve_field(field_name, docs_dict)

                # Classify Discrepancy
                classified = FieldClassifier.classify(field_name, resolved, available_docs)

                # Build Evidence
                evs = EvidenceBuilder.build_evidence(field_name, docs_dict)

                # Populate Graph Data
                graph_data[field_name] = {
                    "authoritative": resolved.authoritative_document,
                    "comparison_id": comp_id,
                    "documents": [
                        {
                            "document": d_type,
                            "value": val.value,
                            "normalized": val.normalized_value
                        } for d_type, val in docs_dict.items()
                    ]
                }

                # Update counters
                status = classified.status
                if status == "Verified Match":
                    matches += 1
                elif status == "Within Tolerance":
                    close_matches += 1
                elif status == "Verified Mismatch":
                    verified_mismatches += 1
                elif status == "Missing Information":
                    missing_information += 1
                elif status == "Unresolved Inconsistency":
                    unresolved_inconsistencies += 1

                # If issue, add to list
                if classified.is_issue:
                    issues.append(Issue(
                        id=comp_id,
                        classification=classified.status,
                        severity=classified.severity,
                        field=field_name,
                        description=classified.description,
                        documents=available_docs,
                        evidence=evs
                    ))
                    evidence_map[comp_id] = evs

            except Exception as e:
                logger.error(f"Failed to compare field '{field_name}': {str(e)}")
                failures.append({
                    "field": field_name,
                    "error": str(e)
                })

        # 5. Build and Save Reports
        summary = ComparisonSummary(
            documents_compared=documents_compared_count,
            canonical_fields=len(sorted_fields),
            matched=matches,
            close_matches=close_matches,
            verified_mismatches=verified_mismatches,
            missing_information=missing_information,
            unresolved_inconsistencies=unresolved_inconsistencies
        )

        from app.readiness.scoring import ReadinessScoringEngine
        issues_dict_list = [issue.model_dump() for issue in issues]
        stats_dict = summary.model_dump()
        scoring = ReadinessScoringEngine.calculate_score_and_status(issues_dict_list, stats_dict)
        docs_reviewed = [d.get("document_type") for d in documents_list if d.get("status") == "parsed"]

        ReportBuilder.save_reports(
            verification_output_dir,
            company_id,
            summary,
            issues,
            evidence_map,
            graph_data,
            matrix,
            sorted_fields,
            scoring,
            docs_reviewed
        )

        # 6. Save Manifest
        end_time = time.perf_counter()
        elapsed_ms = int((end_time - start_time) * 1000)

        from app.core import PIPELINE_VERSION, get_utc_now_iso
        manifest = VerificationManifest(
            pipeline_version=PIPELINE_VERSION,
            generated_at=get_utc_now_iso(),
            registry_version=ComparisonRegistry.get_hash()[:16],
            comparison_rules_hash=ComparisonRegistry.get_hash(),
            fields_compared=len(sorted_fields),
            matches=matches,
            close_matches=close_matches,
            verified_mismatches=verified_mismatches,
            missing_information=missing_information,
            unresolved_inconsistencies=unresolved_inconsistencies,
            processing_time_ms=elapsed_ms,
            failures=failures
        )
        # Save manifest under unified manifests/ directory
        manifests_dir = os.path.join(company_output_dir, "manifests")
        os.makedirs(manifests_dir, exist_ok=True)
        ManifestBuilder.save_manifest(manifest, manifests_dir)

        # Determine verification status (FAIL if there are mismatch issues)
        verification_status = "PASS"
        if verified_mismatches > 0 or unresolved_inconsistencies > 0:
            verification_status = "FAIL"

        return VerifyApiResponse(
            company_id=company_id,
            documents_compared=documents_compared_count,
            canonical_fields=len(sorted_fields),
            issues_generated=len(issues),
            verification_status=verification_status,
            processing_time_ms=elapsed_ms,
            failed_documents=[f.get("field", "") for f in failures] if failures else [],
            warnings=[],
            errors=[f.get("error", "") for f in failures] if failures else []
        )
