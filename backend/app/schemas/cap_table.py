# Auto-generated Pydantic models for cap_table
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


class CapTableDocumentMetadata(BaseModel):
    document_type: Optional[str] = None
    file_name: Optional[Any] = None
    company_legal_name: Optional[Any] = None
    jurisdiction_of_incorporation: Optional[Any] = None
    reporting_date: Optional[Any] = None
    currency: Optional[Any] = None
    share_class_structure: Optional[Any] = None
    version_or_date: Optional[Any] = None
    prepared_by: Optional[Any] = None
    reviewed_by: Optional[Any] = None
    table_basis: Optional[Any] = None
    source_file_reference: Optional[Any] = None

class CapTableCompanyStructure(BaseModel):
    authorized_share_capital: Optional[MetricValue] = None
    issued_share_capital: Optional[MetricValue] = None
    outstanding_share_capital: Optional[MetricValue] = None
    share_classes: Optional[MetricValue] = None
    voting_rights_structure: Optional[MetricValue] = None
    preference_structure: Optional[MetricValue] = None

class CapTableCapTableSummary(BaseModel):
    total_authorized_shares: Optional[MetricValue] = None
    total_issued_shares: Optional[MetricValue] = None
    total_outstanding_shares: Optional[MetricValue] = None
    total_fully_diluted_shares: Optional[MetricValue] = None
    total_shares_in_esop_pool: Optional[MetricValue] = None

class CapTableShareholdersItem(BaseModel):
    holder_name: Optional[Any] = None
    holder_type: Optional[Any] = None
    number_of_shares_or_equivalent: Optional[MetricValue] = None
    share_class: Optional[Any] = None
    issue_date: Optional[Any] = None
    ownership_percentage: Optional[MetricValue] = None
    voting_percentage: Optional[MetricValue] = None
    diluted_ownership_percentage: Optional[MetricValue] = None
    investment_amount: Optional[MetricValue] = None
    instrument_type: Optional[Any] = None

class CapTableFoundersItem(BaseModel):
    founder_name: Optional[Any] = None
    shares_held: Optional[MetricValue] = None
    equity_split_percentage: Optional[MetricValue] = None
    vesting_terms: Optional[MetricValue] = None
    reverse_vesting_or_cliff_terms: Optional[MetricValue] = None
    dilution_after_each_round: Optional[MetricValue] = None
    transfers_between_founders: Optional[MetricValue] = None
    pledged_or_restricted_shares: Optional[MetricValue] = None

class CapTableInvestorsItem(BaseModel):
    investor_name: Optional[Any] = None
    investor_type: Optional[Any] = None
    round_invested_in: Optional[Any] = None
    amount_invested: Optional[MetricValue] = None
    instrument_type: Optional[Any] = None
    share_conversion_terms: Optional[MetricValue] = None
    number_of_shares_issued: Optional[MetricValue] = None
    ownership_percentage: Optional[MetricValue] = None
    post_money_diluted_ownership_percentage: Optional[MetricValue] = None
    voting_rights: Optional[MetricValue] = None
    liquidation_preference: Optional[MetricValue] = None

class CapTableEsop(BaseModel):
    total_pool_size: Optional[MetricValue] = None
    pool_percentage: Optional[MetricValue] = None
    options_granted: Optional[MetricValue] = None
    options_vested: Optional[MetricValue] = None
    options_unvested: Optional[MetricValue] = None
    options_exercised: Optional[MetricValue] = None
    options_available: Optional[MetricValue] = None
    reserved_options: Optional[MetricValue] = None
    expiry_date: Optional[Any] = None

class CapTableConvertibleInstrumentsSafesItem(BaseModel):
    safe_holder_name: Optional[Any] = None
    issue_date: Optional[Any] = None
    amount_invested: Optional[MetricValue] = None
    valuation_cap: Optional[MetricValue] = None
    discount_rate: Optional[MetricValue] = None
    conversion_trigger: Optional[Any] = None
    conversion_status: Optional[Any] = None
    converted_share_count: Optional[MetricValue] = None

class CapTableConvertibleInstrumentsConvertibleNotesItem(BaseModel):
    note_holder_name: Optional[Any] = None
    principal_amount: Optional[MetricValue] = None
    interest_rate: Optional[MetricValue] = None
    maturity_date: Optional[Any] = None
    discount_rate: Optional[MetricValue] = None
    valuation_cap: Optional[MetricValue] = None
    accrued_interest: Optional[MetricValue] = None
    conversion_status: Optional[Any] = None
    converted_share_count: Optional[MetricValue] = None

