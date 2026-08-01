"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { FileText, CheckCircle2, MessageSquare, ArrowLeft, Bot, GitCommit, FileCode, Check, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDuelensData } from "@/context/DuelensDataContext";
import { toast } from "sonner";

export function IssueDetailView({
  issueId,
  onBack,
}: {
  issueId: string;
  onBack?: () => void;
}) {
  const { issues } = useDuelensData();
  const [selectedIssueId, setSelectedIssueId] = useState(issueId);
  const [status, setStatus] = useState<"Open" | "Resolved">("Open");

  const issue = issues.find((i) => i.id === selectedIssueId) || issues[0];

  const handleResolve = () => {
    setStatus("Resolved");
    toast.success(`Issue ${selectedIssueId} successfully resolved.`);
  };

  if (!issue) {
    return (
      <div className="surface p-12 text-center text-muted-foreground flex flex-col items-center">
        <Bot className="size-10 text-muted-foreground/35 mb-2.5 animate-bounce" />
        <p className="text-sm font-semibold">No issues currently flagged for this data-room.</p>
        {onBack && (
          <Button onClick={onBack} variant="outline" size="sm" className="mt-4 rounded-xl">
            <ArrowLeft className="mr-1.5 size-4" /> Go Back
          </Button>
        )}
      </div>
    );
  }

  // Map backend severity to UI labels
  const uiSeverity = issue.severity === "CRITICAL" ? "High" : issue.severity === "WARNING" ? "Medium" : "Low";

  // Build documents list
  const docExcerpts = Object.entries(issue.source_values || {}).map(([filename, val], idx) => ({
    name: (filename || "").replace(".json", "").replace(/_/g, " "),
    value: String(val),
    idx,
  }));

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
              <span className="font-mono text-xs font-bold text-muted-foreground">{issue.id}</span>
              <span
                className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                  status === "Resolved" || issue.resolved
                    ? "bg-verified-soft text-verified"
                    : "bg-critical-soft text-critical"
                }`}
              >
                {status === "Resolved" || issue.resolved ? "Resolved" : "Open"}
              </span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-foreground md:text-3xl capitalize">
              {(issue.field_path || "").split(".").pop()?.replace(/_/g, " ")} Mismatch
            </h2>
          </div>
        </div>

        {/* Issue selector */}
        {issues.length > 1 && (
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-muted-foreground">Select Issue:</span>
            <select
              value={selectedIssueId}
              onChange={(e) => setSelectedIssueId(e.target.value)}
              className="h-9 rounded-xl border border-border bg-card px-3 text-xs font-semibold focus:outline-none"
            >
              {issues.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.id}: {(i.field_path || "").split(".").pop()?.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Side-by-side Document Excerpt Comparison */}
      <div className="grid gap-6 md:grid-cols-2">
        {docExcerpts.map((doc) => (
          <motion.div
            key={doc.name}
            initial={{ opacity: 0, x: doc.idx % 2 === 0 ? -16 : 16 }}
            animate={{ opacity: 1, x: 0 }}
            className="surface p-6"
          >
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                {doc.idx % 2 === 0 ? (
                  <FileText className="size-4 text-primary" />
                ) : (
                  <FileCode className="size-4 text-primary" />
                )}
                <span className="font-semibold text-foreground text-sm capitalize">{doc.name}</span>
              </div>
              <span className="rounded bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground uppercase">
                Source Document
              </span>
            </div>
            <div className="mt-4 rounded-xl border border-border bg-muted/40 p-4 font-mono text-xs text-foreground leading-relaxed">
              Extracted Value: <span className="font-bold text-primary">{doc.value}</span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* AI Analysis & Variance Card */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="surface p-6 border-l-4 border-l-primary"
      >
        <div className="flex items-start gap-4">
          <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-primary-soft text-primary">
            <Bot className="size-6" />
          </span>
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-3">
              <h3 className="font-bold text-foreground">AI Cause Analysis</h3>
              <span className="rounded-full bg-warning-soft px-2.5 py-0.5 text-xs font-bold text-warning capitalize">
                Classification: {issue.classification}
              </span>
              <span className="rounded-full bg-critical-soft px-2.5 py-0.5 text-xs font-bold text-critical">
                Severity: {uiSeverity}
              </span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">{issue.description}</p>
          </div>
        </div>
      </motion.div>

      {/* Audit Trail Timeline & Actions */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Timeline */}
        <div className="surface md:col-span-2 p-6">
          <h3 className="font-bold text-foreground text-sm mb-4">Audit Trail & Investigation History</h3>
          <div className="space-y-4">
            {[
              { title: "Auto-Extraction Completed", date: "System Process Logged", status: "done" },
              { title: "Cross-Document Reconciliation Delta Flagged", date: "System Process Logged", status: "done" },
              { title: "AI Root Cause Diagnosis Generated", date: "System Process Logged", status: "done" },
              { title: "Auditor Verification Pending", date: "User Action Required", status: "current" },
            ].map((item, idx) => (
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
            <p className="mt-1 text-xs text-muted-foreground">reconcile differences across documents.</p>
          </div>

          <div className="mt-6 space-y-2.5">
            <Button
              onClick={handleResolve}
              disabled={status === "Resolved" || issue.resolved}
              className="w-full rounded-xl shadow-[var(--shadow-glow)]"
            >
              <Check className="mr-2 size-4" />
              {status === "Resolved" || issue.resolved ? "Issue Resolved" : "Accept Reconciled Value"}
            </Button>

            <Button
              variant="outline"
              onClick={() => toast.info("Clarification request sent to founders.")}
              className="w-full rounded-xl"
            >
              <MessageSquare className="mr-2 size-4" />
              Request Founder Note
            </Button>

            <Button
              variant="ghost"
              onClick={() => toast.info("Refreshed extraction logs.")}
              className="w-full rounded-xl text-xs text-muted-foreground"
            >
              <RefreshCw className="mr-1.5 size-3.5" />
              Re-run Extraction
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
