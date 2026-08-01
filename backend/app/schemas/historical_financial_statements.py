# Auto-generated Pydantic models for historical_financial_statements
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
    confidence: Optional[float] = 1.0
    evidence: Optional[Dict[str, Any]] = None


class HistoricalFinancialStatementsDocumentMetadata(BaseModel):
    document_type: Optional[str] = None
    file_name: Optional[Any] = None
    company_legal_name: Optional[Any] = None
    consolidated_or_standalone: Optional[Any] = None
    currency: Optional[Any] = None
    accounting_standards_followed: Optional[Any] = None
    auditor_name: Optional[Any] = None
    is_audited: Optional[Any] = None
    number_of_years_covered: Optional[Any] = None
    source_file_reference: Optional[Any] = None

class HistoricalFinancialStatementsFinancialPeriodsItemIncomeStatement(BaseModel):
    revenue_total: Optional[MetricValue] = None
    revenue_by_product_line: Optional[MetricValue] = None
    revenue_by_geography: Optional[MetricValue] = None
    revenue_by_customer_segment: Optional[MetricValue] = None
    other_operating_income: Optional[MetricValue] = None
    non_operating_income: Optional[MetricValue] = None
    cogs_total: Optional[MetricValue] = None
    cogs_raw_material: Optional[MetricValue] = None
    cogs_manufacturing_production: Optional[MetricValue] = None
    cogs_direct_labor: Optional[MetricValue] = None
    cogs_packaging: Optional[MetricValue] = None
    cogs_shipping_logistics: Optional[MetricValue] = None
    cogs_hosting_infra: Optional[MetricValue] = None
    cogs_fulfillment: Optional[MetricValue] = None
    cogs_merchant_fees: Optional[MetricValue] = None
    gross_profit: Optional[MetricValue] = None
    gross_margin_percent: Optional[MetricValue] = None
    opex_salaries_wages: Optional[MetricValue] = None
    opex_marketing_advertising: Optional[MetricValue] = None
    opex_sales_business_development: Optional[MetricValue] = None
    opex_rent_utilities: Optional[MetricValue] = None
    opex_software_subscriptions: Optional[MetricValue] = None
    opex_travel_entertainment: Optional[MetricValue] = None
    opex_legal_professional_fees: Optional[MetricValue] = None
    opex_insurance: Optional[MetricValue] = None
    opex_research_development: Optional[MetricValue] = None
    opex_administrative: Optional[MetricValue] = None
    opex_miscellaneous: Optional[MetricValue] = None
    opex_total: Optional[MetricValue] = None
    ebitda: Optional[MetricValue] = None
    ebit: Optional[MetricValue] = None
    depreciation_and_amortization: Optional[MetricValue] = None
    operating_profit_or_loss: Optional[MetricValue] = None
    interest_income: Optional[MetricValue] = None
    interest_expense: Optional[MetricValue] = None
    forex_gain_loss: Optional[MetricValue] = None
    exceptional_items: Optional[MetricValue] = None
    other_income_expense: Optional[MetricValue] = None
    tax_expense: Optional[MetricValue] = None
    deferred_tax: Optional[MetricValue] = None
    net_profit_before_tax: Optional[MetricValue] = None
    net_profit_after_tax: Optional[MetricValue] = None
    net_margin_percent: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheetCurrentAssets(BaseModel):
    cash_and_bank_balance: Optional[MetricValue] = None
    accounts_receivable: Optional[MetricValue] = None
    inventory: Optional[MetricValue] = None
    prepaid_expenses: Optional[MetricValue] = None
    short_term_investments: Optional[MetricValue] = None
    other_current_assets: Optional[MetricValue] = None
    total_current_assets: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheetNonCurrentAssets(BaseModel):
    property_plant_equipment: Optional[MetricValue] = None
    machinery_and_equipment: Optional[MetricValue] = None
    intangible_assets: Optional[MetricValue] = None
    capital_work_in_progress: Optional[MetricValue] = None
    long_term_investments: Optional[MetricValue] = None
    deferred_tax_assets: Optional[MetricValue] = None
    other_non_current_assets: Optional[MetricValue] = None
    total_non_current_assets: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheetCurrentLiabilities(BaseModel):
    accounts_payable: Optional[MetricValue] = None
    accrued_expenses: Optional[MetricValue] = None
    short_term_borrowings: Optional[MetricValue] = None
    current_portion_long_term_debt: Optional[MetricValue] = None
    tax_payable: Optional[MetricValue] = None
    customer_advances: Optional[MetricValue] = None
    other_current_liabilities: Optional[MetricValue] = None
    total_current_liabilities: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheetNonCurrentLiabilities(BaseModel):
    long_term_loans: Optional[MetricValue] = None
    convertible_notes: Optional[MetricValue] = None
    lease_liabilities: Optional[MetricValue] = None
    deferred_tax_liabilities: Optional[MetricValue] = None
    other_long_term_liabilities: Optional[MetricValue] = None
    total_non_current_liabilities: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheetEquity(BaseModel):
    share_capital: Optional[MetricValue] = None
    additional_paid_in_capital: Optional[MetricValue] = None
    retained_earnings: Optional[MetricValue] = None
    reserves: Optional[MetricValue] = None
    treasury_shares: Optional[MetricValue] = None
    total_shareholders_equity: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheet(BaseModel):
    current_assets: Optional[HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheetCurrentAssets] = None
    non_current_assets: Optional[HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheetNonCurrentAssets] = None
    total_assets: Optional[MetricValue] = None
    current_liabilities: Optional[HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheetCurrentLiabilities] = None
    non_current_liabilities: Optional[HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheetNonCurrentLiabilities] = None
    total_liabilities: Optional[MetricValue] = None
    equity: Optional[HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheetEquity] = None
    total_liabilities_and_equity: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemCashFlowStatementOperatingActivities(BaseModel):
    net_profit_or_loss: Optional[MetricValue] = None
    depreciation_and_amortization: Optional[MetricValue] = None
    working_capital_changes: Optional[MetricValue] = None
    accounts_receivable_movement: Optional[MetricValue] = None
    inventory_movement: Optional[MetricValue] = None
    accounts_payable_movement: Optional[MetricValue] = None
    tax_paid: Optional[MetricValue] = None
    other_operating_adjustments: Optional[MetricValue] = None
    net_cash_from_operations: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemCashFlowStatementInvestingActivities(BaseModel):
    purchase_of_fixed_assets: Optional[MetricValue] = None
    sale_of_fixed_assets: Optional[MetricValue] = None
    acquisition_of_businesses: Optional[MetricValue] = None
    purchase_or_sale_of_investments: Optional[MetricValue] = None
    capital_expenditures: Optional[MetricValue] = None
    net_cash_from_investing: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemCashFlowStatementFinancingActivities(BaseModel):
    equity_funding_received: Optional[MetricValue] = None
    debt_raised: Optional[MetricValue] = None
    loan_repayment: Optional[MetricValue] = None
    interest_paid: Optional[MetricValue] = None
    dividend_paid: Optional[MetricValue] = None
    share_issue_or_buyback: Optional[MetricValue] = None
    safe_or_convertible_note_movement: Optional[MetricValue] = None
    net_cash_from_financing: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemCashFlowStatementCashMovementSummary(BaseModel):
    opening_cash_balance: Optional[MetricValue] = None
    net_cash_from_operations: Optional[MetricValue] = None
    net_cash_from_investing: Optional[MetricValue] = None
    net_cash_from_financing: Optional[MetricValue] = None
    closing_cash_balance: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItemCashFlowStatement(BaseModel):
    operating_activities: Optional[HistoricalFinancialStatementsFinancialPeriodsItemCashFlowStatementOperatingActivities] = None
    investing_activities: Optional[HistoricalFinancialStatementsFinancialPeriodsItemCashFlowStatementInvestingActivities] = None
    financing_activities: Optional[HistoricalFinancialStatementsFinancialPeriodsItemCashFlowStatementFinancingActivities] = None
    cash_movement_summary: Optional[HistoricalFinancialStatementsFinancialPeriodsItemCashFlowStatementCashMovementSummary] = None

