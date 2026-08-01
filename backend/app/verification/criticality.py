"""
Field Criticality Matrix loader.

Provides access to the mandatory / optional / negligible field tiers
defined per document type.  Used by the reconciliation engine and the
readiness prompts to weight findings correctly.
"""

import os
import json
import fnmatch
from typing import Optional

_MATRIX_PATH = os.path.join(os.path.dirname(__file__), "criticality_matrix.json")
_CACHE: Optional[dict] = None


def _load() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_MATRIX_PATH, "r", encoding="utf-8") as f:
            _CACHE = json.load(f)
    return _CACHE


class CriticalityMatrix:
    """Accessor for the field‑criticality tiers."""

    @staticmethod
    def load() -> dict:
        """Return the full matrix dict."""
        return _load()

    @staticmethod
    def get_tier(document_type: str, field_path: str) -> str:
        """
        Return ``"mandatory"``, ``"optional"``, or ``"negligible"`` for the
        given *document_type* and dotted *field_path*.

        Matching rules (tried in order):
        1. Exact match against the stored paths.
        2. Glob / wildcard match  (e.g. ``problem_and_solution.*`` matches
           ``problem_and_solution.description``).
        3. Falls back to ``"optional"`` if no match is found.

        Document‑type aliases are normalised so ``"mis_report"`` →
        ``"mis"`` etc.
        """
        # Normalise aliases
        alias_map = {
            "mis_report": "mis",
            "monthly_mis_report": "mis",
            "financial_statement": "historical_financial_statements",
        }
        doc_key = alias_map.get(document_type, document_type)

        matrix = _load()
        doc_entry = matrix.get(doc_key)
        if doc_entry is None:
            return "optional"

        for tier in ("mandatory", "optional", "negligible"):
            paths = doc_entry.get(tier, [])
            for pattern in paths:
                if pattern == field_path:
                    return tier
                # Wildcard match  (e.g. "problem_and_solution.*")
                if fnmatch.fnmatch(field_path, pattern):
                    return tier

        return "optional"

    @staticmethod
    def get_matrix_json() -> str:
        """
        Return the criticality matrix as a compact JSON string, suitable for
        injection into LLM prompts.
        """
        return json.dumps(_load(), indent=2)

    @staticmethod
    def get_mandatory_fields(document_type: str) -> list:
        """Return the list of mandatory field paths for a document type."""
        alias_map = {
            "mis_report": "mis",
            "monthly_mis_report": "mis",
            "financial_statement": "historical_financial_statements",
        }
        doc_key = alias_map.get(document_type, document_type)
        matrix = _load()
        doc_entry = matrix.get(doc_key, {})
        return doc_entry.get("mandatory", [])
