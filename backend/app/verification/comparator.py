from typing import Any, Optional
from app.verification.comparison_registry import ComparisonRegistry
from app.verification.comparison_strategies import COMPARISON_STRATEGIES

class Comparator:
    @staticmethod
    def compare_values(canonical_field: str, val1: Any, val2: Any) -> str:
        strategy = ComparisonRegistry.get_comparison_strategy(canonical_field) or "string"
        comparator_instance = COMPARISON_STRATEGIES.get(strategy, COMPARISON_STRATEGIES["string"])
        
        tolerance = ComparisonRegistry.get_tolerance(canonical_field)
        return comparator_instance.compare(val1, val2, tolerance)
