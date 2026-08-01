import unittest
import os
import json
from app.verification.normalizer import FieldNormalizer
from app.verification.tolerance import ToleranceEngine
from app.verification.comparison_registry import ComparisonRegistry
from app.verification.mapper import CanonicalFieldMapper
from app.verification.matrix import ComparisonMatrixBuilder
from app.verification.resolver import ConflictResolver
from app.verification.classifier import FieldClassifier
from app.verification.comparator import Comparator
from app.verification.evidence import EvidenceBuilder
from app.verification.schemas.comparison import MappedValue, NormalizedValue

class TestVerificationEngine(unittest.TestCase):
    def test_field_normalization(self):
        # 1. Period normalization
        self.assertEqual(FieldNormalizer.normalize_period("FY 2024"), "FY24")
        self.assertEqual(FieldNormalizer.normalize_period("2023-24"), "FY24")
        self.assertEqual(FieldNormalizer.normalize_period("2024"), "FY24")
        self.assertEqual(FieldNormalizer.normalize_period("FY24"), "FY24")
        
        # 2. Currency normalization
        self.assertEqual(FieldNormalizer.normalize_currency("₹"), "INR")
        self.assertEqual(FieldNormalizer.normalize_currency("INR"), "INR")
        self.assertEqual(FieldNormalizer.normalize_currency("$"), "USD")
        self.assertEqual(FieldNormalizer.normalize_currency("usd"), "USD")
        
        # 3. Numeric conversions
        v_cr, unit_cr = FieldNormalizer.normalize_value("₹25 Cr", "numeric")
        self.assertEqual(v_cr, 250000000.0)
        
        v_lakh, unit_lakh = FieldNormalizer.normalize_value("35 Lakhs", "numeric")
        self.assertEqual(v_lakh, 3500000.0)
        
        v_pct, unit_pct = FieldNormalizer.normalize_value("25%", "numeric")
        self.assertEqual(v_pct, 0.25)
        self.assertEqual(unit_pct, "%")

    def test_tolerance_engine(self):
        self.assertTrue(ToleranceEngine.is_within_tolerance(100.0, 102.0, "2%"))
        self.assertTrue(ToleranceEngine.is_within_tolerance(100.0, 98.0, "2%"))
        self.assertFalse(ToleranceEngine.is_within_tolerance(100.0, 103.0, "2%"))
        self.assertTrue(ToleranceEngine.is_within_tolerance(10.0, 10.0, "Exact"))
        self.assertFalse(ToleranceEngine.is_within_tolerance(10.0, 10.1, "Exact"))

    def test_comparator_and_strategies(self):
        # Test numeric strategy with tolerance
        res1 = Comparator.compare_values("Revenue.FY24", 100.0, 101.5)
        self.assertEqual(res1, "Within Tolerance") # 2% default tolerance
        
        res2 = Comparator.compare_values("Revenue.FY24", 100.0, 103.0)
        self.assertEqual(res2, "Mismatch")
        
        # Test exact string strategy
        res3 = Comparator.compare_values("CompanyLegalName", "Acme Corp", "ACME CORP")
        self.assertEqual(res3, "Verified Match")

    def test_conflict_resolver(self):
        docs = {
            "historical_financial_statements": NormalizedValue(
                document_type="historical_financial_statements",
                original_path="dummy",
                canonical_path="Revenue.FY24",
                value="100 Cr",
                normalized_value=1000000000.0
            ),
            "pitch_deck": NormalizedValue(
                document_type="pitch_deck",
                original_path="dummy",
                canonical_path="Revenue.FY24",
                value="98 Cr",
                normalized_value=980000000.0
            ),
            "financial_projections": NormalizedValue(
                document_type="financial_projections",
                original_path="dummy",
                canonical_path="Revenue.FY24",
                value="120 Cr",
                normalized_value=1200000000.0
            )
        }
        resolved = ConflictResolver.resolve_field("Revenue.FY24", docs)
        self.assertEqual(resolved.authoritative_document, "historical_financial_statements")
        self.assertEqual(resolved.authoritative_value, 1000000000.0)
        self.assertEqual(resolved.comparison_result, "Mismatch")
        self.assertTrue(resolved.is_resolvable)

    def test_classifier(self):
        from app.verification.resolver import ResolvedComparison
        # 1. Verified Mismatch
        resolved_resolvable = ResolvedComparison(
            authoritative_document="historical_financial_statements",
            authoritative_value=100.0,
            comparison_result="Mismatch",
            is_resolvable=True
        )
        c1 = FieldClassifier.classify("Revenue.FY24", resolved_resolvable, ["historical_financial_statements", "pitch_deck"])
        self.assertEqual(c1.status, "Verified Mismatch")
        self.assertTrue(c1.is_issue)
        
        # 2. Unresolved Inconsistency
        resolved_unresolvable = ResolvedComparison(
            authoritative_document="pitch_deck",
            authoritative_value=100.0,
            comparison_result="Mismatch",
            is_resolvable=False
        )
        c2 = FieldClassifier.classify("Revenue.FY24", resolved_unresolvable, ["pitch_deck", "financial_projections"])
        self.assertEqual(c2.status, "Unresolved Inconsistency")
        self.assertTrue(c2.is_issue)

    def test_registry_validation_checks(self):
        # Validate loader works
        ComparisonRegistry.load()
        self.assertTrue(ComparisonRegistry._loaded)
        self.assertIsNotNone(ComparisonRegistry.get_hash())
        
        # Verify get field pattern matching works
        rule = ComparisonRegistry.get_field("Ownership.Founder_A")
        self.assertIsNotNone(rule)
        self.assertEqual(rule["strategy"], "ownership")
