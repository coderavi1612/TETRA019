from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseReasoningClient(ABC):
    @abstractmethod
    def generate_reasoning(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes reasoning over aligned comparison context and returns structured reports.
        """
        pass
