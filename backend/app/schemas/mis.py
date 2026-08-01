# Auto-generated Pydantic models for mis
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


class MisDocumentMetadata(BaseModel):
    document_type: Optional[str] = None
    file_name: Optional[Any] = None
    company_legal_name: Optional[Any] = None
    mis_period: Optional[Any] = None
    currency: Optional[Any] = None
    date_of_preparation: Optional[Any] = None
    version_or_revision_number: Optional[Any] = None
    prepared_by: Optional[Any] = None
    approved_by: Optional[Any] = None
    source_file_reference: Optional[Any] = None

class MisProfitAndLossSummary(BaseModel):
    revenue_total: Optional[MetricValue] = None
    revenue_recurring: Optional[MetricValue] = None
    revenue_non_recurring: Optional[MetricValue] = None
    cogs: Optional[MetricValue] = None
    gross_margin_amount: Optional[MetricValue] = None
    gross_margin_percent: Optional[MetricValue] = None
    opex_people: Optional[MetricValue] = None
    opex_marketing: Optional[MetricValue] = None
    opex_tech_infra: Optional[MetricValue] = None
    opex_g_and_a: Optional[MetricValue] = None
    ebitda: Optional[MetricValue] = None
    net_profit_or_loss: Optional[MetricValue] = None

class MisCashAndLiquidity(BaseModel):
    opening_cash_balance: Optional[MetricValue] = None
    cash_inflows: Optional[MetricValue] = None
    cash_outflows: Optional[MetricValue] = None
    closing_cash_balance: Optional[MetricValue] = None
    net_monthly_burn: Optional[MetricValue] = None
    runway_months: Optional[MetricValue] = None
    bank_balances_by_account: Optional[MetricValue] = None
    restricted_or_escrow_cash: Optional[MetricValue] = None

class MisRevenueAndGrowthMetrics(BaseModel):
    mrr_or_arr: Optional[MetricValue] = None
    monthly_gmv_or_sales_value: Optional[MetricValue] = None
    mom_growth_percent: Optional[MetricValue] = None
    yoy_growth_percent: Optional[MetricValue] = None
    revenue_mix_by_product_line: Optional[MetricValue] = None
    revenue_mix_by_customer_segment: Optional[MetricValue] = None
    revenue_mix_by_geography: Optional[MetricValue] = None
    active_customer_count: Optional[MetricValue] = None
    new_customers_added: Optional[MetricValue] = None
    customers_churned: Optional[MetricValue] = None

class MisUnitEconomics(BaseModel):
    cac: Optional[MetricValue] = None
    ltv: Optional[MetricValue] = None
    monthly_churn_rate: Optional[MetricValue] = None
    logo_churn_rate: Optional[MetricValue] = None
    net_revenue_retention: Optional[MetricValue] = None

class MisBalanceSheetSnapshot(BaseModel):
    accounts_receivable: Optional[MetricValue] = None
    accounts_receivable_ageing: Optional[MetricValue] = None
    accounts_payable: Optional[MetricValue] = None
    accounts_payable_ageing: Optional[MetricValue] = None
    total_debt_outstanding: Optional[MetricValue] = None
    debt_covenant_status: Optional[MetricValue] = None

class MisHeadcount(BaseModel):
    total_headcount_month_end: Optional[MetricValue] = None
    hires_during_month: Optional[MetricValue] = None
    exits_during_month: Optional[MetricValue] = None
    headcount_by_department: Optional[MetricValue] = None

class MisBudgetVsActualVariance(BaseModel):
    revenue_variance: Optional[MetricValue] = None
    ebitda_variance: Optional[MetricValue] = None
    opex_variance: Optional[MetricValue] = None
    variance_commentary: Optional[MetricValue] = None

