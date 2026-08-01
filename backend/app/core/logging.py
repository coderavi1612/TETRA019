import logging
import sys
from typing import Optional

# Setup standard formatting
def setup_logging() -> None:
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        root.addHandler(handler)
        root.setLevel(logging.INFO)

class DuelensLogger:
    @staticmethod
    def log(stage: str, event: str, message: str, level: int = logging.INFO, error: Optional[Exception] = None) -> None:
        """
        Logs a structured E2E pipeline event format: [<Stage>][<Event>] <message>
        """
        log_msg = f"[{stage}][{event}] {message}"
        if error:
            log_msg += f" | Error: {str(error)}"
            
        logger = logging.getLogger(f"duelens.{stage.lower()}")
        logger.log(level, log_msg)
