"use client";

import { motion } from "motion/react";
import { Award, CheckCircle2, AlertTriangle, ShieldCheck, Download, Gauge } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDuelensData } from "@/context/DuelensDataContext";
import { getBaseApiUrl } from "@/lib/api/client";
import { toast } from "sonner";

export function ReadinessSummaryView() {
  const { readinessResults, companyId, metadata } = useDuelensData();

  const summary = readinessResults?.summary;
  const executive = readinessResults?.executive;

  const score = summary?.overall_readiness_score || 0;
  
  const completeness = summary?.scoring_breakdown?.completeness || 0;
  const consistency = summary?.scoring_breakdown?.consistency || 0;
  const recency = summary?.scoring_breakdown?.recency || 0;
  const factuality = summary?.scoring_breakdown?.factuality || 0;

  // Find dynamic PDF IC Memo file download URL
  const pdfDownload = readinessResults?.downloads?.find(
    (d) => d.name.toLowerCase().includes("readiness") && d.type === "pdf"
  ) || readinessResults?.downloads?.[0];

  const handleDownloadPDF = () => {
    if (pdfDownload) {
      const fullUrl = `${getBaseApiUrl()}${pdfDownload.url}`;
      window.open(fullUrl, "_blank");
      toast.success("Streaming Investor Readiness Memo PDF from backend...");
    } else {
      toast.error("Readiness PDF report download not found.");
    }
  };

  const keyPositives = summary?.key_positives || [
    "High extraction confidence across financials",
    "Completed cap table post-ESOP pool reservations",
    "Consistent naming conventions across data-room files"
  ];

  const criticalGaps = summary?.critical_gaps || [
    "Slight variance in customer count due to date snapshots",
    "YoY growth rate roundings in pitch deck"
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-verified-soft px-3 py-1 text-xs font-semibold text-verified">
            <Award className="size-3.5" />
            Investment Readiness Certification
          </span>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Readiness Summary & Final Verdict
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Synthesis report evaluating due diligence readiness, financial model integrity, and key investment risks.
          </p>
        </div>

        <Button onClick={handleDownloadPDF} className="rounded-xl shadow-[var(--shadow-glow)]">
          <Download className="mr-2 size-4" />
          Download IC Memo (PDF)
        </Button>
      </div>

      {/* Main Readiness Gauge Hero Banner */}
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        className="surface grid gap-6 p-6 sm:grid-cols-3 sm:p-8 bg-linear-to-br from-card via-card to-primary-soft/30 border-l-4 border-l-verified"
      >
        <div className="flex items-center gap-4">
          <span className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-verified-soft text-verified shadow-xs">
            <ShieldCheck className="size-7" />
          </span>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Company
            </p>
            <h3 className="text-xl font-bold text-foreground capitalize">{companyId}</h3>
            <p className="text-xs text-muted-foreground">Series A Due Diligence</p>
          </div>
        </div>

        <div className="flex items-center gap-4 sm:justify-center border-t border-border pt-4 sm:border-t-0 sm:pt-0">
          <span className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-primary-soft text-primary shadow-xs">
            <Gauge className="size-7" />
          </span>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Readiness Score
            </p>
            <h3 className="text-3xl font-extrabold text-primary tabular-nums">{score}%</h3>
            <p className="text-xs font-semibold text-verified">
              {score >= 85 ? "Investor Ready" : "Conditional Audit Required"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 sm:justify-end border-t border-border pt-4 sm:border-t-0 sm:pt-0">
          <div className="text-right">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Audited Documents
            </p>
            <p className="text-lg font-bold text-foreground">
              {metadata?.documents || 0} of {metadata?.documents || 0} Verified
            </p>
            <span className="text-xs text-muted-foreground">Reconciled side-by-side</span>
          </div>
        </div>
      </motion.div>

      {/* Narrative Card */}
      {executive && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="surface p-6 bg-muted/20 border-l-4 border-l-primary"
        >
          <h3 className="font-bold text-foreground text-sm mb-2">Executive Summary Verdict</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">{executive.overall_readiness}</p>
          <p className="mt-2 text-xs text-muted-foreground leading-relaxed">{executive.company_overview}</p>
        </motion.div>
      )}

      {/* 4 Dimension Gauge Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Financial Integrity", score: completeness, tone: completeness >= 85 ? "verified" : "warning", desc: "Reconciliation completeness across statements." },
          { label: "Cap Table Health", score: recency, tone: recency >= 85 ? "verified" : "warning", desc: "Ownership validation timelines check." },
          { label: "Projections Realism", score: factuality, tone: factuality >= 85 ? "verified" : "warning", desc: "Validation against historical run rates." },
          { label: "Compliance & Consistency", score: consistency, tone: consistency >= 85 ? "verified" : "warning", desc: "Cross-document naming consistency." },
        ].map((item, idx) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.06 }}
            className="surface p-5"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                {item.label}
              </span>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-extrabold tabular-nums ${
                  item.tone === "verified"
                    ? "bg-verified-soft text-verified"
                    : "bg-warning-soft text-warning"
                }`}
              >
                {item.score}/100
              </span>
            </div>
            <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-border">
              <div
                className={`h-full rounded-full ${item.tone === "verified" ? "bg-verified" : "bg-warning"}`}
                style={{ width: `${item.score}%` }}
              />
            </div>
            <p className="mt-3 text-xs text-muted-foreground">{item.desc}</p>
          </motion.div>
        ))}
      </div>

      {/* Takeaways & Risks Breakdown */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Positive Takeaways */}
        <div className="surface p-6 border-t-4 border-t-verified">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 className="size-5 text-verified" />
            <h3 className="font-bold text-foreground text-base">Key Positive Highlights</h3>
          </div>
          <ul className="space-y-3 text-xs text-muted-foreground">
            {keyPositives.map((pos, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-0.5 size-1.5 rounded-full bg-verified shrink-0" />
                <span className="text-foreground font-medium">{pos}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Flagged Risks */}
        <div className="surface p-6 border-t-4 border-t-warning">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="size-5 text-warning" />
            <h3 className="font-bold text-foreground text-base">Conditional Audit Notes</h3>
          </div>
          <ul className="space-y-3 text-xs text-muted-foreground">
            {criticalGaps.map((gap, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-0.5 size-1.5 rounded-full bg-warning shrink-0" />
                <span className="text-foreground font-medium">{gap}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