class CapTableConvertibleInstrumentsWarrantsItem(BaseModel):
    warrant_holder_name: Optional[Any] = None
    exercise_price: Optional[MetricValue] = None
    expiry_date: Optional[Any] = None
    number_of_warrants: Optional[MetricValue] = None
    conversion_or_exercise_status: Optional[Any] = None

class CapTableConvertibleInstruments(BaseModel):
    safes: List[CapTableConvertibleInstrumentsSafesItem] = Field(default_factory=list)
    convertible_notes: List[CapTableConvertibleInstrumentsConvertibleNotesItem] = Field(default_factory=list)
    warrants: List[CapTableConvertibleInstrumentsWarrantsItem] = Field(default_factory=list)

class CapTableFundingHistoryItem(BaseModel):
    round_name: Optional[Any] = None
    date_of_closing: Optional[Any] = None
    amount_raised: Optional[MetricValue] = None
    pre_money_valuation: Optional[MetricValue] = None
    post_money_valuation: Optional[MetricValue] = None
    share_price: Optional[MetricValue] = None
    shares_issued: Optional[MetricValue] = None
    lead_investor: Optional[Any] = None
    co_investors: Optional[Any] = None
    security_type: Optional[Any] = None
    dilution_caused_by_round: Optional[MetricValue] = None

class CapTableShareClassesAndInstrumentsItem(BaseModel):
    class_name: Optional[Any] = None
    number_issued: Optional[MetricValue] = None
    number_authorized: Optional[MetricValue] = None
    issue_price: Optional[MetricValue] = None
    liquidation_preference: Optional[MetricValue] = None
    voting_rights: Optional[MetricValue] = None
    conversion_rights: Optional[MetricValue] = None
    redemption_rights: Optional[MetricValue] = None
    anti_dilution_rights: Optional[MetricValue] = None

class CapTableOwnershipCalculationsBasicOwnership(BaseModel):
    shares_held: Optional[MetricValue] = None
    total_shares_outstanding: Optional[MetricValue] = None
    ownership_percentage: Optional[MetricValue] = None

class CapTableOwnershipCalculationsFullyDilutedOwnership(BaseModel):
    shares_plus_options: Optional[MetricValue] = None
    shares_plus_safes: Optional[MetricValue] = None
    shares_plus_convertible_notes: Optional[MetricValue] = None
    shares_after_assumed_future_conversions: Optional[MetricValue] = None

class CapTableOwnershipCalculations(BaseModel):
    basic_ownership: Optional[CapTableOwnershipCalculationsBasicOwnership] = None
    fully_diluted_ownership: Optional[CapTableOwnershipCalculationsFullyDilutedOwnership] = None
    voting_ownership: Optional[MetricValue] = None
    founder_dilution: Optional[MetricValue] = None
    investor_concentration: Optional[MetricValue] = None

class CapTableDilutionAndChangeHistoryItem(BaseModel):
    date_of_change: Optional[Any] = None
    event_type: Optional[Any] = None
    number_of_shares_issued_or_transferred: Optional[MetricValue] = None
    parties_involved: Optional[Any] = None
    resulting_ownership_percentage: Optional[MetricValue] = None
    resulting_diluted_ownership_percentage: Optional[MetricValue] = None

class CapTableCapTableNotes(BaseModel):
    vesting_details: Optional[MetricValue] = None
    conversion_assumptions: Optional[MetricValue] = None
    pool_refresh_assumptions: Optional[MetricValue] = None
    transfer_restrictions: Optional[MetricValue] = None
    exceptions_or_corrections: Optional[MetricValue] = None

class CapTableCrossDocumentKeyDataPoints(BaseModel):
    company_legal_name: Optional[MetricValue] = None
    reporting_date: Optional[MetricValue] = None
    founder_names: Optional[MetricValue] = None
    investor_names: Optional[MetricValue] = None
    total_shares_outstanding: Optional[MetricValue] = None
    authorized_shares: Optional[MetricValue] = None
    issued_shares: Optional[MetricValue] = None
    share_class: Optional[MetricValue] = None
    ownership_percentage: Optional[MetricValue] = None
    fully_diluted_percentage: Optional[MetricValue] = None
    voting_percentage: Optional[MetricValue] = None
    amount_invested: Optional[MetricValue] = None
    round_name: Optional[MetricValue] = None
    valuation: Optional[MetricValue] = None
    esop_pool_size: Optional[MetricValue] = None
    esop_granted: Optional[MetricValue] = None
    esop_available: Optional[MetricValue] = None
    safe_amount: Optional[MetricValue] = None
    convertible_note_amount: Optional[MetricValue] = None
    conversion_terms: Optional[MetricValue] = None
    dilution_percentage: Optional[MetricValue] = None

