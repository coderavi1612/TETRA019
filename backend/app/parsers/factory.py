import os
from app.parsers.base import BaseParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.ppt_parser import PPTParser
from app.parsers.excel_parser import ExcelParser
from app.parsers.csv_parser import CSVParser

class ParserFactory:
    @staticmethod
    def get_parser(filename: str) -> BaseParser:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            return PDFParser()
        elif ext == ".pptx":
            return PPTParser()
        elif ext == ".xlsx":
            return ExcelParser()
        elif ext == ".csv":
            return CSVParser()
        else:
            raise ValueError(f"Unsupported file extension '{ext}' for parsing.")
