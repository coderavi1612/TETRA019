class HistoricalFinancialsPrompt:
    PROMPT = (
        "DOCUMENT-SPECIFIC INSTRUCTIONS: Historical Financial Statements\n"
        "Financial statements provide the authoritative baseline of performance. Focus on extracting:\n"
        "- Income statement metrics (Revenue, Cost of Goods Sold, Gross Profit, Operating Expenses, EBITDA, Net Profit)\n"
        "- Balance sheet metrics (Cash Balance, Accounts Receivable, Inventories, Debt outstanding, Share Capital, Retained Earnings)\n"
        "- Cash flow statement metrics (Operating Cash Flow, Capex, Financing inflows)\n"
        "Pay special attention to column headers for fiscal periods and verify currency representations."
    )
