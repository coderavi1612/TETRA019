from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from typing import List
import os
import shutil

from app.schemas.upload import UploadSuccessResponse, UploadedFileResponse
from app.config import settings

router = APIRouter()

SUPPORTED_EXTENSIONS = {".pdf", ".pptx", ".xlsx", ".csv"}

@router.post("", response_model=UploadSuccessResponse)
async def upload_documents(
    company_id: str = Form(..., description="Unique identifier for the company"),
    files: List[UploadFile] = File(..., description="Fundraising documents to upload")
):
    clean_company_id = company_id.strip()
    if not clean_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="company_id cannot be empty or whitespace."
        )

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files were uploaded."
        )

    # Validate file types before performing any writes
    for file in files:
        filename = file.filename or ""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported file type '{ext}' for file '{filename}'. "
                    f"Supported types are: {', '.join(SUPPORTED_EXTENSIONS)}"
                )
            )

    # Establish target company folder
    company_upload_dir = os.path.join(settings.UPLOAD_DIR, clean_company_id)
    os.makedirs(company_upload_dir, exist_ok=True)

    # Initialize DB run and job
    from app.pipeline.job_manager import JobManager, JobStatus
    from app.core.db import upsert_pipeline_run, save_pipeline_output
    import mimetypes
    
    job_id = JobManager.create_job(clean_company_id)
    try:
        upsert_pipeline_run(job_id, clean_company_id, JobStatus.ACCEPTED.value)
    except Exception:
        pass

    uploaded_files_info = []

    for file in files:
        filename = file.filename or "unnamed_file"
        file_path = os.path.join(company_upload_dir, filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file '{filename}': {str(e)}"
            )
        finally:
            await file.close()

        # Gather details
        size_bytes = os.path.getsize(file_path)
        ext = os.path.splitext(filename)[1].lower()
        mime = file.content_type or mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        # Save uploaded file directly to Supabase DB
        try:
            text_content = None
            binary_content = None
            if ext in [".pdf", ".pptx", ".xlsx"]:
                with open(file_path, "rb") as f:
                    binary_content = f.read()
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text_content = f.read()

            save_pipeline_output(
                job_id=job_id,
                company_id=clean_company_id,
                stage="parse",
                category="uploads",
                file_name=filename,
                mime_type=mime,
                size_bytes=size_bytes,
                text_content=text_content,
                binary_content=binary_content
            )
        except Exception:
            pass
        
        uploaded_files_info.append(
            UploadedFileResponse(
                filename=filename,
                size_bytes=size_bytes,
                file_type=ext[1:].upper(), # e.g. PDF, XLSX, CSV, PPTX
                status="saved"
            )
        )

    return UploadSuccessResponse(
        company_id=clean_company_id,
        files=uploaded_files_info,
        message="Files uploaded successfully"
    )
