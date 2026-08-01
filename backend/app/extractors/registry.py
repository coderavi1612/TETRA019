import os
import re
from typing import Dict, List, Any

class MetricRegistryLoader:
    @staticmethod
    def load_registry(md_files_dir: str) -> Dict[str, Any]:
        """
        Dynamically loads and parses the expected facts, categories, and priorities
        from specification markdown files in md_files_dir.
        """
        # Maps file names to canonical document types
        mapping = {
            "pitchdeck.md": "pitch_deck",
            "Historical_Financial_Statements.md": "historical_financial_statements",
            "MIS-report.md": "mis_report",
            "Financial_projections.md": "financial_projections",
            "cap-table.md": "cap_table"
        }
        
        registry = {}
        
        if not os.path.exists(md_files_dir) or not os.path.isdir(md_files_dir):
            return {}
            
        for filename in os.listdir(md_files_dir):
            if filename not in mapping:
                continue
                
            doc_type = mapping[filename]
            file_path = os.path.join(md_files_dir, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue
                
            # Heuristically parse expected data points following "Extract" headers
            data_points = []
            
            # Find lines under data points section
            match = re.search(
                r"(?:Data Points the AI Should Extract|Key Data Points the AI Should Extract|Must-Have Contents)[^\n]*\n(?:The AI should[^\n]*\n)?([\s\S]*?)(?=\n#|\n\n\w|\Z)",
                content,
                re.IGNORECASE
            )
            
            if match:
                lines = match.group(1).strip().split("\n")
                for line in lines:
                    cleaned = line.strip().lstrip("-* ").strip()
                    # Skip empty lines, headers, or section comments
                    if cleaned and not cleaned.startswith("#") and len(cleaned) > 2:
                        data_points.append(cleaned)
            
            # Fallback arrays if the regex pattern doesn't yield results
            if not data_points:
                if doc_type == "pitch_deck":
                    data_points = [
                        "Company name", "Legal entity name", "Fundraising round", 
                        "Amount raising", "Revenue", "Monthly revenue", "Gross margin", 
                        "EBITDA", "Net profit or loss", "Cash balance", "Burn rate", 
                        "Runway", "Customer count", "Paying customer count", "Growth rate", 
                        "Retention", "Churn", "Market size", "Pricing", 
                        "Ownership or investor references", "Use of funds", "Projection summary values"
                    ]
                elif doc_type == "historical_financial_statements":
                    data_points = [
                        "Company name", "Financial period", "Revenue", "Gross margin", 
                        "EBITDA", "Net profit", "Cash balance", "Burn rate", "Working capital", 
                        "Funding received", "Debt outstanding", "Share capital", "Retained earnings"
                    ]
                elif doc_type == "mis_report":
                    data_points = [
                        "Monthly revenue", "Revenue growth trend", "Customer count", 
                        "Cash balance", "Burn rate", "Runway", "Gross margin", 
                        "EBITDA margin", "Headcount", "AR/AP", "Debt outstanding", "MoM/YoY growth rate"
                    ]
                elif doc_type == "financial_projections":
                    data_points = [
                        "Near-term revenue forecast", "Growth rate assumption", "Customer count trajectory", 
                        "Gross margin", "EBITDA margin", "Burn rate", "Runway", "Funding ask amount", 
                        "Headcount plan", "Breakeven timeline"
                    ]
                elif doc_type == "cap_table":
                    data_points = [
                        "Company legal name", "Reporting date", "Founder names", "Investor names", 
                        "Total shares outstanding", "Amount invested", "Round name", "Valuation", 
                        "ESOP pool size", "SAFE amount", "Convertible note amount"
                    ]
            
            # Categorize facts dynamically based on keywords
            categories = {
                "financial": [],
                "traction": [],
                "customers": [],
                "fundraising": [],
                "market": [],
                "team": []
            }
            
            for fact in data_points:
                fact_lower = fact.lower()
                if any(kw in fact_lower for kw in ["growth", "mom", "yoy", "traction", "trend"]):
                    cat = "traction"
                elif any(kw in fact_lower for kw in ["customer", "user", "churn", "retention"]):
                    cat = "customers"
                elif any(kw in fact_lower for kw in ["fund", "raise", "round", "invest", "safe", "note", "equity", "valuation", "dilut", "ask"]):
                    cat = "fundraising"
                elif any(kw in fact_lower for kw in ["market", "tam", "sam", "som", "compet", "opportunity"]):
                    cat = "market"
                elif any(kw in fact_lower for kw in ["founder", "team", "leader", "headcount", "hiring", "esop", "employee", "people", "salary", "wage"]):
                    cat = "team"
                else:
                    cat = "financial"
                    
                categories[cat].append(fact)
            
            # Setup priorities
            if doc_type in ["cap_table", "historical_financial_statements"]:
                priority = 1
            elif doc_type == "mis_report":
                priority = 2
            elif doc_type == "financial_projections":
                priority = 3
            else:
                priority = 4
                
            registry[doc_type] = {
                "document_type": doc_type,
                "expected_facts": data_points,
                "categories": categories,
                "priority": priority
            }
            
        return registry
