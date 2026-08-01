import os
import json
import time
from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.config import settings
from app.core import success_response, error_response, PIPELINE_VERSION, get_utc_now_iso

router = APIRouter()

SUPPORTED_CATEGORIES = {"parsed", "extracted", "verification", "readiness", "manifests", "logs"}

@router.get("/files/{company_id}/{category}/{filename}")
async def get_artifact_file(company_id: str, category: str, filename: str):
    clean_company_id = company_id.strip()
    clean_category = category.strip().lower()
    clean_filename = filename.strip()

    if clean_category not in SUPPORTED_CATEGORIES:
        return error_response(["Invalid artifact category requested."], status_code=400)

    # Resolve safe path
    company_dir = os.path.abspath(os.path.join(settings.OUTPUT_DIR, clean_company_id))
    target_path = os.path.abspath(os.path.join(company_dir, clean_category, clean_filename))
    
    # Path traversal protection
    output_dir_abs = os.path.abspath(settings.OUTPUT_DIR)
    if not target_path.startswith(output_dir_abs):
        return error_response(["Access denied: path traversal detected."], status_code=403)

    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        return error_response([f"File '{clean_filename}' not found in category '{clean_category}'."], status_code=404)

    # Dynamic MIME detection
    extension_to_mime = {
        ".json": "application/json",
        ".pdf": "application/pdf",
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".log": "text/plain"
    }
    ext = os.path.splitext(clean_filename)[1].lower()
    mime = extension_to_mime.get(ext, "application/octet-stream")

    return FileResponse(target_path, media_type=mime, filename=clean_filename)

@router.get("/companies/{company_id}/artifacts")
async def list_company_artifacts(company_id: str):
    clean_company_id = company_id.strip()
    if not clean_company_id:
        return error_response(["company_id cannot be empty."], status_code=400)

    company_dir = os.path.join(settings.OUTPUT_DIR, clean_company_id)
    if not os.path.exists(company_dir):
        return error_response([f"Company '{clean_company_id}' not found."], status_code=404)

    manifest_path = os.path.join(company_dir, "manifests", "artifacts_manifest.json")
    
    # Attempt to read manifest first
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return success_response(data)
        except Exception:
            pass

    # Fallback filesystem scanning if manifest missing
    artifacts = []
    category_to_stage = {
        "parsed": "parse",
        "extracted": "extract",
        "verification": "verify",
        "readiness": "readiness",
        "manifests": "system",
        "logs": "system"
    }
    
    extension_to_mime = {
        ".json": "application/json",
        ".pdf": "application/pdf",
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".log": "text/plain"
    }

    for cat in SUPPORTED_CATEGORIES:
        cat_dir = os.path.join(company_dir, cat)
        if os.path.exists(cat_dir) and os.path.isdir(cat_dir):
            for filename in os.listdir(cat_dir):
                file_path = os.path.join(cat_dir, filename)
                if os.path.isfile(file_path):
                    if filename == "artifacts_manifest.json":
                        continue
                        
                    stat_info = os.stat(file_path)
                    ext = os.path.splitext(filename)[1].lower()
                    mime = extension_to_mime.get(ext, "application/octet-stream")
                    mtime = stat_info.st_mtime
                    generated_at_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime))
                    
                    artifacts.append({
                        "name": filename,
                        "category": cat,
                        "mime_type": mime,
                        "size": stat_info.st_size,
                        "download_url": f"/api/v1/files/{clean_company_id}/{cat}/{filename}",
                        "generated_at": generated_at_iso,
                        "stage": category_to_stage.get(cat, "system")
                    })

    manifest_data = {
        "manifest_version": "1.0",
        "pipeline_version": PIPELINE_VERSION,
        "generated_at": get_utc_now_iso(),
        "company_id": clean_company_id,
        "artifacts": artifacts
    }
    
    return success_response(manifest_data)
