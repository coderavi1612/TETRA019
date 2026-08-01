import time
from typing import Dict

class PerformanceTracker:
    def __init__(self):
        self.timings: Dict[str, float] = {
            "startup_time_ms": 0.0,
            "document_load_time_ms": 0.0,
            "chunking_time_ms": 0.0,
            "prompt_build_time_ms": 0.0,
            "gemini_time_ms": 0.0,
            "repair_time_ms": 0.0,
            "validation_time_ms": 0.0,
            "merge_time_ms": 0.0,
            "verification_time_ms": 0.0,
            "manifest_generation_time_ms": 0.0,
            "total_time_ms": 0.0
        }
        self._start_times: Dict[str, float] = {}

    def start(self, name: str) -> None:
        self._start_times[name] = time.time()

    def stop(self, name: str) -> None:
        if name in self._start_times:
            duration_ms = (time.time() - self._start_times[name]) * 1000.0
            self.timings[name] = self.timings.get(name, 0.0) + duration_ms
            del self._start_times[name]

    def record(self, name: str, value_ms: float) -> None:
        self.timings[name] = value_ms

    def get_timings(self) -> Dict[str, int]:
        return {k: int(round(v)) for k, v in self.timings.items()}
