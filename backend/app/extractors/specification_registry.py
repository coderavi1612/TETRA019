import os
import re
import hashlib
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class SpecificationRegistry:
    _registry: Dict[str, Any] = {}
    _version: str = "1.0"
    _loaded: bool = False

    @classmethod
    def load(cls, md_files_dir: str = None) -> None:
        """
        Dynamically loads and parses the specification markdown files.
        Builds the categories, expected fields/metrics, and document rules.
        """
        if cls._loaded:
            return

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
        if md_files_dir is None:
            md_files_dir = os.path.join(base_dir, "md-files")
            
        if not os.path.exists(md_files_dir):
            workspace_dir = os.path.dirname(base_dir)
            md_files_dir = os.path.join(workspace_dir, "md-files")

        if not os.path.exists(md_files_dir) or not os.path.isdir(md_files_dir):
            logger.warning(f"Specification markdown directory not found at: {md_files_dir}")
            return

        # Maps file names to canonical document types
        mapping = {
            "pitchdeck.md": "pitch_deck",
            "Historical_Financial_Statements.md": "historical_financial_statements",
            "MIS-report.md": "mis_report",
            "Financial_projections.md": "financial_projections",
            "cap-table.md": "cap_table"
        }

        cls._registry = {}
        content_accumulator = ""

        logger.info(f"Loading specifications from: {md_files_dir}")

        for filename in os.listdir(md_files_dir):
            if filename not in mapping:
                continue
                
            doc_type = mapping[filename]
            file_path = os.path.join(md_files_dir, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    content_accumulator += content
            except Exception as e:
                logger.error(f"Error reading spec file {filename}: {str(e)}")
                continue

            # Heuristically parse expected data points following "Extract" headers
            data_points = []
            match = re.search(
                r"(?:Data Points the AI Should Extract|Key Data Points the AI Should Extract|Must-Have Contents)[^\n]*\n(?:The AI should[^\n]*\n)?([\s\S]*?)(?=\n#|\n\n\w|\Z)",
                content,
                re.IGNORECASE
            )
            
            if match:
                lines = match.group(1).strip().split("\n")
                for line in lines:
                    cleaned = line.strip().lstrip("-* ").strip()
                    if cleaned:
                        data_points.append(cleaned)
            
            # Setup default fallback data points if regex fails
            if not data_points:
                data_points = cls._get_fallback_data_points(doc_type)

            # Categorize fields based on keywords
            categories = cls._categorize_fields(data_points)

            # Extraction Priority Mapping
            if doc_type in ["cap_table", "historical_financial_statements"]:
                priority = 1
            elif doc_type in ["mis_report", "monthly_mis_report"]:
                priority = 2
            elif doc_type == "financial_projections":
                priority = 3
            else:
                priority = 4

            # Parse reconciliation and consistency checkpoints
            reconciliation_rules = cls._parse_section(content, "Common Inconsistencies|Reconciliation")
            validation_rules = cls._parse_section(content, "What Makes the.*Perfect")

            cls._registry[doc_type] = {
                "document_type": doc_type,
                "expected_fields": data_points,
                "categories": categories,
                "priority": priority,
                "reconciliation_rules": reconciliation_rules,
                "validation_rules": validation_rules
            }

            # Map mis_report alias
            if doc_type == "mis_report":
                cls._registry["monthly_mis_report"] = cls._registry[doc_type]

        from app.core import sha256_string
        cls._version = sha256_string(content_accumulator)[:16]
        cls._loaded = True
        logger.info(f"Loaded SpecificationRegistry version: {cls._version}")

    @classmethod
    def get_version(cls) -> str:
        cls.load()
        return cls._version

    @classmethod
    def get_document_definition(cls, doc_type: str) -> Dict[str, Any]:
        cls.load()
        return cls._registry.get(doc_type) or {}

    @classmethod
    def get_categories(cls, doc_type: str) -> Dict[str, List[str]]:
        cls.load()
        return (cls._registry.get(doc_type) or {}).get("categories") or {}

    @classmethod
    def get_expected_fields(cls, doc_type: str) -> List[str]:
        cls.load()
        return (cls._registry.get(doc_type) or {}).get("expected_fields") or []

    @classmethod
    def get_reconciliation_rules(cls, doc_type: str) -> List[str]:
        cls.load()
        return (cls._registry.get(doc_type) or {}).get("reconciliation_rules") or []

    @classmethod
    def get_validation_rules(cls, doc_type: str) -> List[str]:
        cls.load()
        return (cls._registry.get(doc_type) or {}).get("validation_rules") or []

    @staticmethod
    def _categorize_fields(fields: List[str]) -> Dict[str, List[str]]:
        categories = {
            "financial": [],
            "traction": [],
            "customers": [],
            "fundraising": [],
            "market": [],
            "team": []
        }
        for field in fields:
            field_lower = field.lower()
            if any(kw in field_lower for kw in ["growth", "mom", "yoy", "traction", "trend"]):
                cat = "traction"
            elif any(kw in field_lower for kw in ["customer", "user", "churn", "retention"]):
                cat = "customers"
            elif any(kw in field_lower for kw in ["fund", "raise", "round", "invest", "safe", "note", "equity", "valuation", "dilut", "ask"]):
                cat = "fundraising"
            elif any(kw in field_lower for kw in ["market", "tam", "sam", "som", "compet", "opportunity"]):
                cat = "market"
            elif any(kw in field_lower for kw in ["founder", "team", "leader", "headcount", "hiring", "esop", "employee", "people", "salary", "wage"]):
                cat = "team"
            else:
                cat = "financial"
            categories[cat].append(field)
        return categories

    @staticmethod
    def _parse_section(content: str, header_pattern: str) -> List[str]:
        rules = []
        match = re.search(
            rf"(?:{header_pattern})[^\n]*\n([\s\S]*?)(?=\n#|\n\n\w|\Z)",
            content,
            re.IGNORECASE
        )
        if match:
            lines = match.group(1).strip().split("\n")
            for line in lines:
                cleaned = line.strip().lstrip("-* ").strip()
                if cleaned and len(cleaned) > 2:
                    rules.append(cleaned)
        return rules

    @staticmethod
    def _get_fallback_data_points(doc_type: str) -> List[str]:
        if doc_type == "pitch_deck":
            return [
                "Company name", "Legal entity name", "Fundraising round", 
                "Amount raising", "Revenue", "Monthly revenue", "Gross margin", 
                "EBITDA", "Net profit or loss", "Cash balance", "Burn rate", 
                "Runway", "Customer count", "Paying customer count", "Growth rate", 
                "Retention", "Churn", "Market size", "Pricing", 
                "Ownership or investor references", "Use of funds", "Projection summary values"
            ]
        elif doc_type == "historical_financial_statements":
            return [
                "Company name", "Financial period", "Revenue", "Gross margin", 
                "EBITDA", "Net profit", "Cash balance", "Burn rate", "Working capital", 
                "Funding received", "Debt outstanding", "Share capital", "Retained earnings"
            ]
        elif doc_type in ["mis_report", "monthly_mis_report"]:
            return [
                "Monthly revenue", "Revenue growth trend", "Customer count", 
                "Cash balance", "Burn rate", "Runway", "Gross margin", 
                "EBITDA margin", "Headcount", "AR/AP", "Debt outstanding", "MoM/YoY growth rate"
            ]
        elif doc_type == "financial_projections":
            return [
                "Near-term revenue forecast", "Growth rate assumption", "Customer count trajectory", 
                "Gross margin", "EBITDA margin", "Burn rate", "Runway", "Funding ask amount", 
                "Headcount plan", "Breakeven timeline"
            ]
        elif doc_type == "cap_table":
            return [
                "Company legal name", "Reporting date", "Founder names", "Investor names", 
                "Total shares outstanding", "Amount invested", "Round name", "Valuation", 
                "ESOP pool size", "SAFE amount", "Convertible note amount"
            ]
        return []
