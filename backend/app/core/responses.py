import contextvars
import datetime
from typing import Any, Dict, List
from fastapi.responses import JSONResponse

# ContextVar to hold request_id across async flow
request_id_var = contextvars.ContextVar("request_id", default="")

def success_response(
    data: Any = None, 
    meta: Dict[str, Any] = None, 
    warnings: List[str] = None
) -> Dict[str, Any]:
    """
    Standard successful API response envelope.
    """
    return {
        "success": True,
        "api_version": "v1",
        "request_id": request_id_var.get() or "system",
        "data": data if data is not None else {},
        "meta": meta if meta is not None else {},
        "warnings": warnings if warnings is not None else [],
        "errors": [],
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

def error_response(
    errors: List[str], 
    status_code: int = 400
) -> JSONResponse:
    """
    Standard error API response envelope returned as a JSONResponse.
    """
    content = {
        "success": False,
        "api_version": "v1",
        "request_id": request_id_var.get() or "system",
        "data": {},
        "meta": {},
        "warnings": [],
        "errors": errors,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    return JSONResponse(status_code=status_code, content=content)
