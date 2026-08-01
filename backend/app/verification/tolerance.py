class ToleranceEngine:
    @staticmethod
    def is_within_tolerance(val1: float, val2: float, tolerance: str) -> bool:
        if not tolerance:
            return val1 == val2
        tol_clean = tolerance.strip().lower()
        if tol_clean == "exact":
            return val1 == val2
        if tol_clean.endswith("%"):
            try:
                percent = float(tol_clean.replace("%", "").strip()) / 100.0
                if val1 == 0:
                    return val2 == 0
                # Relies on relative difference to the base value
                diff = abs(val1 - val2) / abs(val1)
                return diff <= percent
            except Exception:
                return False
        return val1 == val2