class HistoricalFinancialStatementsFinancialPeriodsItemPeriodNotes(BaseModel):
    material_accounting_policies: Optional[MetricValue] = None
    significant_one_time_events: Optional[MetricValue] = None
    restatements_or_corrections: Optional[MetricValue] = None
    segment_notes: Optional[MetricValue] = None
    related_party_transactions: Optional[MetricValue] = None
    debt_and_funding_details: Optional[MetricValue] = None
    equity_changes_during_period: Optional[MetricValue] = None
    auditor_remarks: Optional[MetricValue] = None

class HistoricalFinancialStatementsFinancialPeriodsItem(BaseModel):
    period_label: Optional[Any] = None
    period_type: Optional[Any] = None
    period_start_date: Optional[Any] = None
    period_end_date: Optional[Any] = None
    income_statement: Optional[HistoricalFinancialStatementsFinancialPeriodsItemIncomeStatement] = None
    balance_sheet: Optional[HistoricalFinancialStatementsFinancialPeriodsItemBalanceSheet] = None
    cash_flow_statement: Optional[HistoricalFinancialStatementsFinancialPeriodsItemCashFlowStatement] = None
    period_notes: Optional[HistoricalFinancialStatementsFinancialPeriodsItemPeriodNotes] = None

class HistoricalFinancialStatementsCrossDocumentKeyDataPoints(BaseModel):
    company_name: Optional[MetricValue] = None
    financial_period: Optional[MetricValue] = None
    revenue: Optional[MetricValue] = None
    gross_margin: Optional[MetricValue] = None
    ebitda: Optional[MetricValue] = None
    net_profit: Optional[MetricValue] = None
    cash_balance: Optional[MetricValue] = None
    burn_rate: Optional[MetricValue] = None
    working_capital: Optional[MetricValue] = None
    customer_related_metrics: Optional[MetricValue] = None
    funding_received: Optional[MetricValue] = None
    debt_outstanding: Optional[MetricValue] = None
    share_capital: Optional[MetricValue] = None
    retained_earnings: Optional[MetricValue] = None
    ownership_related_financial_changes: Optional[MetricValue] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsRevenueVsPitchDeck(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsCashBalanceVsMisOrProjections(BaseModel):
    compare_against: List[str] = Field(default_factory=list)
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsGrossMarginConsistency(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsEbitdaConsistency(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsFundingVsCapTable(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsDebtConsistencyAcrossStatements(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsShareCapitalRetainedEarningsReconciliation(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsOneTimeIncomeClassification(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsPeriodAlignment(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsUnsupportedPitchDeckClaims(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class HistoricalFinancialStatementsCrossDocumentConsistencyCheckpoints(BaseModel):
    revenue_vs_pitch_deck: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsRevenueVsPitchDeck] = None
    cash_balance_vs_mis_or_projections: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsCashBalanceVsMisOrProjections] = None
    gross_margin_consistency: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsGrossMarginConsistency] = None
    ebitda_consistency: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsEbitdaConsistency] = None
    funding_vs_cap_table: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsFundingVsCapTable] = None
    debt_consistency_across_statements: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsDebtConsistencyAcrossStatements] = None
    share_capital_retained_earnings_reconciliation: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsShareCapitalRetainedEarningsReconciliation] = None
    one_time_income_classification: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsOneTimeIncomeClassification] = None
    period_alignment: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsPeriodAlignment] = None
    unsupported_pitch_deck_claims: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpointsUnsupportedPitchDeckClaims] = None

class HistoricalFinancialStatementsExtractionNotesClassificationLegend(BaseModel):
    missing_information: Optional[str] = None
    unresolved_inconsistency: Optional[str] = None
    verified_mismatch: Optional[str] = None

class HistoricalFinancialStatementsExtractionNotes(BaseModel):
    missing_fields: List[str] = Field(default_factory=list)
    ambiguous_or_unclear_fields: List[str] = Field(default_factory=list)
    opening_closing_balance_reconciliation_check: Optional[Any] = None
    classification_legend: Optional[HistoricalFinancialStatementsExtractionNotesClassificationLegend] = None

class HistoricalFinancialStatements(BaseModel):
    document_metadata: Optional[HistoricalFinancialStatementsDocumentMetadata] = None
    financial_periods: List[HistoricalFinancialStatementsFinancialPeriodsItem] = Field(default_factory=list)
    cross_document_key_data_points: Optional[HistoricalFinancialStatementsCrossDocumentKeyDataPoints] = None
    cross_document_consistency_checkpoints: Optional[HistoricalFinancialStatementsCrossDocumentConsistencyCheckpoints] = None
    extraction_notes: Optional[HistoricalFinancialStatementsExtractionNotes] = None
