import time
from typing import Dict

class Timer:
    def __init__(self):
        self.start_time = None
        self.elapsed_ms = 0
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            self.elapsed_ms = int((time.time() - self.start_time) * 1000)

class PerformanceCollector:
    def __init__(self):
        self._stages = {}
        
    def start(self, stage: str) -> None:
        self._stages[stage] = time.time()
        
    def stop(self, stage: str) -> int:
        if stage in self._stages:
            val = self._stages[stage]
            if isinstance(val, (int, float)):
                duration = int((time.time() - val) * 1000)
                self._stages[stage] = duration
                return duration
        return 0
        
    def get_timings(self) -> Dict[str, int]:
        return {stage: val for stage, val in self._stages.items() if isinstance(val, int)}
