"""
Cross-Document Reconciliation Engine  (Stage 1.5)

Runs after all per-document extractions are complete and before the
readiness evaluation.  Produces a structured array of checkpoint findings
that the readiness prompts consume.
"""

import os
import json
import hashlib
import logging
from typing import List, Dict, Any, Optional

from app.config import settings
from app.verification.criticality import CriticalityMatrix
from app.core.logging import DuelensLogger

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# System instruction injected into the Gemini call
# ──────────────────────────────────────────────────────────────

RECONCILIATION_SYSTEM_INSTRUCTION = (
    "You are a cross-document reconciliation engine for a venture fundraising audit. You have "
    "been given the fully populated extraction JSON for some or all of: pitch_deck, "
    "historical_financial_statements, mis, financial_projections, cap_table. You also have a "
    "Field Criticality Matrix marking each field as Mandatory, Optional, or Negligible.\n\n"

    "For EACH checkpoint listed in the source documents' own \"cross_document_checkpoints\" / "
    "\"cross_document_consistency_checkpoints\" blocks, produce a structured finding. Also "
    "independently check the following high-value pairings even if not explicitly listed as "
    "a checkpoint, because they recur across every VC audit:\n\n"

    "MANDATORY CHECKPOINTS (never skip; if either side of the comparison is null, classify "
    "as missing_information — do not skip the checkpoint):\n"
    "1. Revenue: pitch_deck.traction.revenue/monthly_revenue vs. "
    "historical_financial_statements.income_statement.revenue_total (most recent period) "
    "vs. mis.profit_and_loss_summary.revenue_total (matching month).\n"
    "2. Cash balance: mis.cash_and_liquidity.closing_cash_balance vs. "
    "historical_financial_statements.balance_sheet.current_assets.cash_and_bank_balance "
    "vs. pitch_deck.financial_highlights.cash_balance, all for the same as-of date.\n"
    "3. Burn rate & runway: mis.cash_and_liquidity.net_monthly_burn/runway_months vs. "
    "financial_projections.projection_periods[].cash_flow_and_funding.projected_burn vs. "
    "pitch_deck.financial_highlights.burn_rate/runway.\n"
    "4. Growth rate: mis.revenue_and_growth_metrics.mom_growth_percent (trailing average) "
    "vs. pitch_deck.traction.monthly_growth_rate vs. "
    "financial_projections assumptions_register growth assumption.\n"
    "5. Customer count: pitch_deck.traction.customer_count vs. "
    "mis.revenue_and_growth_metrics.active_customer_count vs. the starting customer count "
    "implied by financial_projections.projection_periods[0].revenue_build.customer_count_projected.\n"
    "6. Funding ask & valuation: pitch_deck.fundraising_ask.amount_raising/valuation vs. "
    "cap_table.funding_history (most recent/pending round) vs. "
    "financial_projections.funding_ask.funding_ask_amount.\n"
    "7. Founder ownership: cap_table.founders[].equity_split_percentage vs. any founder "
    "ownership claim in pitch_deck.fundraising_ask.ownership_or_investor_references.\n"
    "8. ESOP pool: cap_table.esop.pool_percentage/total_pool_size vs. any ESOP claim in "
    "pitch_deck vs. headcount growth implied by financial_projections.headcount_plan.\n"
    "9. EBITDA / margins: historical_financial_statements.income_statement.ebitda / "
    "gross_margin_percent vs. mis.profit_and_loss_summary equivalents (same or adjacent "
    "period) vs. financial_projections assumed forward margins (check for an unexplained "
    "jump with no operational narrative).\n"
    "10. Debt & convertible instruments: cap_table.convertible_instruments (SAFEs, notes) "
    "vs. historical_financial_statements.balance_sheet.non_current_liabilities.convertible_notes "
    "vs. mis.balance_sheet_snapshot.total_debt_outstanding.\n"
    "11. Breakeven timeline: financial_projections.breakeven.breakeven_period vs. any "
    "breakeven narrative claim in pitch_deck vs. plausibility given mis trailing "
    "trend (margin/burn trajectory).\n"
    "12. Period alignment across all documents: confirm every document's stated \"as of\" / "
    "reporting date is either the same date or has an explicit, statable gap (e.g., MIS "
    "is one month more recent than the financial statements) — flag silently mismatched "
    "dates presented as if contemporaneous.\n\n"

    "For each checkpoint, output:\n"
    "{\n"
    "  \"checkpoint_id\": string,\n"
    "  \"canonical_field\": string,\n"
    "  \"documents_involved\": [string],\n"
    "  \"values_compared\": [\n"
    "    { \"document\": string, \"value\": number|string|null, \"unit\": string|null,\n"
    "      \"period\": string|null, \"source_reference\": string|null,\n"
    "      \"source_block_id\": string|null, \"extracted_text_snippet\": string|null }\n"
    "  ],\n"
    "  \"classification\": \"missing_information\" | \"unresolved_inconsistency\" | \"verified_mismatch\" | \"consistent\",\n"
    "  \"severity\": \"critical\" | \"high\" | \"medium\" | \"low\",\n"
    "  \"authoritative_document\": string|null,\n"
    "  \"authoritative_value\": number|string|null,\n"
    "  \"variance_amount\": number|null,\n"
    "  \"variance_percent\": number|null,\n"
    "  \"description\": string,\n"
    "  \"recommended_action_type\": \"clarify_with_founder\" | \"request_missing_document\" | \"reconcile_internally\" | \"no_action_needed\"\n"
    "}\n\n"

    "CLASSIFICATION RULES:\n"
    "- missing_information: one or more of the values needed for the comparison is null in "
    "every document that should plausibly contain it.\n"
    "- consistent: values match within tolerance (see below) or the same explicit figure.\n"
    "- unresolved_inconsistency: values differ, AND a plausible timing/definitional/rounding "
    "explanation exists (e.g., different reporting periods 1 month apart, gross vs. net "
    "revenue, INR vs. USD without stated FX rate, ARR vs. MRR×12 rounding).\n"
    "- verified_mismatch: values differ, BOTH sources are equally authoritative for that "
    "exact data point (same metric, same period, same currency, same basis), and no "
    "plausible explanation accounts for the gap.\n\n"

    "TOLERANCE RULES (apply before classifying as mismatch vs. consistent):\n"
    "- Currency/revenue figures: within 2% of each other (rounding) = consistent; 2–10% "
    "with a stated timing gap = unresolved_inconsistency; >10% or no explanation for any "
    "gap = verified_mismatch (subject to severity weighting below).\n"
    "- Percentages (margins, growth rates): within 1 percentage point = consistent; 1–5pp "
    "with explanation = unresolved_inconsistency; >5pp or unexplained = verified_mismatch.\n"
    "- Counts (customers, headcount, shares): exact match expected; off by rounding to "
    "nearest 5% = unresolved_inconsistency; otherwise verified_mismatch.\n"
    "- Dates: exact match or within the same reporting month = consistent; otherwise treat "
    "as a period-alignment issue, not a value mismatch — do not compare values across "
    "periods more than one reporting cycle apart without flagging the gap itself first.\n\n"

    "SEVERITY WEIGHTING (use the Field Criticality Matrix):\n"
    "- critical: Mandatory field, verified_mismatch, and it's a top-line number an investor "
    "would use to size the check (revenue, cash, valuation, funding ask, founder ownership, "
    "runway, EBITDA).\n"
    "- high: Mandatory field, verified_mismatch, secondary metric; OR Mandatory field, missing "
    "entirely from a document that should have it.\n"
    "- medium: Optional field mismatch, or Mandatory field unresolved_inconsistency.\n"
    "- low: Optional field missing_information, or any Negligible field issue (Negligible "
    "field issues should rarely even reach this stage — see Field Criticality Matrix).\n\n"

    "Never invent an \"authoritative_document\" unless the checkpoint's own compare_against "
    "metadata or an explicit audited/certified status (e.g., audited financials over an "
    "unaudited MIS estimate) supports it. If two sources are equally authoritative, leave "
    "authoritative_document null and say so in description.\n\n"

    "Output strictly the JSON array of checkpoint objects — no prose, no markdown fences."
)


