class HistoricalFinancialsPrompt:
    PROMPT = (
        "DOCUMENT-SPECIFIC INSTRUCTIONS: Historical Financial Statements\n\n"
        "Additional focus: process one financial_periods[] entry per distinct reporting period "
        "found (do not merge multiple years into one entry). For each period, confirm whether "
        "figures are audited or management/provisional as stated in document_metadata.is_audited "
        "— never assume audited status.\n\n"
        "Cross-check internal arithmetic ONLY to decide whether a subtotal/total in the source "
        "table itself is inconsistent (e.g., a printed \"Total Assets\" that doesn't sum from the "
        "line items shown in the SAME table) — flag this as an ambiguous field with the "
        "observed discrepancy, but do not silently correct it or emit a recalculated number.\n\n"
        "For cash_flow_statement, verify the opening_cash_balance of period N should visually "
        "match closing_cash_balance of period N-1 if both are present in the same document — "
        "if they don't match, note it in extraction_notes rather than editing either number."
    )
