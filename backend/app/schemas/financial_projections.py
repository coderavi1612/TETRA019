# Auto-generated Pydantic models for financial_projections
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


class FinancialProjectionsDocumentMetadata(BaseModel):
    document_type: Optional[str] = None
    file_name: Optional[Any] = None
    company_legal_name: Optional[Any] = None
    projection_period_covered: Optional[Any] = None
    currency: Optional[Any] = None
    base_or_start_month: Optional[Any] = None
    version_or_revision_number: Optional[Any] = None
    source_file_reference: Optional[Any] = None

class FinancialProjectionsScenario(BaseModel):
    scenario_name: Optional[Any] = None
    scenario_type: Optional[Any] = None

class FinancialProjectionsProjectionPeriodsItemRevenueBuild(BaseModel):
    revenue_forecast_total: Optional[MetricValue] = None
    revenue_by_product_line_segment: Optional[MetricValue] = None
    new_customers_per_month: Optional[MetricValue] = None
    arpu: Optional[MetricValue] = None
    expansion_revenue: Optional[MetricValue] = None
    churn_assumption: Optional[MetricValue] = None
    customer_count_projected: Optional[MetricValue] = None

class FinancialProjectionsProjectionPeriodsItemCostAndMarginBuild(BaseModel):
    cogs: Optional[MetricValue] = None
    gross_margin_percent: Optional[MetricValue] = None
    opex_people: Optional[MetricValue] = None
    opex_marketing: Optional[MetricValue] = None
    opex_tech_infra: Optional[MetricValue] = None
    opex_g_and_a: Optional[MetricValue] = None
    opex_total: Optional[MetricValue] = None
    ebitda: Optional[MetricValue] = None
    net_profit_or_loss: Optional[MetricValue] = None
    is_breakeven_period: Optional[Any] = None

class FinancialProjectionsProjectionPeriodsItemCashFlowAndFunding(BaseModel):
    projected_burn: Optional[MetricValue] = None
    projected_cash_balance: Optional[MetricValue] = None
    projected_runway: Optional[MetricValue] = None

class FinancialProjectionsProjectionPeriodsItemHeadcountPlan(BaseModel):
    total_headcount: Optional[MetricValue] = None
    headcount_by_department: Optional[MetricValue] = None

class FinancialProjectionsProjectionPeriodsItem(BaseModel):
    period_label: Optional[Any] = None
    period_type: Optional[Any] = None
    period_start_date: Optional[Any] = None
    period_end_date: Optional[Any] = None
    scenario: Optional[Any] = None
    revenue_build: Optional[FinancialProjectionsProjectionPeriodsItemRevenueBuild] = None
    cost_and_margin_build: Optional[FinancialProjectionsProjectionPeriodsItemCostAndMarginBuild] = None
    cash_flow_and_funding: Optional[FinancialProjectionsProjectionPeriodsItemCashFlowAndFunding] = None
    headcount_plan: Optional[FinancialProjectionsProjectionPeriodsItemHeadcountPlan] = None

class FinancialProjectionsFundingAsk(BaseModel):
    funding_ask_amount: Optional[MetricValue] = None
    use_of_funds_linkage: Optional[MetricValue] = None
    runway_milestones_assumed: Optional[MetricValue] = None

class FinancialProjectionsBreakeven(BaseModel):
    breakeven_period: Optional[MetricValue] = None
    breakeven_basis: Optional[MetricValue] = None

class FinancialProjectionsScenarioFraming(BaseModel):
    base_case_summary: Optional[MetricValue] = None
    best_case_summary: Optional[MetricValue] = None
    worst_case_summary: Optional[MetricValue] = None