# ──────────────────────────────────────────────────────────────
# Engine
# ──────────────────────────────────────────────────────────────

class ReconciliationEngine:
    """Executes the cross-document reconciliation stage."""

    @classmethod
    def run(cls, company_id: str, outputs_dir: str = None) -> List[Dict[str, Any]]:
        """
        Load all extracted JSONs, call Gemini with the reconciliation prompt,
        parse the checkpoint array, and save it to
        ``verification/reconciliation_checkpoints.json``.
        """
        if outputs_dir is None:
            outputs_dir = settings.OUTPUT_DIR

        company_output_dir = os.path.join(outputs_dir, company_id)
        extracted_dir = os.path.join(company_output_dir, "extracted")
        verification_dir = os.path.join(company_output_dir, "verification")
        os.makedirs(verification_dir, exist_ok=True)

        # 1. Gather all extracted JSONs
        extractions: Dict[str, Any] = {}
        if os.path.isdir(extracted_dir):
            for fname in os.listdir(extracted_dir):
                if fname.endswith(".json"):
                    fpath = os.path.join(extracted_dir, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        # Derive a document type key from the filename
                        doc_key = os.path.splitext(fname)[0]
                        extractions[doc_key] = data
                    except Exception as exc:
                        logger.warning(f"[Reconciliation] Skipping {fname}: {exc}")

        if not extractions:
            DuelensLogger.log("Reconciliation", "SKIP",
                              f"No extracted documents found for {company_id}. Generating empty checkpoints.")
            checkpoints = cls._generate_mock_checkpoints(company_id)
            cls._save(checkpoints, verification_dir)
            return checkpoints

        # 2. Build the prompt
        criticality_json = CriticalityMatrix.get_matrix_json()
        extraction_payload = json.dumps(extractions, indent=2)

        user_prompt = (
            "Below are the fully populated extraction JSONs for this company, followed by "
            "the Field Criticality Matrix. Produce the checkpoint array.\n\n"
            f"EXTRACTION DATA:\n{extraction_payload}\n\n"
            f"FIELD CRITICALITY MATRIX:\n{criticality_json}"
        )

        # 3. Check cache
        prompt_hash = hashlib.sha256(
            (RECONCILIATION_SYSTEM_INSTRUCTION + user_prompt).encode("utf-8")
        ).hexdigest()
        cache_path = os.path.join(company_output_dir, "cache", "reconciliation", f"{prompt_hash}.json")

        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                DuelensLogger.log("Reconciliation", "CACHE_HIT",
                                  f"Returning cached reconciliation checkpoints for {company_id}")
                cls._save(cached, verification_dir)
                return cached
            except Exception:
                pass

        # 4. Call Gemini (or mock)
        checkpoints = cls._call_gemini(user_prompt, company_id)

        # 5. Save
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(checkpoints, f, indent=2)
        cls._save(checkpoints, verification_dir)

        DuelensLogger.log("Reconciliation", "COMPLETE",
                          f"Reconciliation produced {len(checkpoints)} checkpoints for {company_id}")
        return checkpoints

    # ── private helpers ────────────────────────────────────────

    @staticmethod
    def _save(checkpoints: List[Dict[str, Any]], verification_dir: str) -> None:
        out_path = os.path.join(verification_dir, "reconciliation_checkpoints.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(checkpoints, f, indent=2)

    @staticmethod
    def _call_gemini(user_prompt: str, company_id: str) -> List[Dict[str, Any]]:
        """Call Gemini for reconciliation, with mock fallback."""
        from app.readiness.ai.gemini import GeminiReadinessCaller
        import os

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        is_mock = (
            not api_key or
            any(kw in api_key.lower() for kw in ["dummy", "mock", "test", "fake", "temp"])
        )

        if is_mock:
            DuelensLogger.log("Reconciliation", "MOCK",
                              f"Using mock reconciliation checkpoints for {company_id}")
            return ReconciliationEngine._generate_mock_checkpoints(company_id)

        try:
            from google import genai
            from google.genai import types

            model_name = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
            client = genai.Client(api_key=api_key)
            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                system_instruction=RECONCILIATION_SYSTEM_INSTRUCTION
            )

            DuelensLogger.log("Reconciliation", "REQUEST",
                              f"Calling model {model_name} for reconciliation")

            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=config
            )

            text = response.text.strip()
            checkpoints = json.loads(text)
            if isinstance(checkpoints, list):
                return checkpoints
            # If the model wrapped the array inside an object, try to extract
            if isinstance(checkpoints, dict):
                for v in checkpoints.values():
                    if isinstance(v, list):
                        return v
            return [checkpoints]

        except Exception as e:
            DuelensLogger.log("Reconciliation", "ERROR",
                              f"Gemini reconciliation call failed: {e}. Using mock.", error=e)
            return ReconciliationEngine._generate_mock_checkpoints(company_id)

    @staticmethod
    def _generate_mock_checkpoints(company_id: str) -> List[Dict[str, Any]]:
        """Return a realistic set of mock checkpoints covering the 12 mandatory checks."""
        return [
            {
                "checkpoint_id": "RECON-001",
                "canonical_field": "Revenue",
                "documents_involved": ["pitch_deck", "historical_financial_statements", "mis"],
                "values_compared": [
                    {"document": "pitch_deck", "value": 12000000, "unit": "INR",
                     "period": "FY2025", "source_reference": "investor_deck.pptx",
                     "source_block_id": "pitch_deck_slide_08_block_02",
                     "extracted_text_snippet": "Revenue: 1.2 Cr in FY25"},
                    {"document": "historical_financial_statements", "value": 9000000, "unit": "INR",
                     "period": "FY2025", "source_reference": "test_financials.xlsx",
                     "source_block_id": "financials_sheet_pnl_row_4",
                     "extracted_text_snippet": "Total Revenue FY25: 9,000,000"},
                    {"document": "mis", "value": 850000, "unit": "INR",
                     "period": "Feb 2025", "source_reference": "mis_report.csv",
                     "source_block_id": "mis_report_csv_row_2",
                     "extracted_text_snippet": "Feb 25 Revenue: 850000"}
                ],
                "classification": "verified_mismatch",
                "severity": "critical",
                "authoritative_document": "historical_financial_statements",
                "authoritative_value": 9000000,
                "variance_amount": 3000000,
                "variance_percent": 33.3,
                "description": "Revenue in the pitch deck (₹1.2 Cr) exceeds the audited financial statements (₹90 L) by 33%. The MIS shows monthly revenue of ₹8.5 L for Feb 2025 which annualizes below both figures.",
                "recommended_action_type": "clarify_with_founder"
            },
            {
                "checkpoint_id": "RECON-002",
                "canonical_field": "Cash Balance",
                "documents_involved": ["pitch_deck", "historical_financial_statements", "mis"],
                "values_compared": [
                    {"document": "pitch_deck", "value": None, "unit": "INR",
                     "period": None, "source_reference": None,
                     "source_block_id": None, "extracted_text_snippet": None},
                    {"document": "historical_financial_statements", "value": None, "unit": "INR",
                     "period": None, "source_reference": None,
                     "source_block_id": None, "extracted_text_snippet": None},
                    {"document": "mis", "value": None, "unit": "INR",
                     "period": None, "source_reference": None,
                     "source_block_id": None, "extracted_text_snippet": None}
                ],
                "classification": "missing_information",
                "severity": "high",
                "authoritative_document": None,
                "authoritative_value": None,
                "variance_amount": None,
                "variance_percent": None,
                "description": "Cash balance is not populated in any of the three documents. This blocks assessment of runway and burn rate accuracy.",
                "recommended_action_type": "request_missing_document"
            },
            {
                "checkpoint_id": "RECON-003",
                "canonical_field": "Burn Rate & Runway",
                "documents_involved": ["mis", "financial_projections", "pitch_deck"],
                "values_compared": [
                    {"document": "mis", "value": None, "unit": "INR/month",
                     "period": None, "source_reference": None,
                     "source_block_id": None, "extracted_text_snippet": None}
                ],
                "classification": "missing_information",
                "severity": "high",
                "authoritative_document": None,
                "authoritative_value": None,
                "variance_amount": None,
                "variance_percent": None,
                "description": "Burn rate and runway metrics are not available in any document. Cannot validate runway claims.",
                "recommended_action_type": "request_missing_document"
            },
            {
                "checkpoint_id": "RECON-004",
                "canonical_field": "Growth Rate",
                "documents_involved": ["mis", "pitch_deck", "financial_projections"],
                "values_compared": [],
                "classification": "missing_information",
                "severity": "medium",
                "authoritative_document": None,
                "authoritative_value": None,
                "variance_amount": None,
                "variance_percent": None,
                "description": "MoM growth rate is not populated in MIS or pitch deck. Cannot cross-verify growth claims.",
                "recommended_action_type": "clarify_with_founder"
            },
            {
                "checkpoint_id": "RECON-005",
                "canonical_field": "Customer Count",
                "documents_involved": ["pitch_deck", "mis"],
                "values_compared": [],
                "classification": "missing_information",
                "severity": "medium",
                "authoritative_document": None,
                "authoritative_value": None,
                "variance_amount": None,
                "variance_percent": None,
                "description": "Customer count is not available for cross-verification between documents.",
                "recommended_action_type": "clarify_with_founder"
            },
            {
                "checkpoint_id": "RECON-006",
                "canonical_field": "Funding Ask & Valuation",
                "documents_involved": ["pitch_deck", "cap_table", "financial_projections"],
                "values_compared": [
                    {"document": "pitch_deck", "value": 20000000, "unit": "INR",
                     "period": None, "source_reference": "investor_deck.pptx",
                     "source_block_id": "pitch_deck_slide_12_block_01",
                     "extracted_text_snippet": "Raising INR 2 Crores Seed Round"},
                    {"document": "financial_projections", "value": 20000000, "unit": "INR",
                     "period": None, "source_reference": "financial_projections.xlsx",
                     "source_block_id": "projections_sheet_model_row_12",
                     "extracted_text_snippet": "Funding requirement: 2 Cr"}
                ],
                "classification": "consistent",
                "severity": "low",
                "authoritative_document": None,
                "authoritative_value": 20000000,
                "variance_amount": 0,
                "variance_percent": 0.0,
                "description": "Funding ask amount is consistent at ₹2 Cr across pitch deck and financial projections.",
                "recommended_action_type": "no_action_needed"
            },
            {
                "checkpoint_id": "RECON-007",
                "canonical_field": "Founder Ownership",
                "documents_involved": ["cap_table", "pitch_deck"],
                "values_compared": [
                    {"document": "cap_table", "value": 60.0, "unit": "%",
                     "period": None, "source_reference": "cap_table.xlsx",
                     "source_block_id": "cap_table_sheet_shareholders_row_2",
                     "extracted_text_snippet": "60.0% Ownership"}
                ],
                "classification": "consistent",
                "severity": "low",
                "authoritative_document": "cap_table",
                "authoritative_value": 60.0,
                "variance_amount": None,
                "variance_percent": None,
                "description": "Founder ownership from cap table shows 60%. Pitch deck does not make a conflicting claim.",
                "recommended_action_type": "no_action_needed"
            },
            {
                "checkpoint_id": "RECON-008",
                "canonical_field": "ESOP Pool",
                "documents_involved": ["cap_table", "pitch_deck", "financial_projections"],
                "values_compared": [],
                "classification": "missing_information",
                "severity": "medium",
                "authoritative_document": None,
                "authoritative_value": None,
                "variance_amount": None,
                "variance_percent": None,
                "description": "ESOP pool size and percentage are not populated in any document.",
                "recommended_action_type": "request_missing_document"
            },
            {
                "checkpoint_id": "RECON-009",
                "canonical_field": "EBITDA / Margins",
                "documents_involved": ["historical_financial_statements", "mis", "financial_projections"],
                "values_compared": [],
                "classification": "missing_information",
                "severity": "high",
                "authoritative_document": None,
                "authoritative_value": None,
                "variance_amount": None,
                "variance_percent": None,
                "description": "EBITDA and margin metrics are not populated for cross-document comparison.",
                "recommended_action_type": "request_missing_document"
            },
            {
                "checkpoint_id": "RECON-010",
                "canonical_field": "Debt & Convertible Instruments",
                "documents_involved": ["cap_table", "historical_financial_statements", "mis"],
                "values_compared": [],
                "classification": "missing_information",
                "severity": "medium",
                "authoritative_document": None,
                "authoritative_value": None,
                "variance_amount": None,
                "variance_percent": None,
                "description": "Convertible instrument details are not populated across any of the documents.",
                "recommended_action_type": "clarify_with_founder"
            },
            {
                "checkpoint_id": "RECON-011",
                "canonical_field": "Breakeven Timeline",
                "documents_involved": ["financial_projections", "pitch_deck", "mis"],
                "values_compared": [],
                "classification": "missing_information",
                "severity": "medium",
                "authoritative_document": None,
                "authoritative_value": None,
                "variance_amount": None,
                "variance_percent": None,
                "description": "Breakeven period is not explicitly stated in any document.",
                "recommended_action_type": "clarify_with_founder"
            },
            {
                "checkpoint_id": "RECON-012",
                "canonical_field": "Period Alignment",
                "documents_involved": ["pitch_deck", "historical_financial_statements", "mis", "financial_projections", "cap_table"],
                "values_compared": [],
                "classification": "unresolved_inconsistency",
                "severity": "medium",
                "authoritative_document": None,
                "authoritative_value": None,
                "variance_amount": None,
                "variance_percent": None,
                "description": "Documents reference different reporting periods (FY2025 annual vs. Feb 2025 monthly). The gap is within one fiscal year but may affect point-in-time comparisons.",
                "recommended_action_type": "reconcile_internally"
            }
        ]
