from typing import Dict, Type
from pydantic import BaseModel

from app.schemas.pitch_deck import PitchDeck, MetricValue
from app.schemas.historical_financial_statements import HistoricalFinancialStatements
from app.schemas.mis import Mis
from app.schemas.financial_projections import FinancialProjections
from app.schemas.cap_table import CapTable

SCHEMA_REGISTRY: Dict[str, Type[BaseModel]] = {
    "pitch_deck": PitchDeck,
    "historical_financial_statements": HistoricalFinancialStatements,
    "mis": Mis,
    "mis_report": Mis,
    "monthly_mis_report": Mis,
    "financial_projections": FinancialProjections,
    "cap_table": CapTable,
}

# Export MetricValue model commonly used by extractors
__all__ = [
    "SCHEMA_REGISTRY",
    "PitchDeck",
    "HistoricalFinancialStatements",
    "Mis",
    "FinancialProjections",
    "CapTable",
    "MetricValue"
]
