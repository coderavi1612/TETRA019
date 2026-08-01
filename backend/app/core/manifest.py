from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, Any, List

def get_utc_now_iso() -> str:
    # Safely generates timezone-aware ISO string to prevent DeprecationWarning
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "") + "Z"

class BaseManifest(BaseModel):
    schema_version: str = "1.0"
    pipeline_version: str = "1.0"
    generated_at: str = Field(default_factory=get_utc_now_iso)
    processing_time_ms: int = 0
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    versions: Dict[str, str] = Field(default_factory=dict)
