from typing import Any, Dict, List, Optional
from app.verification.resolver import ResolvedComparison
from app.verification.comparison_registry import ComparisonRegistry

class ClassifiedResult:
    def __init__(self, status: str, severity: str, description: str, is_issue: bool):
        self.status = status
        self.severity = severity
        self.description = description
        self.is_issue = is_issue

class FieldClassifier:
    @staticmethod
    def classify(canonical_field: str, resolved: ResolvedComparison, available_docs: List[str]) -> ClassifiedResult:
        rule = ComparisonRegistry.get_field(canonical_field)
        default_severity = rule.get("severity", "MEDIUM") if rule else "MEDIUM"
        is_required = rule.get("required", False) if rule else False
        
        # 1. Match / Within Tolerance
        if resolved.comparison_result in ("Verified Match", "Within Tolerance"):
            return ClassifiedResult(
                status=resolved.comparison_result,
                severity=default_severity,
                description=f"Field '{canonical_field}' is consistent across all documents.",
                is_issue=False
            )
            
        # 2. Missing Information
        if resolved.comparison_result == "Missing Information":
            desc = f"Required field '{canonical_field}' is missing entirely."
            if available_docs:
                desc = f"Field '{canonical_field}' is present in {available_docs} but missing in other documents."
            is_issue = is_required or len(available_docs) > 0
            return ClassifiedResult(
                status="Missing Information",
                severity=default_severity if is_required else "LOW",
                description=desc,
                is_issue=is_issue
            )
            
        # 3. Mismatch
        if resolved.comparison_result == "Mismatch":
            if resolved.is_resolvable:
                desc = (
                    f"Verified Mismatch for field '{canonical_field}'. "
                    f"Authoritative source '{resolved.authoritative_document}' has value '{resolved.authoritative_value}', "
                    f"which conflicts with other documents."
                )
                return ClassifiedResult(
                    status="Verified Mismatch",
                    severity=default_severity,
                    description=desc,
                    is_issue=True
                )
            else:
                desc = (
                    f"Unresolved Inconsistency for field '{canonical_field}'. "
                    f"Conflicting values exist across documents, but no authoritative priority is defined."
                )
                return ClassifiedResult(
                    status="Unresolved Inconsistency",
                    severity=default_severity,
                    description=desc,
                    is_issue=True
                )
                
        return ClassifiedResult(
            status="Unknown",
            severity="LOW",
            description=f"Unknown comparison status for field '{canonical_field}'.",
            is_issue=False
        )
