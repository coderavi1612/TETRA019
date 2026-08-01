import time
from typing import Dict
from app.core import PerformanceCollector

class PerformanceTracker(PerformanceCollector):
    def __init__(self):
        super().__init__()
        # Preset initial default values
        for name in [
            "startup_time_ms", "document_load_time_ms", "chunking_time_ms",
            "prompt_build_time_ms", "gemini_time_ms", "repair_time_ms",
            "validation_time_ms", "merge_time_ms", "verification_time_ms",
            "manifest_generation_time_ms", "total_time_ms"
        ]:
            self._stages[name] = 0

    def record(self, name: str, value_ms: float) -> None:
        self._stages[name] = int(round(value_ms))

    def stop(self, name: str) -> int:
        if name in self._stages:
            val = self._stages[name]
            # If val is still a start timestamp
            if isinstance(val, float) and val > 1000000000.0:
                duration = int((time.time() - val) * 1000)
                accum_key = f"{name}_accum"
                total_duration = self._stages.get(accum_key, 0) + duration
                self._stages[accum_key] = total_duration
                self._stages[name] = total_duration
                return duration
        return 0
