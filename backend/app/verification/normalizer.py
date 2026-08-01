import re
from typing import Any, Optional, Tuple

class FieldNormalizer:
    @staticmethod
    def normalize_currency(currency_str: Optional[str]) -> Optional[str]:
        if not currency_str:
            return None
        c = currency_str.strip().lower()
        if c in ("inr", "₹", "rupees", "rupee"):
            return "INR"
        if c in ("usd", "$", "dollars", "dollar"):
            return "USD"
        return currency_str.strip().upper()

    @staticmethod
    def normalize_period(period_str: Optional[str]) -> Optional[str]:
        if not period_str:
            return None
        p = str(period_str).strip().lower().replace(" ", "")
        
        # FY 2024 / FY2024 / FY24
        match_fy = re.match(r"^fy(?:20)?(\d{2})$", p)
        if match_fy:
            return f"FY{match_fy.group(1)}"
            
        # 2023-24 / 2023-2024
        match_range = re.match(r"^(\d{4})[-/](\d{2,4})$", p)
        if match_range:
            year2 = match_range.group(2)
            if len(year2) == 4:
                year2 = year2[2:]
            return f"FY{year2}"
            
        # Just a year: 2024
        match_year = re.match(r"^(?:20)?(\d{2})$", p)
        if match_year:
            return f"FY{match_year.group(1)}"
            
        return period_str.strip()

    @staticmethod
    def normalize_value(val: Any, strategy: str, unit: Optional[str] = None) -> Tuple[Any, Optional[str]]:
        if val is None:
            return None, None
            
        val_str = str(val).strip()
        
        if strategy == "numeric" or strategy == "ownership":
            cleaned = val_str.replace("₹", "").replace("$", "").replace(",", "").strip()
            
            # Combine value and unit for parsing
            search_str = cleaned
            if unit:
                search_str = f"{cleaned} {unit}".strip()
            
            # Check percentage
            if search_str.endswith("%") or (unit and "%" in str(unit)):
                try:
                    cleaned_pct = search_str.replace("%", "").strip()
                    pct_match = re.search(r"([\d\.]+)", cleaned_pct)
                    if pct_match:
                        num = float(pct_match.group(1)) / 100.0
                        return num, "%"
                except ValueError:
                    pass
            
            # Check scaling (Cr, Lakhs, Mn, Bn, K)
            match_cr = re.search(r"([\d\.]+)\s*(?:cr|crore|crores)", search_str, re.IGNORECASE)
            if match_cr:
                try:
                    return float(match_cr.group(1)) * 10000000.0, "INR"
                except ValueError:
                    pass
                    
            match_lakh = re.search(r"([\d\.]+)\s*(?:lakh|lakhs|l)", search_str, re.IGNORECASE)
            if match_lakh:
                try:
                    val_lakh = float(match_lakh.group(1))
                    return val_lakh * 100000.0, "INR"
                except ValueError:
                    pass

            match_bn = re.search(r"([\d\.]+)\s*(?:bn|billion|billions|b)", search_str, re.IGNORECASE)
            if match_bn:
                try:
                    return float(match_bn.group(1)) * 1000000000.0, "USD"
                except ValueError:
                    pass

            match_mn = re.search(r"([\d\.]+)\s*(?:mn|million|millions|m)", search_str, re.IGNORECASE)
            if match_mn:
                try:
                    return float(match_mn.group(1)) * 1000000.0, "USD"
                except ValueError:
                    pass

            match_k = re.search(r"([\d\.]+)\s*(?:k|thousand|thousands)", search_str, re.IGNORECASE)
            if match_k:
                try:
                    return float(match_k.group(1)) * 1000.0, None
                except ValueError:
                    pass

            # Just float conversion
            try:
                # Strip spaces or other non-numeric symbols
                cleaned_numeric = "".join([c for c in cleaned if c.isdigit() or c in (".", "-", "+")])
                if cleaned_numeric:
                    val_float = float(cleaned_numeric)
                    if strategy == "ownership" and val_float > 1.0:
                        pass
                    return val_float, None
            except ValueError:
                pass
            return val, None

        if strategy == "boolean":
            lower_val = val_str.lower()
            if lower_val in ("true", "1", "yes", "y", "actual"):
                return True, None
            if lower_val in ("false", "0", "no", "n", "budget"):
                return False, None
            return bool(val), None

        return val_str, None
