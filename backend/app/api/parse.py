from fastapi import APIRouter, HTTPException, status
from app.schemas.parse import ParseResponse, ParseResultFile
from app.parsers.orchestrator import DocumentParserOrchestrator

router = APIRouter()

@router.post("/{company_id}", response_model=ParseResponse)
async def parse_documents(company_id: str):
    clean_company_id = company_id.strip()
    if not clean_company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="company_id cannot be empty or whitespace."
        )

    try:
        result = DocumentParserOrchestrator.run_parse(clean_company_id)
        # Convert results list to Pydantic objects for response validation
        files_validated = [
            ParseResultFile(
                file_name=f["file_name"],
                document_type=f["document_type"],
                status=f["status"],
                blocks=f["blocks"],
                errors=f["errors"]
            )
            for f in result["files"]
        ]
        return ParseResponse(
            company_id=result["company_id"],
            documents_parsed=result["documents_parsed"],
            files=files_validated
        )
    except FileNotFoundError as fnf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fnf)
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during parsing: {str(e)}"
        )
