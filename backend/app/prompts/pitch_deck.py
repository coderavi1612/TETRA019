class PitchDeckPrompt:
    PROMPT = (
        "DOCUMENT-SPECIFIC INSTRUCTIONS: Pitch Deck\n"
        "Pitch decks present a high-level commercial narrative. Focus on extracting:\n"
        "- High-level financial performance claims (Revenue, Margins, Cash)\n"
        "- Traction metrics (MoM Growth %, customer counts, retention and churn)\n"
        "- Fundraising parameters (Round ask, valuation target, use of funds, founders/team headcount)\n"
        "- Market size references (TAM, SAM, SOM)\n"
        "Ensure each extracted fact is directly traceable to the specific slide number and source block."
    )
