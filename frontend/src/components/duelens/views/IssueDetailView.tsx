"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { FileText, CheckCircle2, MessageSquare, ArrowLeft, Bot, GitCommit, FileCode, Check, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export function IssueDetailView({
  issueId = "INV-204",
  onBack,
}: {
  issueId?: string;
  onBack?: () => void;
}) {
  const [selectedIssue, setSelectedIssue] = useState(issueId);
  const [status, setStatus] = useState<"Open" | "Resolved">("Open");

  const issueData = {
    "INV-204": {
      title: "Customer Count Mismatch",
      category: "Operational / Traction Metric",
      severity: "High",
      docA: { name: "PitchDeck.pdf", page: "Slide 6", snippet: "Over 420+ Paying Enterprise Customers across North America and EU." },
      docB: { name: "MonthlyMIS.xlsx", page: "Sheet 'Traction' (Row 42)", snippet: "Active Subscriptions Count: 428 accounts as of March 31, 2026." },
      delta: "+8 accounts (1.9% difference)",
      aiAnalysis:
        "The Pitch Deck was created on March 15th and rounded down the customer count (420+). The MIS was generated at month-end on March 31st and includes 8 new enterprise sign-ups closed during the final two weeks of the quarter.",
      timeline: [
        { title: "Auto-Extraction Completed", date: "Today 10:14 AM", status: "done" },
        { title: "Cross-Document Reconciliation Flagged Delta", date: "Today 10:15 AM", status: "done" },
        { title: "AI Root Cause Diagnosis Generated", date: "Today 10:15 AM", status: "done" },
        { title: "Auditor Verification Pending", date: "Pending Action", status: "current" },
      ],
    },
    "INV-206": {
      title: "Growth Rate Discrepancy",
      category: "Financial Performance Metric",
      severity: "High",
      docA: { name: "PitchDeck.pdf", page: "Slide 12", snippet: "YoY Growth: 115% ARR Expansion rate." },
      docB: { name: "FinancialProjections.xlsx", page: "Sheet 'Summary' (Row 12)", snippet: "Compound YoY Revenue Growth: 112.5%." },
      delta: "2.5% Growth Variance",
      aiAnalysis:
        "Pitch Deck presents an annualized Q4 run-rate expansion, whereas the Financial Projections model applies compound monthly growth actuals across 12 months.",
      timeline: [
        { title: "Auto-Extraction Completed", date: "Today 10:14 AM", status: "done" },
        { title: "Discrepancy Flagged", date: "Today 10:15 AM", status: "done" },
        { title: "Auditor Verification Pending", date: "Pending Action", status: "current" },
      ],
    },
  }[selectedIssue] ?? {
    title: "Customer Count Mismatch",
    category: "Operational / Traction Metric",
    severity: "High",
    docA: { name: "PitchDeck.pdf", page: "Slide 6", snippet: "Over 420+ Paying Enterprise Customers across North America and EU." },
    docB: { name: "MonthlyMIS.xlsx", page: "Sheet 'Traction' (Row 42)", snippet: "Active Subscriptions Count: 428 accounts as of March 31, 2026." },
    delta: "+8 accounts (1.9% difference)",
    aiAnalysis: "Pitch Deck rounds customer count down.",
    timeline: [],
  };

  const handleResolve = () => {
    setStatus("Resolved");
    toast.success(`Issue ${selectedIssue} successfully resolved.`);
  };

  return (
    <div className="space-y-8">
      {/* Top Bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          {onBack && (
            <Button variant="outline" size="icon" onClick={onBack} className="rounded-xl">
              <ArrowLeft className="size-4" />
            </Button>
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-muted-foreground">{selectedIssue}</span>
              <span
                className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                  status === "Resolved"
                    ? "bg-verified-soft text-verified"
                    : "bg-critical-soft text-critical"
                }`}
              >
                {status}
              </span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-foreground md:text-3xl">
              {issueData.title}
            </h2>
          </div>
        </div>

        {/* Issue selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-muted-foreground">Select Issue:</span>
          <select
            value={selectedIssue}
            onChange={(e) => setSelectedIssue(e.target.value)}
            className="h-9 rounded-xl border border-border bg-card px-3 text-xs font-semibold focus:outline-none"
          >
            <option value="INV-204">INV-204: Customer Count Mismatch</option>
            <option value="INV-206">INV-206: Growth Rate Discrepancy</option>
          </select>
        </div>
      </div>

      {/* Side-by-side Document Excerpt Comparison */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Doc A */}
        <motion.div initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} className="surface p-6">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div className="flex items-center gap-2">
              <FileText className="size-4 text-primary" />
              <span className="font-semibold text-foreground text-sm">{issueData.docA.name}</span>
            </div>
            <span className="rounded bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
              {issueData.docA.page}
            </span>
          </div>
          <div className="mt-4 rounded-xl border border-border bg-muted/40 p-4 font-mono text-xs text-foreground leading-relaxed">
            &quot;{issueData.docA.snippet}&quot;
          </div>
        </motion.div>

        {/* Doc B */}
        <motion.div initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} className="surface p-6">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div className="flex items-center gap-2">
              <FileCode className="size-4 text-primary" />
              <span className="font-semibold text-foreground text-sm">{issueData.docB.name}</span>
            </div>
            <span className="rounded bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
              {issueData.docB.page}
            </span>
          </div>
          <div className="mt-4 rounded-xl border border-border bg-muted/40 p-4 font-mono text-xs text-foreground leading-relaxed">
            &quot;{issueData.docB.snippet}&quot;
          </div>
        </motion.div>
      </div>

      {/* AI Analysis & Variance Card */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="surface p-6 border-l-4 border-l-primary">
        <div className="flex items-start gap-4">
          <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-primary-soft text-primary">
            <Bot className="size-6" />
          </span>
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <h3 className="font-bold text-foreground">AI Cause Analysis</h3>
              <span className="rounded-full bg-warning-soft px-2.5 py-0.5 text-xs font-bold text-warning">
                Variance: {issueData.delta}
              </span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">{issueData.aiAnalysis}</p>
          </div>
        </div>
      </motion.div>

      {/* Audit Trail Timeline & Actions */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Timeline */}
        <div className="surface md:col-span-2 p-6">
          <h3 className="font-bold text-foreground text-sm mb-4">Audit Trail & Investigation History</h3>
          <div className="space-y-4">
            {issueData.timeline.map((item, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary-soft text-primary">
                  {item.status === "done" ? <CheckCircle2 className="size-4" /> : <GitCommit className="size-4" />}
                </span>
                <div>
                  <p className="text-xs font-semibold text-foreground">{item.title}</p>
                  <p className="text-[11px] text-muted-foreground">{item.date}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Resolution Actions */}
        <div className="surface p-6 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-foreground text-sm">Resolution Actions</h3>
            <p className="mt-1 text-xs text-muted-foreground">Select an action to update financial model and reconcile values.</p>
          </div>

          <div className="mt-6 space-y-2.5">
            <Button onClick={handleResolve} disabled={status === "Resolved"} className="w-full rounded-xl shadow-[var(--shadow-glow)]">
              <Check className="mr-2 size-4" />
              {status === "Resolved" ? "Issue Resolved" : "Accept MIS Value (428)"}
            </Button>

            <Button variant="outline" onClick={() => toast.info("Clarification request sent to founders.")} className="w-full rounded-xl">
              <MessageSquare className="mr-2 size-4" />
              Request Founder Note
            </Button>

            <Button variant="ghost" onClick={() => toast.info("Refreshed extraction logs.")} className="w-full rounded-xl text-xs text-muted-foreground">
              <RefreshCw className="mr-1.5 size-3.5" />
              Re-run Extraction
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
