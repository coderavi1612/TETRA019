class MISPrompt:
    PROMPT = (
        "DOCUMENT-SPECIFIC INSTRUCTIONS: Monthly MIS Report\n\n"
        "Additional focus: extract one MIS snapshot per reporting month found in the document — "
        "if the file contains a trailing 6- or 12-month trend table, treat each column as a "
        "separate period and extract into a repeated set of periods if your calling code "
        "supports multiple MIS snapshots; otherwise extract only the most recent/labeled period "
        "and note the trend table's existence in extraction_notes for downstream trend analysis.\n\n"
        "Distinguish \"budget\" columns from \"actual\" columns explicitly — populate "
        "budget_vs_actual_variance only from a column/row that is explicitly labeled variance, "
        "never compute it yourself from separate actual and budget columns.\n\n"
        "Logo/customer mentions: extract named customers only where explicitly listed (e.g., a "
        "\"key accounts\" or \"logos\" section) — do not infer customer identity from revenue-by-"
        "segment figures."
    )
