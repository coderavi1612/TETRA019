"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { AlertTriangle, FileSearch, ArrowRight, Lightbulb, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EXTRACTION_ROWS } from "@/data/mock";
import { toast } from "sonner";

export function ExtractionReviewView() {
  const [rows] = useState(EXTRACTION_ROWS);
  const [insightApplied, setInsightApplied] = useState(false);

  const applyMIS = () => {
    setInsightApplied(true);
    toast.success("Applied MIS value (112.5%) globally for Growth Rate across documents.");
  };

  return (
    <div className="space-y-8">
      {/* Header & Stats */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary">
            <FileSearch className="size-3.5" />
            Auto-Extraction Engine
          </span>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Extraction Review
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Cross-referencing auto-extracted values across primary source documents.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="surface flex flex-col px-4 py-2.5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Avg. Confidence
            </span>
            <span className="text-xl font-extrabold text-primary tabular-nums">94.2%</span>
          </div>
          <div className="surface flex flex-col px-4 py-2.5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Unresolved Flags
            </span>
            <span className="text-xl font-extrabold text-warning tabular-nums">3</span>
          </div>
        </div>
      </div>

      {/* Main Extraction Table */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="surface overflow-hidden"
      >
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="bg-muted/70 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-6 py-4 font-semibold">KPI / Financial Metric</th>
                <th className="px-5 py-4 font-semibold">Pitch Deck</th>
                <th className="px-5 py-4 font-semibold">Financial Statements</th>
                <th className="px-5 py-4 font-semibold">Monthly MIS</th>
                <th className="px-5 py-4 font-semibold">Projections</th>
                <th className="px-5 py-4 font-semibold">Cap Table</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {rows.map((row) => (
                <tr key={row.kpi} className="transition-colors hover:bg-muted/30">
                  <td className="px-6 py-4 font-semibold text-foreground">{row.kpi}</td>

                  {/* Pitch Deck */}
                  <td className="px-5 py-4">
                    {row.pitchDeck.val !== "—" ? (
                      <div className="flex flex-col gap-1">
                        <span className="font-mono text-sm font-medium">{row.pitchDeck.val}</span>
                        <span className="inline-flex w-fit items-center gap-1 rounded bg-verified-soft px-1.5 py-0.5 text-[10px] font-bold text-verified">
                          {row.pitchDeck.conf}%
                        </span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground/50">—</span>
                    )}
                  </td>

                  {/* Financial Statements */}
                  <td className="px-5 py-4">
                    {row.financials.val !== "—" ? (
                      <div className="flex flex-col gap-1">
                        <span className="font-mono text-sm font-medium">{row.financials.val}</span>
                        <div className="flex items-center gap-1">
                          <span
                            className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-bold ${
                              row.financials.warning
                                ? "bg-warning-soft text-warning"
                                : "bg-verified-soft text-verified"
                            }`}
                          >
                            {row.financials.conf}%
                            {row.financials.warning && <AlertTriangle className="size-3" />}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <span className="text-muted-foreground/50">—</span>
                    )}
                  </td>

                  {/* Monthly MIS */}
                  <td className="px-5 py-4">
                    {row.mis.val !== "—" ? (
                      <div className="flex flex-col gap-1">
                        <span className="font-mono text-sm font-medium">
                          {row.kpi === "Growth Rate (YoY)" && insightApplied ? "112.5% (Applied)" : row.mis.val}
                        </span>
                        <div className="flex items-center gap-1">
                          <span
                            className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-bold ${
                              row.mis.warning
                                ? "bg-warning-soft text-warning"
                                : "bg-verified-soft text-verified"
                            }`}
                          >
                            {row.mis.conf}%
                            {row.mis.warning && <AlertTriangle className="size-3" />}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <span className="text-muted-foreground/50">—</span>
                    )}
                  </td>

                  {/* Projections */}
                  <td className="px-5 py-4">
                    {row.projections.val !== "—" ? (
                      <div className="flex flex-col gap-1">
                        <span className="font-mono text-sm font-medium">{row.projections.val}</span>
                        <span className="inline-flex w-fit items-center gap-1 rounded bg-verified-soft px-1.5 py-0.5 text-[10px] font-bold text-verified">
                          {row.projections.conf}%
                        </span>
                      </div>
                    ) : (
                      <span className="text-muted-foreground/50">—</span>
                    )}
                  </td>

                  {/* Cap Table */}
                  <td className="px-5 py-4">
                    {row.capTable.val !== "—" ? (
                      <div className="flex flex-col gap-1">
                        <span className="font-mono text-sm font-medium">{row.capTable.val}</span>
                        <div className="flex items-center gap-1">
                          <span
                            className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-bold ${
                              row.capTable.warning
                                ? "bg-warning-soft text-warning"
                                : "bg-verified-soft text-verified"
                            }`}
                          >
                            {row.capTable.conf}%
                            {row.capTable.warning && <AlertTriangle className="size-3" />}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <span className="text-muted-foreground/50">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Analyst Insight & Progress Grid */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* AI Insight Card */}
        <div className="surface md:col-span-2 flex flex-col justify-between border-l-4 border-l-primary p-6">
          <div className="flex items-start gap-4">
            <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-primary-soft text-primary">
              <Lightbulb className="size-5" />
            </span>
            <div>
              <h3 className="font-bold text-foreground">AI Analyst Insight</h3>
              <p className="mt-1 text-sm text-muted-foreground leading-relaxed">
                The extraction engine identified a variance in <span className="font-semibold text-foreground">Growth Rate (YoY)</span> between the{" "}
                <span className="font-semibold text-foreground">Pitch Deck (115%)</span> and <span className="font-semibold text-foreground">Monthly MIS (112.5%)</span>.
                The MIS value is derived from raw transactional ledger entries, whereas the Pitch Deck appears to be an annualized Q4 estimate.
              </p>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3 pl-15">
            <Button
              size="sm"
              onClick={applyMIS}
              disabled={insightApplied}
              className="rounded-lg shadow-[var(--shadow-glow)]"
            >
              <Check className="mr-1.5 size-4" />
              {insightApplied ? "MIS Value Applied Globally" : "Apply MIS Value Globally"}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => toast.info("Discrepancy flagged for manual controller review.")}
              className="rounded-lg"
            >
              <X className="mr-1.5 size-4" />
              Ignore Discrepancy
            </Button>
          </div>
        </div>

        {/* Status Card */}
        <div className="surface flex flex-col justify-between p-6 bg-linear-to-br from-card to-primary-soft/30">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-widest text-primary">
              Extraction Progress
            </span>
            <h3 className="mt-2 text-3xl font-extrabold text-foreground">78% Reviewed</h3>
            <p className="mt-1 text-xs text-muted-foreground">4 financial metrics remaining for manual audit.</p>
          </div>

          <div className="mt-6 space-y-3">
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-border">
              <div className="h-full rounded-full bg-primary" style={{ width: "78%" }} />
            </div>

            <div className="flex items-center justify-between text-xs font-medium">
              <span className="text-muted-foreground">Status: In Audit</span>
              <span className="flex items-center gap-1 font-semibold text-primary">
                View next metric
                <ArrowRight className="size-3.5" />
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
