class CapTablePrompt:
    PROMPT = (
        "DOCUMENT-SPECIFIC INSTRUCTIONS: Cap Table\n"
        "Cap tables record equity ownership allocations. Focus on extracting:\n"
        "- Shareholder details: Founder and investor names, shares owned, and ownership/voting percentages\n"
        "- Corporate capitalization: Authorized/issued shares and share classes\n"
        "- Funding transactions: Historical amounts invested, round valuations, and round names\n"
        "- ESOP pools: Total pool size, shares granted, and available ESOP shares\n"
        "- Dilutive instruments: SAFE and convertible note sizes"
    )
