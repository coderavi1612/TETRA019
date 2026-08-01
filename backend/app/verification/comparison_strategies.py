from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from app.verification.tolerance import ToleranceEngine

class BaseComparator(ABC):
    @abstractmethod
    def compare(self, val1: Any, val2: Any, tolerance: Optional[str] = None) -> str:
        """
        Compares two normalized values.
        Returns one of: 'Verified Match', 'Within Tolerance', 'Mismatch'
        """
        pass

class NumericComparator(BaseComparator):
    def compare(self, val1: Any, val2: Any, tolerance: Optional[str] = None) -> str:
        if val1 is None or val2 is None:
            return "Mismatch"
        try:
            v1 = float(val1)
            v2 = float(val2)
        except (ValueError, TypeError):
            return "Mismatch"

        if v1 == v2:
            return "Verified Match"
        if tolerance:
            if ToleranceEngine.is_within_tolerance(v1, v2, tolerance):
                return "Within Tolerance"
        return "Mismatch"

class StringComparator(BaseComparator):
    def compare(self, val1: Any, val2: Any, tolerance: Optional[str] = None) -> str:
        s1 = str(val1).strip().lower() if val1 is not None else ""
        s2 = str(val2).strip().lower() if val2 is not None else ""
        return "Verified Match" if s1 == s2 else "Mismatch"

class DateComparator(BaseComparator):
    def compare(self, val1: Any, val2: Any, tolerance: Optional[str] = None) -> str:
        d1 = str(val1).strip().lower() if val1 is not None else ""
        d2 = str(val2).strip().lower() if val2 is not None else ""
        # Standardize space and simple year strings
        d1 = d1.replace(" ", "").replace("-", "")
        d2 = d2.replace(" ", "").replace("-", "")
        return "Verified Match" if d1 == d2 else "Mismatch"

class CurrencyComparator(BaseComparator):
    def compare(self, val1: Any, val2: Any, tolerance: Optional[str] = None) -> str:
        c1 = str(val1).strip().lower() if val1 is not None else ""
        c2 = str(val2).strip().lower() if val2 is not None else ""
        return "Verified Match" if c1 == c2 else "Mismatch"

class BooleanComparator(BaseComparator):
    def compare(self, val1: Any, val2: Any, tolerance: Optional[str] = None) -> str:
        def to_bool(v: Any) -> bool:
            if isinstance(v, str):
                return v.strip().lower() in ("true", "1", "yes")
            return bool(v)
        b1 = to_bool(val1) if val1 is not None else False
        b2 = to_bool(val2) if val2 is not None else False
        return "Verified Match" if b1 == b2 else "Mismatch"

class OwnershipComparator(BaseComparator):
    def compare(self, val1: Any, val2: Any, tolerance: Optional[str] = None) -> str:
        # Ownership requires near-exact percentage matching
        if val1 is None or val2 is None:
            return "Mismatch"
        try:
            v1 = float(val1)
            v2 = float(val2)
        except (ValueError, TypeError):
            return "Mismatch"

        # Match exactly or within 0.05%
        if abs(v1 - v2) <= 0.0005:
            return "Verified Match"
        return "Mismatch"

# Comparison Strategy Registry
COMPARISON_STRATEGIES: Dict[str, BaseComparator] = {
    "numeric": NumericComparator(),
    "string": StringComparator(),
    "date": DateComparator(),
    "currency": CurrencyComparator(),
    "boolean": BooleanComparator(),
    "ownership": OwnershipComparator()
}
