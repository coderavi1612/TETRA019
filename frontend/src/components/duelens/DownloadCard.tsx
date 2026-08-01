"use client";

import { motion } from "motion/react";
import { Download, FileText, Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { toast } from "sonner";
import { downloadPDF } from "@/lib/download";
import { useDuelensData } from "@/context/DuelensDataContext";

export function DownloadCard() {
  const [state, setState] = useState<"idle" | "loading" | "done">("idle");
  const { readinessResults, issues, matrixData, companyId } = useDuelensData();

  const handleDownload = async () => {
    setState("loading");
    try {
      await downloadPDF({
        companyName: readinessResults?.summary?.company_name || (readinessResults?.summary?.company_id 
          ? readinessResults.summary.company_id.charAt(0).toUpperCase() + readinessResults.summary.company_id.slice(1)
          : companyId.charAt(0).toUpperCase() + companyId.slice(1)),
        readinessScore: readinessResults?.summary?.readiness_score ?? 0,
        overallStatus: readinessResults?.summary?.overall_status ?? "NOT_READY",
        summaryStats: [
          { label: "Verified Matches", value: readinessResults?.summary?.verified_matches ?? 0, tone: "verified" as const },
          { label: "Warnings", value: issues.filter(i => i.severity === 'WARNING').length, tone: "warning" as const },
          { label: "Critical Issues", value: issues.filter(i => i.severity === 'CRITICAL').length, tone: "critical" as const },
          { label: "Missing Information", value: readinessResults?.summary?.missing_information ?? 0, tone: "muted" as const },
        ],
        comparisonRows: (matrixData?.fields || []).map(f => {
          const values = [
            f.values?.pitch_deck?.value !== undefined ? String(f.values.pitch_deck.value) : "—",
            f.values?.historical_financial_statements?.value !== undefined ? String(f.values.historical_financial_statements.value) : "—",
            f.values?.mis?.value !== undefined ? String(f.values.mis.value) : "—",
            f.values?.financial_projections?.value !== undefined ? String(f.values.financial_projections.value) : "—",
            f.values?.cap_table?.value !== undefined ? String(f.values.cap_table.value) : "—",
          ];
          const status = f.is_consistent ? "Verified" as const : "Mismatch" as const;
          return {
            metric: f.field_path.split('.').pop()?.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') || f.field_path,
            values,
            status
          };
        }),
        discrepancies: issues.map(issue => {
          const pairs = Object.entries(issue.source_values || {}).map(([doc, val]) => ({
            label: doc.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
            value: val !== null && val !== undefined ? String(val) : "—"
          }));
          return {
            id: issue.id,
            title: issue.field_path.split('.').pop()?.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') || issue.field_path,
            kind: issue.classification,
            severity: issue.severity === 'CRITICAL' ? ('High' as const) : issue.severity === 'WARNING' ? ('Medium' as const) : ('Low' as const),
            pairs,
            note: issue.description
          };
        }),
        questions: (readinessResults?.questions || []).map(q => ({
          question: q.question
        })),
        recommendation: readinessResults?.summary?.recommendations?.[0] || 
                        (readinessResults?.executive?.immediate_actions?.[0]) || 
                        "Clarify and align all metrics before proceeding with due diligence."
      });
      setState("done");
      toast.success("Report downloaded");
      setTimeout(() => setState("idle"), 2500);
    } catch (e) {
      console.error(e);
      toast.error("Download failed — please try again");
      setState("idle");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.6 }}
      className="surface grid gap-8 p-6 md:grid-cols-[1fr_auto] md:items-center md:p-10"
    >
      <div>
        <span className="flex size-11 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-[var(--shadow-glow)]">
          <Download className="size-5" />
        </span>
        <h3 className="mt-4 text-xl font-bold">Take the report with you</h3>
        <p className="mt-2 max-w-lg text-sm text-muted-foreground">
          Export the full consistency analysis, discrepancy log and follow-up questions as a
          formatted PDF for your investment committee.
        </p>
      </div>

      <Button
        size="lg"
        className="h-12 rounded-full px-8"
        onClick={handleDownload}
        disabled={state === "loading"}
      >
        {state === "loading" ? (
          <Loader2 className="size-4 animate-spin" />
        ) : state === "done" ? (
          <Check className="size-4" />
        ) : (
          <FileText className="size-4" />
        )}
        {state === "loading" ? "Generating…" : state === "done" ? "Downloaded" : "Download Investor Report (PDF)"}
      </Button>
    </motion.div>
  );
}