class CapTableReconciliationCheckpointsBalanceSheetReconciliationShareCapitalMatchesCapTable(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsBalanceSheetReconciliationAdditionalPaidInCapitalAlignsWithFinancingHistory(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsBalanceSheetReconciliationEquityInflowsMatchCashFlowFromFinancing(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsBalanceSheetReconciliationRetainedEarningsAlignWithHistoricalPnl(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsBalanceSheetReconciliation(BaseModel):
    share_capital_matches_cap_table: Optional[CapTableReconciliationCheckpointsBalanceSheetReconciliationShareCapitalMatchesCapTable] = None
    additional_paid_in_capital_aligns_with_financing_history: Optional[CapTableReconciliationCheckpointsBalanceSheetReconciliationAdditionalPaidInCapitalAlignsWithFinancingHistory] = None
    equity_inflows_match_cash_flow_from_financing: Optional[CapTableReconciliationCheckpointsBalanceSheetReconciliationEquityInflowsMatchCashFlowFromFinancing] = None
    retained_earnings_align_with_historical_pnl: Optional[CapTableReconciliationCheckpointsBalanceSheetReconciliationRetainedEarningsAlignWithHistoricalPnl] = None

class CapTableReconciliationCheckpointsPitchDeckReconciliationFounderOwnershipClaims(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsPitchDeckReconciliationTotalAmountRaised(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsPitchDeckReconciliationInvestorNames(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsPitchDeckReconciliationCurrentRoundStatus(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsPitchDeckReconciliationUseOfProceeds(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsPitchDeckReconciliationEsopSize(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsPitchDeckReconciliation(BaseModel):
    founder_ownership_claims: Optional[CapTableReconciliationCheckpointsPitchDeckReconciliationFounderOwnershipClaims] = None
    total_amount_raised: Optional[CapTableReconciliationCheckpointsPitchDeckReconciliationTotalAmountRaised] = None
    investor_names: Optional[CapTableReconciliationCheckpointsPitchDeckReconciliationInvestorNames] = None
    current_round_status: Optional[CapTableReconciliationCheckpointsPitchDeckReconciliationCurrentRoundStatus] = None
    use_of_proceeds: Optional[CapTableReconciliationCheckpointsPitchDeckReconciliationUseOfProceeds] = None
    esop_size: Optional[CapTableReconciliationCheckpointsPitchDeckReconciliationEsopSize] = None

class CapTableReconciliationCheckpointsFinancialStatementReconciliationEquityEntriesMatchFundingRounds(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsFinancialStatementReconciliationConvertedSecuritiesAppearProperly(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsFinancialStatementReconciliationSafeAndNoteReceiptsAlignWithFinancingCashFlow(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsFinancialStatementReconciliationShareCountChangesConsistentWithBalanceSheet(BaseModel):
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableReconciliationCheckpointsFinancialStatementReconciliation(BaseModel):
    equity_entries_match_funding_rounds: Optional[CapTableReconciliationCheckpointsFinancialStatementReconciliationEquityEntriesMatchFundingRounds] = None
    converted_securities_appear_properly: Optional[CapTableReconciliationCheckpointsFinancialStatementReconciliationConvertedSecuritiesAppearProperly] = None
    safe_and_note_receipts_align_with_financing_cash_flow: Optional[CapTableReconciliationCheckpointsFinancialStatementReconciliationSafeAndNoteReceiptsAlignWithFinancingCashFlow] = None
    share_count_changes_consistent_with_balance_sheet: Optional[CapTableReconciliationCheckpointsFinancialStatementReconciliationShareCountChangesConsistentWithBalanceSheet] = None

class CapTableReconciliationCheckpoints(BaseModel):
    balance_sheet_reconciliation: Optional[CapTableReconciliationCheckpointsBalanceSheetReconciliation] = None
    pitch_deck_reconciliation: Optional[CapTableReconciliationCheckpointsPitchDeckReconciliation] = None
    financial_statement_reconciliation: Optional[CapTableReconciliationCheckpointsFinancialStatementReconciliation] = None

class CapTableCrossDocumentConsistencyCheckpointsFounderOwnershipVsPitchDeck(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableCrossDocumentConsistencyCheckpointsAmountRaisedVsPitchDeck(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableCrossDocumentConsistencyCheckpointsEsopSizeVsPitchDeck(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableCrossDocumentConsistencyCheckpointsConvertibleNoteVsFinancialStatements(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableCrossDocumentConsistencyCheckpointsSafeVsProjectionsOrFundingNotes(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableCrossDocumentConsistencyCheckpointsShareCountVsEquityBalance(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableCrossDocumentConsistencyCheckpointsPostMoneyOwnershipVsDilutionMath(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableCrossDocumentConsistencyCheckpointsInvestorNamesConsistency(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableCrossDocumentConsistencyCheckpointsRoundDatesConsistency(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableCrossDocumentConsistencyCheckpointsFullyDilutedOwnershipDisclosure(BaseModel):
    compare_against: Optional[str] = None
    typical_flag: Optional[str] = None
    status: Optional[Any] = None
    notes: Optional[Any] = None

class CapTableCrossDocumentConsistencyCheckpoints(BaseModel):
    founder_ownership_vs_pitch_deck: Optional[CapTableCrossDocumentConsistencyCheckpointsFounderOwnershipVsPitchDeck] = None
    amount_raised_vs_pitch_deck: Optional[CapTableCrossDocumentConsistencyCheckpointsAmountRaisedVsPitchDeck] = None
    esop_size_vs_pitch_deck: Optional[CapTableCrossDocumentConsistencyCheckpointsEsopSizeVsPitchDeck] = None
    convertible_note_vs_financial_statements: Optional[CapTableCrossDocumentConsistencyCheckpointsConvertibleNoteVsFinancialStatements] = None
    safe_vs_projections_or_funding_notes: Optional[CapTableCrossDocumentConsistencyCheckpointsSafeVsProjectionsOrFundingNotes] = None
    share_count_vs_equity_balance: Optional[CapTableCrossDocumentConsistencyCheckpointsShareCountVsEquityBalance] = None
    post_money_ownership_vs_dilution_math: Optional[CapTableCrossDocumentConsistencyCheckpointsPostMoneyOwnershipVsDilutionMath] = None
    investor_names_consistency: Optional[CapTableCrossDocumentConsistencyCheckpointsInvestorNamesConsistency] = None
    round_dates_consistency: Optional[CapTableCrossDocumentConsistencyCheckpointsRoundDatesConsistency] = None
    fully_diluted_ownership_disclosure: Optional[CapTableCrossDocumentConsistencyCheckpointsFullyDilutedOwnershipDisclosure] = None

class CapTableExtractionNotesClassificationLegend(BaseModel):
    missing_information: Optional[str] = None
    unresolved_inconsistency: Optional[str] = None
    verified_mismatch: Optional[str] = None

class CapTableExtractionNotes(BaseModel):
    missing_fields: List[str] = Field(default_factory=list)
    ambiguous_or_unclear_fields: List[str] = Field(default_factory=list)
    classification_legend: Optional[CapTableExtractionNotesClassificationLegend] = None

class CapTable(BaseModel):
    document_metadata: Optional[CapTableDocumentMetadata] = None
    company_structure: Optional[CapTableCompanyStructure] = None
    cap_table_summary: Optional[CapTableCapTableSummary] = None
    shareholders: List[CapTableShareholdersItem] = Field(default_factory=list)
    founders: List[CapTableFoundersItem] = Field(default_factory=list)
    investors: List[CapTableInvestorsItem] = Field(default_factory=list)
    esop: Optional[CapTableEsop] = None
    convertible_instruments: Optional[CapTableConvertibleInstruments] = None
    funding_history: List[CapTableFundingHistoryItem] = Field(default_factory=list)
    share_classes_and_instruments: List[CapTableShareClassesAndInstrumentsItem] = Field(default_factory=list)
    ownership_calculations: Optional[CapTableOwnershipCalculations] = None
    dilution_and_change_history: List[CapTableDilutionAndChangeHistoryItem] = Field(default_factory=list)
    cap_table_notes: Optional[CapTableCapTableNotes] = None
    cross_document_key_data_points: Optional[CapTableCrossDocumentKeyDataPoints] = None
    reconciliation_checkpoints: Optional[CapTableReconciliationCheckpoints] = None
    cross_document_consistency_checkpoints: Optional[CapTableCrossDocumentConsistencyCheckpoints] = None
    extraction_notes: Optional[CapTableExtractionNotes] = None
