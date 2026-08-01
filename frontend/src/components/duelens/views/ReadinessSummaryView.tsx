"use client";

import { motion } from "motion/react";
import { Award, CheckCircle2, AlertTriangle, ShieldCheck, Download, Gauge } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import jsPDF from "jspdf";

export function ReadinessSummaryView() {
  const downloadPDF = () => {
    try {
      const doc = new jsPDF();
      doc.setFont("helvetica", "bold");
      doc.setFontSize(18);
      doc.text("Duelens - Investor Readiness Memo", 20, 25);

      doc.setFontSize(11);
      doc.setFont("helvetica", "normal");
      doc.text("Company: TechNova Pvt Ltd", 20, 35);
      doc.text("Readiness Score: 88% (Investor Ready)", 20, 42);
      doc.text("Audit Status: Verified with 3 Conditional Notes", 20, 49);

      doc.line(20, 55, 190, 55);

      doc.setFont("helvetica", "bold");
      doc.text("Executive Summary:", 20, 65);
      doc.setFont("helvetica", "normal");
      doc.text(
        "Financial data across historical statements and MIS shows strong 92% integrity.\n" +
          "Minor variances in customer count (+8 in MIS) and growth rate rounding in pitch deck\n" +
          "have been reconciled. Projections assume 140% growth which requires monitoring.",
        20,
        73
      );

      doc.setFont("helvetica", "bold");
      doc.text("Metric Breakdown:", 20, 95);
      doc.setFont("helvetica", "normal");
      doc.text("1. Financial Statement Integrity: 92/100", 25, 105);
      doc.text("2. Cap Table & Ownership Health: 85/100", 25, 112);
      doc.text("3. Projections Realism & Burn: 80/100", 25, 119);

      doc.save("TechNova_Investor_Readiness_Memo.pdf");
      toast.success("Downloaded Investor Readiness Memo (PDF).");
    } catch {
      toast.error("Failed to generate PDF report.");
    }
  };

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

        <Button onClick={downloadPDF} className="rounded-xl shadow-[var(--shadow-glow)]">
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
            <h3 className="text-xl font-bold text-foreground">TechNova Pvt Ltd</h3>
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
            <h3 className="text-3xl font-extrabold text-primary tabular-nums">88%</h3>
            <p className="text-xs font-semibold text-verified">Investor Ready (Conditional)</p>
          </div>
        </div>

        <div className="flex items-center gap-4 sm:justify-end border-t border-border pt-4 sm:border-t-0 sm:pt-0">
          <div className="text-right">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Audited Documents
            </p>
            <p className="text-lg font-bold text-foreground">5 of 5 Verified</p>
            <span className="text-xs text-muted-foreground">2 Mismatches Resolved</span>
          </div>
        </div>
      </motion.div>

      {/* 4 Dimension Gauge Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Financial Integrity", score: 92, tone: "verified", desc: "High reconciliation across MIS & Bank statements." },
          { label: "Cap Table Health", score: 85, tone: "verified", desc: "ESOP pool variance verified." },
          { label: "Projections Realism", score: 80, tone: "warning", desc: "Requires ARR growth monitoring." },
          { label: "Compliance & Tax", score: 95, tone: "verified", desc: "No legal contingencies found." },
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
            <li className="flex items-start gap-2">
              <span className="mt-0.5 size-1.5 rounded-full bg-verified shrink-0" />
              <span>
                <strong className="text-foreground">Revenue Accuracy:</strong> Audited financial statements match Trial Balance ($12.38M) with 99% extraction confidence.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 size-1.5 rounded-full bg-verified shrink-0" />
              <span>
                <strong className="text-foreground">Cash Runway:</strong> Verified cash balance of $4.21M provides 18+ months runway at current burn rate.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 size-1.5 rounded-full bg-verified shrink-0" />
              <span>
                <strong className="text-foreground">Clean Cap Table:</strong> Founder equity is 44.82% post-ESOP option pool reservation.
              </span>
            </li>
          </ul>
        </div>

        {/* Flagged Risks */}
        <div className="surface p-6 border-t-4 border-t-warning">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="size-5 text-warning" />
            <h3 className="font-bold text-foreground text-base">Conditional Audit Notes</h3>
          </div>
          <ul className="space-y-3 text-xs text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="mt-0.5 size-1.5 rounded-full bg-warning shrink-0" />
              <span>
                <strong className="text-foreground">Pitch Deck Rounding:</strong> Growth rate presented as 115% vs 112.5% actual monthly MIS compound rate.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-0.5 size-1.5 rounded-full bg-warning shrink-0" />
              <span>
                <strong className="text-foreground">Customer Count Delta:</strong> Pitch deck snapshot (420) precedes late-month onboarded accounts (428).
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
