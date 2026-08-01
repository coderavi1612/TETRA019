class CapTablePrompt:
    PROMPT = (
        "DOCUMENT-SPECIFIC INSTRUCTIONS: Cap Table\n\n"
        "Additional focus: extract every shareholder/investor/founder row as a separate array "
        "entry, even if some columns are blank for that row — do not skip rows with partial data.\n\n"
        "Ownership percentages: extract both non-diluted and fully-diluted percentages "
        "separately whenever both are shown; never compute one from the other.\n\n"
        "SAFEs and convertible notes: extract valuation cap and discount rate exactly as stated, "
        "including \"N/A\" or \"no cap\" language captured verbatim in the snippet (leave value null, "
        "put the literal text in extracted_text_snippet).\n\n"
        "If the cap table shows a summary/waterfall table AND a detailed shareholder register, "
        "prefer the detailed register for shareholders[] and use the summary only to populate "
        "cap_table_summary — do not double-count the same holder from both sources."
    )
