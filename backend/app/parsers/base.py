from abc import ABC, abstractmethod
from app.schemas.parsed_document import ParsedDocument

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str, company_id: str, document_type: str) -> ParsedDocument:
        """
        Parses a document at file_path and returns a Pydantic ParsedDocument object.
        Must preserve original reading order and link each block back to its exact source.
        """
        pass
