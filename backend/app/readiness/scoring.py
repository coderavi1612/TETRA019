from typing import Dict, Any, List

class ReadinessScoringEngine:
    @staticmethod
    def calculate_score_and_status(issues: List[Dict[str, Any]], stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates deterministic readiness score (0-100), penalties, and overrides.
        """
        score = 100
        penalties = []
        critical_issues_count = 0
        warning_issues_count = 0

        # Penalties:
        # - Verified Mismatch: CRITICAL (-20), HIGH (-10), MEDIUM (-5), LOW (-2)
        # - Unresolved Inconsistency: CRITICAL (-25), HIGH (-15), MEDIUM (-7), LOW (-3)
        # - Missing Information:
        #     Required: CRITICAL (-15), HIGH (-8), MEDIUM (-4), LOW (-1)
        #     Optional: CRITICAL (-5), HIGH (-3), MEDIUM (-1), LOW (0)
        
        for issue in issues:
            classification = issue.get("classification")
            severity = str(issue.get("severity", "LOW")).upper()
            field = issue.get("field", "")
            
            # Check if the field is required from ComparisonRegistry
            from app.verification.comparison_registry import ComparisonRegistry
            rule = ComparisonRegistry.get_field(field)
            is_required = True
            if rule:
                is_required = rule.get("required", True)

            deduction = 0
            if classification == "Verified Mismatch":
                if severity == "CRITICAL":
                    deduction = 20
                    critical_issues_count += 1
                elif severity == "HIGH":
                    deduction = 10
                    warning_issues_count += 1
                elif severity == "MEDIUM":
                    deduction = 5
                else:
                    deduction = 2
            elif classification == "Unresolved Inconsistency":
                if severity == "CRITICAL":
                    deduction = 25
                    critical_issues_count += 1
                elif severity == "HIGH":
                    deduction = 15
                    warning_issues_count += 1
                elif severity == "MEDIUM":
                    deduction = 7
                else:
                    deduction = 3
            elif classification == "Missing Information":
                if is_required:
                    if severity == "CRITICAL":
                        deduction = 15
                        critical_issues_count += 1
                    elif severity == "HIGH":
                        deduction = 8
                        warning_issues_count += 1
                    elif severity == "MEDIUM":
                        deduction = 4
                    else:
                        deduction = 1
                else:
                    if severity == "CRITICAL":
                        deduction = 5
                        critical_issues_count += 1
                    elif severity == "HIGH":
                        deduction = 3
                        warning_issues_count += 1
                    elif severity == "MEDIUM":
                        deduction = 1
                    else:
                        deduction = 0

            if deduction > 0:
                score -= deduction
                penalties.append({
                    "field": field,
                    "classification": classification,
                    "severity": severity,
                    "deduction": deduction
                })

        # Clamp score between 0 and 100
        score = max(0, min(100, score))

        # Base status based on score
        if score >= 90:
            status = "READY"
        elif score >= 70:
            status = "READY_WITH_MINOR_CHANGES"
        elif score >= 40:
            status = "NEEDS_MAJOR_REVIEW"
        else:
            status = "NOT_READY"

        # Overrides:
        # If any CRITICAL verified mismatch or unresolved inconsistency is present, cap status at NEEDS_MAJOR_REVIEW.
        has_critical_inconsistency = False
        for issue in issues:
            classification = issue.get("classification")
            severity = str(issue.get("severity", "LOW")).upper()
            if severity == "CRITICAL" and classification in ("Verified Mismatch", "Unresolved Inconsistency"):
                has_critical_inconsistency = True
                break

        if has_critical_inconsistency and status in ("READY", "READY_WITH_MINOR_CHANGES"):
            status = "NEEDS_MAJOR_REVIEW"

        # If 3 or more CRITICAL issues of any classification are present, overall status is NOT_READY.
        if critical_issues_count >= 3:
            status = "NOT_READY"

        return {
            "readiness_score": score,
            "overall_status": status,
            "penalties": penalties,
            "critical_issues_count": critical_issues_count,
            "warning_issues_count": warning_issues_count
        }