class MisOptionalValueAdd(BaseModel):
    expense_detail_by_department: Optional[MetricValue] = None
    marketing_funnel_impressions: Optional[MetricValue] = None
    marketing_funnel_leads: Optional[MetricValue] = None
    marketing_funnel_conversion_rate: Optional[MetricValue] = None
    cac_by_channel: Optional[MetricValue] = None
    dau_mau: Optional[MetricValue] = None
    feature_adoption: Optional[MetricValue] = None
    engagement_score: Optional[MetricValue] = None
    top_10_customer_concentration: Optional[MetricValue] = None
    single_customer_revenue_dependency: Optional[MetricValue] = None
    debt_repayment_schedule: Optional[MetricValue] = None
    upcoming_debt_maturities: Optional[MetricValue] = None
    hiring_plan_vs_actual: Optional[MetricValue] = None
    management_commentary: Optional[MetricValue] = None
    fundraising_status_tracker: Optional[MetricValue] = None
    esop_pool_utilisation: Optional[MetricValue] = None

class MisCrossDocumentCheckpointsMonthlyRevenue(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpointsRevenueGrowthTrend(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpointsCustomerUserCount(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpointsCashBalanceMonthEnd(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpointsBurnRateRunway(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpointsGrossMarginEbitdaMargin(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpointsHeadcount(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpointsAccountsReceivablePayable(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpointsDebtOutstanding(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpointsMomYoyGrowthRate(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpointsBudgetVsActualVariance(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    expected_match_logic: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class MisCrossDocumentCheckpoints(BaseModel):
    monthly_revenue: Optional[MisCrossDocumentCheckpointsMonthlyRevenue] = None
    revenue_growth_trend: Optional[MisCrossDocumentCheckpointsRevenueGrowthTrend] = None
    customer_user_count: Optional[MisCrossDocumentCheckpointsCustomerUserCount] = None
    cash_balance_month_end: Optional[MisCrossDocumentCheckpointsCashBalanceMonthEnd] = None
    burn_rate_runway: Optional[MisCrossDocumentCheckpointsBurnRateRunway] = None
    gross_margin_ebitda_margin: Optional[MisCrossDocumentCheckpointsGrossMarginEbitdaMargin] = None
    headcount: Optional[MisCrossDocumentCheckpointsHeadcount] = None
    accounts_receivable_payable: Optional[MisCrossDocumentCheckpointsAccountsReceivablePayable] = None
    debt_outstanding: Optional[MisCrossDocumentCheckpointsDebtOutstanding] = None
    mom_yoy_growth_rate: Optional[MisCrossDocumentCheckpointsMomYoyGrowthRate] = None
    budget_vs_actual_variance: Optional[MisCrossDocumentCheckpointsBudgetVsActualVariance] = None

class MisExtractionNotesClassificationLegend(BaseModel):
    missing_information: Optional[str] = None
    unresolved_inconsistency: Optional[str] = None
    verified_mismatch: Optional[str] = None

class MisExtractionNotes(BaseModel):
    missing_fields: List[str] = Field(default_factory=list)
    ambiguous_or_unclear_fields: List[str] = Field(default_factory=list)
    classification_legend: Optional[MisExtractionNotesClassificationLegend] = None

class Mis(BaseModel):
    document_metadata: Optional[MisDocumentMetadata] = None
    profit_and_loss_summary: Optional[MisProfitAndLossSummary] = None
    cash_and_liquidity: Optional[MisCashAndLiquidity] = None
    revenue_and_growth_metrics: Optional[MisRevenueAndGrowthMetrics] = None
    unit_economics: Optional[MisUnitEconomics] = None
    balance_sheet_snapshot: Optional[MisBalanceSheetSnapshot] = None
    headcount: Optional[MisHeadcount] = None
    budget_vs_actual_variance: Optional[MisBudgetVsActualVariance] = None
    optional_value_add: Optional[MisOptionalValueAdd] = None
    cross_document_checkpoints: Optional[MisCrossDocumentCheckpoints] = None
    extraction_notes: Optional[MisExtractionNotes] = None
