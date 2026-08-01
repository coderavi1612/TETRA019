# Auto-generated Pydantic models for pitch_deck
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union

class MetricValue(BaseModel):
    value: Optional[Any] = None
    unit: Optional[str] = None
    period: Optional[str] = None
    actual_vs_budget: Optional[str] = None
    source_reference: Optional[str] = None
    source_block_id: Optional[str] = None
    page: Optional[int] = None
    slide: Optional[int] = None
    sheet: Optional[str] = None
    extracted_text_snippet: Optional[str] = None


class PitchDeckDocumentMetadata(BaseModel):
    document_type: Optional[str] = None
    file_name: Optional[Any] = None
    company_name: Optional[Any] = None
    legal_entity_name: Optional[Any] = None
    presenter_name: Optional[Any] = None
    presenter_designation: Optional[Any] = None
    document_date: Optional[Any] = None
    fundraising_round_name: Optional[Any] = None
    total_slides: Optional[Any] = None
    source_file_reference: Optional[Any] = None

class PitchDeckCompanyIdentity(BaseModel):
    company_name: Optional[MetricValue] = None
    legal_entity_name: Optional[MetricValue] = None
    tagline: Optional[MetricValue] = None
    website: Optional[MetricValue] = None

class PitchDeckProblemAndSolution(BaseModel):
    problem_statement: Optional[MetricValue] = None
    target_customer: Optional[MetricValue] = None
    solution_overview: Optional[MetricValue] = None
    key_features: Optional[MetricValue] = None

class PitchDeckMarketOpportunity(BaseModel):
    market_size_tam: Optional[MetricValue] = None
    market_size_sam: Optional[MetricValue] = None
    market_size_som: Optional[MetricValue] = None
    industry_growth_rate: Optional[MetricValue] = None
    segment_or_geography_focus: Optional[MetricValue] = None

class PitchDeckBusinessModel(BaseModel):
    revenue_streams: Optional[MetricValue] = None
    pricing_model: Optional[MetricValue] = None
    customer_segments: Optional[MetricValue] = None
    sales_channels: Optional[MetricValue] = None

class PitchDeckTraction(BaseModel):
    revenue: Optional[MetricValue] = None
    monthly_revenue: Optional[MetricValue] = None
    monthly_growth_rate: Optional[MetricValue] = None
    customer_count: Optional[MetricValue] = None
    paying_customer_count: Optional[MetricValue] = None
    retention_rate: Optional[MetricValue] = None
    churn_rate: Optional[MetricValue] = None
    sales_pipeline_or_order_volume: Optional[MetricValue] = None
    partnerships_or_notable_wins: Optional[MetricValue] = None

class PitchDeckFinancialHighlights(BaseModel):
    revenue: Optional[MetricValue] = None
    gross_margin: Optional[MetricValue] = None
    ebitda: Optional[MetricValue] = None
    net_profit_or_loss: Optional[MetricValue] = None
    cash_balance: Optional[MetricValue] = None
    burn_rate: Optional[MetricValue] = None
    runway: Optional[MetricValue] = None
    major_financial_trend: Optional[MetricValue] = None

class PitchDeckHistoricalPerformancePeriodSummariesItem(BaseModel):
    period: Optional[Any] = None
    revenue: Optional[MetricValue] = None
    key_operating_metrics: Optional[MetricValue] = None
    milestones_achieved: Optional[MetricValue] = None

class PitchDeckHistoricalPerformance(BaseModel):
    period_summaries: List[PitchDeckHistoricalPerformancePeriodSummariesItem] = Field(default_factory=list)

class PitchDeckGoToMarket(BaseModel):
    customer_acquisition_strategy: Optional[MetricValue] = None
    marketing_channels: Optional[MetricValue] = None
    sales_approach: Optional[MetricValue] = None
    distribution_model: Optional[MetricValue] = None
    expansion_plan: Optional[MetricValue] = None

class PitchDeckCompetition(BaseModel):
    main_competitors: Optional[MetricValue] = None
    competitive_advantages: Optional[MetricValue] = None
    differentiation_points: Optional[MetricValue] = None
    market_positioning: Optional[MetricValue] = None

class PitchDeckTeam(BaseModel):
    founders: Optional[MetricValue] = None
    key_leadership: Optional[MetricValue] = None
    advisors: Optional[MetricValue] = None

class PitchDeckFundraisingAsk(BaseModel):
    amount_raising: Optional[MetricValue] = None
    instrument_type: Optional[MetricValue] = None
    valuation: Optional[MetricValue] = None
    use_of_funds: Optional[MetricValue] = None
    expected_runway_after_raise: Optional[MetricValue] = None
    current_round_stage: Optional[MetricValue] = None
    existing_investors: Optional[MetricValue] = None
    ownership_or_investor_references: Optional[MetricValue] = None

class PitchDeckFinancialProjectionSummary(BaseModel):
    forecast_revenue: Optional[MetricValue] = None
    forecast_growth_rate: Optional[MetricValue] = None
    expected_margin_improvement: Optional[MetricValue] = None
    major_assumptions: Optional[MetricValue] = None
    expansion_milestones: Optional[MetricValue] = None

class PitchDeckClosingContact(BaseModel):
    founder_email: Optional[MetricValue] = None
    founder_phone: Optional[MetricValue] = None
    social_links: Optional[MetricValue] = None

class PitchDeckExtractionNotes(BaseModel):
    missing_fields: List[str] = Field(default_factory=list)
    ambiguous_or_unclear_fields: List[str] = Field(default_factory=list)
    vague_unsupported_claims: List[str] = Field(default_factory=list)

class PitchDeck(BaseModel):
    document_metadata: Optional[PitchDeckDocumentMetadata] = None
    company_identity: Optional[PitchDeckCompanyIdentity] = None
    problem_and_solution: Optional[PitchDeckProblemAndSolution] = None
    market_opportunity: Optional[PitchDeckMarketOpportunity] = None
    business_model: Optional[PitchDeckBusinessModel] = None
    traction: Optional[PitchDeckTraction] = None
    financial_highlights: Optional[PitchDeckFinancialHighlights] = None
    historical_performance: Optional[PitchDeckHistoricalPerformance] = None
    go_to_market: Optional[PitchDeckGoToMarket] = None
    competition: Optional[PitchDeckCompetition] = None
    team: Optional[PitchDeckTeam] = None
    fundraising_ask: Optional[PitchDeckFundraisingAsk] = None
    financial_projection_summary: Optional[PitchDeckFinancialProjectionSummary] = None
    closing_contact: Optional[PitchDeckClosingContact] = None
    extraction_notes: Optional[PitchDeckExtractionNotes] = None
