import os

class DocumentClassifier:
    @staticmethod
    def classify(filename: str) -> str:
        # Normalize name for keyword matching
        name = os.path.splitext(filename)[0].lower().replace("_", " ").replace("-", " ")
        
        # Check capitalization table
        if any(kw in name for kw in ["cap table", "captable", "capitalization", "ownership", "shareholder"]):
            return "cap_table"
            
        # Check pitch deck
        if any(kw in name for kw in ["pitch deck", "pitchdeck", "presentation", "deck"]):
            return "pitch_deck"
            
        # Check MIS
        if any(kw in name for kw in ["mis", "monthly mis", "mis report"]):
            return "mis_report"
            
        # Check projections
        if any(kw in name for kw in ["projection", "forecast", "financial projections", "financial model"]):
            return "financial_projections"
            
        # Check historical financials
        if any(kw in name for kw in ["financial statement", "financials", "audited", "historical"]):
            return "historical_financial_statements"
            
        # Fallback to single token abbreviation checks
        tokens = name.split()
        if "ct" in tokens:
            return "cap_table"
        if "pd" in tokens:
            return "pitch_deck"
        if "mis" in tokens:
            return "mis_report"
        if "fp" in tokens:
            return "financial_projections"
        if "fs" in tokens:
            return "historical_financial_statements"
            
        return "unknown"
