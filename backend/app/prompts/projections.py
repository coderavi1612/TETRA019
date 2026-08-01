class ProjectionsPrompt:
    PROMPT = (
        "DOCUMENT-SPECIFIC INSTRUCTIONS: Financial Projections\n\n"
        "Additional focus: extract one projection_periods[] entry per forecast period/column in "
        "the model (monthly, quarterly, or annual — preserve whatever granularity the source "
        "uses; do not aggregate monthly figures into quarters or vice versa).\n\n"
        "scenario.scenario_type must be extracted from explicit labeling (e.g., \"Base Case,\" "
        "\"Bull Case,\" \"Downside\") — if the document presents only a single unlabeled forecast, "
        "set scenario_type to null and note that no scenario framing was provided (this itself "
        "is a readiness signal, not a defect to paper over).\n\n"
        "breakeven.breakeven_period must be extracted from the specific period the model itself "
        "marks as breakeven (is_breakeven_period = true) or a narrative statement — never infer "
        "breakeven by scanning for the first period where net_profit_or_loss turns positive if "
        "the document doesn't itself label it as breakeven.\n\n"
        "esop_pool_expansion_assumptions: extract any stated future pool top-up plans distinct "
        "from the current cap table pool — these are forward assumptions, not current state."
    )