class FinancialProjectionsOptionalValueAdd(BaseModel):
    cohort_retention_revenue_curves: Optional[MetricValue] = None
    sensitivity_analysis: Optional[MetricValue] = None
    prior_period_projected_vs_actual: Optional[MetricValue] = None
    burn_multiple: Optional[MetricValue] = None
    magic_number: Optional[MetricValue] = None
    cac_payback_period: Optional[MetricValue] = None
    milestone_map: Optional[MetricValue] = None
    tax_and_statutory_assumptions: Optional[MetricValue] = None
    esop_pool_expansion_assumptions: Optional[MetricValue] = None

class FinancialProjectionsCrossDocumentCheckpointsNearTermRevenueForecast(BaseModel):
    compare_against: Optional[str] = None
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class FinancialProjectionsCrossDocumentCheckpointsGrowthRateAssumption(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class FinancialProjectionsCrossDocumentCheckpointsCustomerUserCountTrajectory(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class FinancialProjectionsCrossDocumentCheckpointsGrossMarginEbitdaMargin(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class FinancialProjectionsCrossDocumentCheckpointsBurnRateAndRunway(BaseModel):
    compare_against: Optional[str] = None
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class FinancialProjectionsCrossDocumentCheckpointsFundingAskAmount(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class FinancialProjectionsCrossDocumentCheckpointsHeadcountPlan(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class FinancialProjectionsCrossDocumentCheckpointsBreakevenTimeline(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class FinancialProjectionsCrossDocumentCheckpointsPriorPeriodProjectedVsActual(BaseModel):
    compare_against: Optional[str] = None
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class FinancialProjectionsCrossDocumentCheckpoints(BaseModel):
    near_term_revenue_forecast: Optional[FinancialProjectionsCrossDocumentCheckpointsNearTermRevenueForecast] = None
    growth_rate_assumption: Optional[FinancialProjectionsCrossDocumentCheckpointsGrowthRateAssumption] = None
    customer_user_count_trajectory: Optional[FinancialProjectionsCrossDocumentCheckpointsCustomerUserCountTrajectory] = None
    gross_margin_ebitda_margin: Optional[FinancialProjectionsCrossDocumentCheckpointsGrossMarginEbitdaMargin] = None
    burn_rate_and_runway: Optional[FinancialProjectionsCrossDocumentCheckpointsBurnRateAndRunway] = None
    funding_ask_amount: Optional[FinancialProjectionsCrossDocumentCheckpointsFundingAskAmount] = None
    headcount_plan: Optional[FinancialProjectionsCrossDocumentCheckpointsHeadcountPlan] = None
    breakeven_timeline: Optional[FinancialProjectionsCrossDocumentCheckpointsBreakevenTimeline] = None
    prior_period_projected_vs_actual: Optional[FinancialProjectionsCrossDocumentCheckpointsPriorPeriodProjectedVsActual] = None

class FinancialProjectionsExtractionNotesClassificationLegend(BaseModel):
    missing_information: Optional[str] = None
    unresolved_inconsistency: Optional[str] = None
    verified_mismatch: Optional[str] = None

class FinancialProjectionsExtractionNotes(BaseModel):
    missing_fields: List[str] = Field(default_factory=list)
    ambiguous_or_unclear_fields: List[str] = Field(default_factory=list)
    classification_legend: Optional[FinancialProjectionsExtractionNotesClassificationLegend] = None

class FinancialProjections(BaseModel):
    document_metadata: Optional[FinancialProjectionsDocumentMetadata] = None
    assumptions_register: List[MetricValue] = Field(default_factory=list)
    scenario: Optional[FinancialProjectionsScenario] = None
    projection_periods: List[FinancialProjectionsProjectionPeriodsItem] = Field(default_factory=list)
    funding_ask: Optional[FinancialProjectionsFundingAsk] = None
    breakeven: Optional[FinancialProjectionsBreakeven] = None
    scenario_framing: Optional[FinancialProjectionsScenarioFraming] = None
    optional_value_add: Optional[FinancialProjectionsOptionalValueAdd] = None
    cross_document_checkpoints: Optional[FinancialProjectionsCrossDocumentCheckpoints] = None
    extraction_notes: Optional[FinancialProjectionsExtractionNotes] = None
