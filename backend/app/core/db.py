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
    generated_at = None,
    conn = None
):
    """
    Saves or updates a pipeline stage output file in the database. Reuses connection if provided.
    """
    local_conn = conn
    should_close = False
    try:
        if not local_conn:
            local_conn = get_db_connection()
            should_close = True
        
        cur = local_conn.cursor()
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
        
        cur.close()
        if should_close:
            local_conn.commit()
    except Exception as e:
        logger.error(f"Error saving pipeline output {file_name} for job {job_id}: {e}", exc_info=True)
        if local_conn and should_close:
            local_conn.rollback()
        raise e
    finally:
        if local_conn and should_close:
            local_conn.close()

def sync_company_artifacts_to_db(company_id: str, job_id: str):
    """
    Scans the uploads and outputs directories for a company and syncs all raw files,
    stage outputs, and report files to the database.
    """
    if not job_id:
        logger.warning(f"No job_id provided to sync artifacts to DB for company: {company_id}. Skipping.")
        return

    category_to_stage = {
        "uploads": "parse",
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
        ".log": "text/plain",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".csv": "text/csv"
    }

    logger.info(f"Syncing artifacts to DB for company={company_id}, job_id={job_id}...")

    conn = None
    try:
        conn = get_db_connection()
        
        # 1. Sync Uploaded Raw Documents
        upload_company_dir = os.path.join(settings.UPLOAD_DIR, company_id)
        if os.path.exists(upload_company_dir) and os.path.isdir(upload_company_dir):
            for filename in os.listdir(upload_company_dir):
                file_path = os.path.join(upload_company_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        stat_info = os.stat(file_path)
                        ext = os.path.splitext(filename)[1].lower()
                        mime = extension_to_mime.get(ext, mimetypes.guess_type(file_path)[0] or "application/octet-stream")
                        mtime = stat_info.st_mtime
                        generated_at = datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc)
                        size_bytes = stat_info.st_size

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
                            company_id=company_id,
                            stage="parse",
                            category="uploads",
                            file_name=filename,
                            mime_type=mime,
                            size_bytes=size_bytes,
                            text_content=text_content,
                            binary_content=binary_content,
                            generated_at=generated_at,
                            conn=conn
                        )
                    except Exception as ex:
                        logger.error(f"Failed to sync uploaded file {filename} to DB: {ex}", exc_info=True)

        # 2. Sync Pipeline Output Directories
        company_output_dir = os.path.join(settings.OUTPUT_DIR, company_id)
        if os.path.exists(company_output_dir) and os.path.isdir(company_output_dir):
            categories = ["parsed", "extracted", "verification", "readiness", "manifests", "logs"]
            for cat in categories:
                cat_dir = os.path.join(company_output_dir, cat)
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

                                if ext in [".pdf", ".pptx", ".xlsx"]:
                                    with open(file_path, "rb") as f:
                                        binary_content = f.read()
                                else:
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
                                    generated_at=generated_at,
                                    conn=conn
                                )
                            except Exception as ex:
                                logger.error(f"Failed to sync output file {filename} in category {cat} to DB: {ex}", exc_info=True)
        conn.commit()
        logger.info(f"Syncing artifacts to DB completed for company={company_id}, job_id={job_id}.")
    except Exception as e:
        logger.error(f"Error syncing company artifacts to DB: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def get_all_companies_summary():
    """
    Retrieves a list of all companies from pipeline_runs, with their latest job status,
    updated timestamp, and count of parsed documents.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT r.company_id, r.job_id, r.status, r.updated_at, 
                   COALESCE(c.file_count, 0) as file_count
            FROM (
                SELECT DISTINCT ON (company_id) company_id, job_id, status, updated_at
                FROM pipeline_runs
                ORDER BY company_id, updated_at DESC
            ) r
            LEFT JOIN (
                SELECT job_id, COUNT(*) as file_count 
                FROM pipeline_outputs 
                WHERE category IN ('parsed', 'uploads')
                GROUP BY job_id
            ) c ON r.job_id = c.job_id
            ORDER BY r.updated_at DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "company_id": row[0],
                "job_id": row[1],
                "status": row[2],
                "updated_at": row[3].isoformat() if row[3] else None,
                "file_count": row[4]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting companies summary: {e}", exc_info=True)
        return []
    finally:
        if conn:
            conn.close()


def get_pipeline_outputs_from_db(company_id: str):
    """
    Retrieves all pipeline outputs stored in Supabase DB for a specific company_id.
    Returns a dict mapping (category.lower(), file_name.lower()) -> output_dict.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT category, file_name, mime_type, size_bytes, text_content, binary_content, stage, generated_at
            FROM pipeline_outputs
            WHERE company_id = %s;
        """, (company_id,))
        rows = cur.fetchall()
        cur.close()
        outputs = {}
        for row in rows:
            cat, filename, mime, size, text_c, bin_c, stage, gen_at = row
            key = (cat.lower(), filename.lower())
            outputs[key] = {
                "category": cat,
                "file_name": filename,
                "mime_type": mime,
                "size_bytes": size,
                "text_content": text_c,
                "binary_content": bytes(bin_c) if bin_c else None,
                "stage": stage,
                "generated_at": gen_at.isoformat() if gen_at else None
            }
        return outputs
    except Exception as e:
        logger.error(f"Error fetching pipeline outputs from DB for company {company_id}: {e}")
        return {}
    finally:
        if conn:
            conn.close()


