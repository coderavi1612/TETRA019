class PitchDeckPrompt:
    PROMPT = (
        "DOCUMENT-SPECIFIC INSTRUCTIONS: Pitch Deck\n\n"
        "Additional focus: this document is narrative and promotional — extract CLAIMS, not "
        "verified facts. If a slide states a number without stating its basis or period "
        "(e.g., \"Growing 20% MoM\" with no month named), extract the claim verbatim into the "
        "snippet and leave \"period\" null rather than assuming \"current month.\"\n\n"
        "Distinguish TAM/SAM/SOM carefully — do not extract a single market-size figure into all "
        "three if the deck only states one number generically as \"market size.\"\n\n"
        "Flag (in vague_unsupported_claims) any traction, growth, or market claim that lacks a "
        "supporting number, date, or methodology — e.g., \"massive market opportunity\" or "
        "\"rapid growth\" with no figures attached.\n\n"
        "Slide/page number is mandatory whenever a value is populated — this is the primary "
        "citation the readiness report will point investors back to."
    )
