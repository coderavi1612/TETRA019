import os
import logging
import datetime
import mimetypes
import psycopg2
from psycopg2.extras import execute_values
from app.config import settings

logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    """
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in environment settings.")
    return psycopg2.connect(settings.DATABASE_URL)

def init_db():
    """
    Initializes the database schema by creating required tables.
    """
    logger.info("Initializing database schema...")
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create pipeline_runs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                job_id VARCHAR(255) PRIMARY KEY,
                company_id VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL,
                started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP WITH TIME ZONE,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create pipeline_outputs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_outputs (
                id SERIAL PRIMARY KEY,
                job_id VARCHAR(255) NOT NULL REFERENCES pipeline_runs(job_id) ON DELETE CASCADE,
                company_id VARCHAR(255) NOT NULL,
                stage VARCHAR(50) NOT NULL,
                category VARCHAR(50) NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                mime_type VARCHAR(100),
                size_bytes INTEGER,
                text_content TEXT,
                binary_content BYTEA,
                generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (job_id, category, file_name)
            );
        """)
        
        conn.commit()
        cur.close()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}", exc_info=True)
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def upsert_pipeline_run(job_id: str, company_id: str, status: str, started_at=None, completed_at=None):
    """
    Upserts a pipeline run entry.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        now = datetime.datetime.now(datetime.timezone.utc)
        
        cur.execute("""
            INSERT INTO pipeline_runs (job_id, company_id, status, started_at, completed_at, updated_at)
            VALUES (%s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP), %s, CURRENT_TIMESTAMP)
            ON CONFLICT (job_id) DO UPDATE
            SET status = EXCLUDED.status,
                completed_at = COALESCE(EXCLUDED.completed_at, pipeline_runs.completed_at),
                updated_at = CURRENT_TIMESTAMP;
        """, (job_id, company_id, status, started_at, completed_at))
        
        conn.commit()
        cur.close()
    except Exception as e:
        logger.error(f"Error upserting pipeline run {job_id}: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def save_pipeline_output(
    job_id: str,
    company_id: str,
    stage: str,
    category: str,
    file_name: str,
    mime_type: str,
    size_bytes: int,
    text_content: str = None,
    binary_content: bytes = None,
    generated_at = None
):
    """
    Saves or updates a pipeline stage output file in the database.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO pipeline_outputs (
                job_id, company_id, stage, category, file_name, mime_type, 
                size_bytes, text_content, binary_content, generated_at, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP), CURRENT_TIMESTAMP)
            ON CONFLICT (job_id, category, file_name) DO UPDATE
            SET mime_type = EXCLUDED.mime_type,
                size_bytes = EXCLUDED.size_bytes,
                text_content = EXCLUDED.text_content,
                binary_content = EXCLUDED.binary_content,
                generated_at = EXCLUDED.generated_at,
                created_at = CURRENT_TIMESTAMP;
        """, (
            job_id, company_id, stage, category, file_name, mime_type,
            size_bytes, text_content, binary_content, generated_at
        ))
        
        conn.commit()
        cur.close()
    except Exception as e:
        logger.error(f"Error saving pipeline output {file_name} for job {job_id}: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def sync_company_artifacts_to_db(company_id: str, job_id: str):
    """
    Scans the outputs directory for a company and syncs all stage outputs and report files to the database.
    """
    if not job_id:
        logger.warning(f"No job_id provided to sync artifacts to DB for company: {company_id}. Skipping.")
        return

    company_dir = os.path.join(settings.OUTPUT_DIR, company_id)
    if not os.path.exists(company_dir):
        logger.warning(f"Outputs directory for company {company_id} does not exist. Skipping DB sync.")
        return

    categories = ["parsed", "extracted", "verification", "readiness", "manifests", "logs"]
    
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

    logger.info(f"Syncing artifacts to DB for company={company_id}, job_id={job_id}...")

    for cat in categories:
        cat_dir = os.path.join(company_dir, cat)
        if os.path.exists(cat_dir) and os.path.isdir(cat_dir):
            for filename in os.listdir(cat_dir):
                file_path = os.path.join(cat_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        stat_info = os.stat(file_path)
                        ext = os.path.splitext(filename)[1].lower()
                        mime = extension_to_mime.get(ext, mimetypes.guess_type(file_path)[0] or "application/octet-stream")
                        
                        mtime = stat_info.st_mtime
                        generated_at = datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc)
                        size_bytes = stat_info.st_size
                        stage = category_to_stage.get(cat, "system")

                        text_content = None
                        binary_content = None

                        if ext == ".pdf":
                            # Read as binary
                            with open(file_path, "rb") as f:
                                binary_content = f.read()
                        else:
                            # Read as text
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                text_content = f.read()

                        save_pipeline_output(
                            job_id=job_id,
                            company_id=company_id,
                            stage=stage,
                            category=cat,
                            file_name=filename,
                            mime_type=mime,
                            size_bytes=size_bytes,
                            text_content=text_content,
                            binary_content=binary_content,
                            generated_at=generated_at
                        )
                    except Exception as ex:
                        logger.error(f"Failed to sync file {filename} in category {cat} to DB: {ex}", exc_info=True)

    logger.info(f"Syncing artifacts to DB completed for company={company_id}, job_id={job_id}.")
