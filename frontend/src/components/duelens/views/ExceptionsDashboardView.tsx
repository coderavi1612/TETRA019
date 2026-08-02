"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  AlertTriangle,
  AlertOctagon,
  HelpCircle,
  ArrowRight,
  CheckCircle,
  ShieldAlert,
  FileText,
  CheckCircle2,
  MessageSquare,
  Bot,
  GitCommit,
  FileCode,
  Check,
  RefreshCw,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDuelensData } from "@/context/DuelensDataContext";
import { toast } from "sonner";

export function ExceptionsDashboardView() {
  const { issues } = useDuelensData();
  const [activeFilter, setActiveFilter] = useState<string>("All");
  const [resolvedIds, setResolvedIds] = useState<string[]>([]);
  const [expandedIssueId, setExpandedIssueId] = useState<string | null>(null);

  const mapSeverity = (sev: string): "High" | "Medium" | "Low" => {
    if (sev === "CRITICAL") return "High";
    if (sev === "WARNING") return "Medium";
    return "Low";
  };

  const filtered = issues.filter((issue) => {
    const uiSev = mapSeverity(issue.severity);
    if (activeFilter === "All") return true;
    return uiSev === activeFilter;
  });

  const markResolved = (id: string) => {
    setResolvedIds((prev) => [...prev, id]);
    toast.success(`Exception ${id} marked as resolved.`);
  };

  const expandedIssue = expandedIssueId
    ? issues.find((i) => i.id === expandedIssueId)
    : null;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-critical-soft px-3 py-1 text-xs font-semibold text-critical">
            <ShieldAlert className="size-3.5" />
            Exceptions & Mismatch Tracker
          </span>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Exceptions Dashboard
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            All flagged inconsistencies, financial discrepancies, and structural
            anomalies verified across submitted documents.
          </p>
        </div>

        {/* Severity Filters */}
        <div className="flex flex-wrap items-center gap-1.5 rounded-2xl border border-border bg-muted/50 p-1.5">
          {["All", "High", "Medium", "Low"].map((filter) => {
            const active = activeFilter === filter;
            return (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition-all ${
                  active
                    ? "bg-primary text-primary-foreground shadow-xs"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {filter === "All"
                  ? `All (${issues.length})`
                  : `${filter} Severity`}
              </button>
            );
          })}
        </div>
      </div>

      {/* ───────── Inline Issue Detail Panel ───────── */}
      <AnimatePresence mode="wait">
        {expandedIssue && (
          <motion.div
            key={`detail-${expandedIssue.id}`}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <IssueDetailInline
              issue={expandedIssue}
              allIssues={issues}
              isResolved={
                resolvedIds.includes(expandedIssue.id) ||
                expandedIssue.resolved
              }
              onResolve={() => markResolved(expandedIssue.id)}
              onClose={() => setExpandedIssueId(null)}
              onSelectIssue={(id) => setExpandedIssueId(id)}
              mapSeverity={mapSeverity}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* ───────── Discrepancy Cards Grid ───────── */}
      {filtered.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((item, idx) => {
            const isResolved = resolvedIds.includes(item.id) || item.resolved;
            const uiSeverity = mapSeverity(item.severity);
            const isExpanded = expandedIssueId === item.id;

            const pairs = Object.entries(item.source_values || {}).map(
              ([doc, val]) => ({
                label: (doc || "")
                  .replace(".json", "")
                  .replace(/_/g, " "),
                value: String(val),
              })
            );

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08 }}
                className={`surface flex flex-col justify-between p-6 transition-all cursor-pointer ${
                  isResolved
                    ? "opacity-60 border-emerald-500/30 bg-emerald-500/5"
                    : ""
                } ${
                  isExpanded
                    ? "ring-2 ring-primary/60 border-primary/40"
                    : "hover:border-primary/20"
                }`}
                onClick={() =>
                  setExpandedIssueId(isExpanded ? null : item.id)
                }
              >
                <div>
                  {/* Header */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-2.5">
                      <span
                        className={`flex size-9 items-center justify-center rounded-xl shrink-0 ${
                          uiSeverity === "High"
                            ? "bg-critical-soft text-critical"
                            : uiSeverity === "Medium"
                              ? "bg-warning-soft text-warning"
                              : "bg-muted text-muted-foreground"
                        }`}
                      >
                        {uiSeverity === "High" ? (
                          <AlertOctagon className="size-4" />
                        ) : uiSeverity === "Medium" ? (
                          <AlertTriangle className="size-4" />
                        ) : (
                          <HelpCircle className="size-4" />
                        )}
                      </span>
                      <div>
                        <p className="text-xs font-bold text-muted-foreground">
                          {item.id}
                        </p>
                        <h3 className="font-semibold text-foreground text-sm leading-snug capitalize">
                          {(item.field_path || "")
                            .split(".")
                            .pop()
                            ?.replace(/_/g, " ")}
                        </h3>
                      </div>
                    </div>

                    <span
                      className={`rounded-full px-2.5 py-1 text-[11px] font-bold ${
                        uiSeverity === "High"
                          ? "bg-critical-soft text-critical"
                          : uiSeverity === "Medium"
                            ? "bg-warning-soft text-warning"
                            : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {uiSeverity}
                    </span>
                  </div>

                  <p className="mt-2 text-xs font-medium text-muted-foreground font-mono truncate">
                    {item.field_path}
                  </p>

                  {/* Values comparison */}
                  {pairs.length > 0 && (
                    <div className="mt-4 flex items-center gap-2 overflow-x-auto pb-1">
                      {pairs.map((p, i) => (
                        <div
                          key={p.label}
                          className="flex items-center gap-1.5 shrink-0"
                        >
                          <div className="rounded-xl border border-border bg-muted/40 p-2.5">
                            <p className="text-[9px] font-semibold text-muted-foreground uppercase leading-none mb-1">
                              {p.label}
                            </p>
                            <p className="text-xs font-bold text-foreground tabular-nums">
                              {p.value}
                            </p>
                          </div>
                          {i < pairs.length - 1 && (
                            <ArrowRight className="size-3 text-muted-foreground" />
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Note */}
                  <p className="mt-4 text-xs text-muted-foreground leading-relaxed">
                    {item.description}
                  </p>
                </div>

                {/* Actions */}
                <div className="mt-6 pt-4 border-t border-border flex items-center justify-between gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setExpandedIssueId(isExpanded ? null : item.id);
                    }}
                    className="text-xs font-bold text-primary hover:underline flex items-center gap-1"
                  >
                    {isExpanded ? "Hide Details" : "View Details"}
                    <ArrowRight
                      className={`size-3 transition-transform ${isExpanded ? "rotate-90" : ""}`}
                    />
                  </button>

                  <Button
                    size="sm"
                    variant={isResolved ? "outline" : "secondary"}
                    onClick={(e) => {
                      e.stopPropagation();
                      markResolved(item.id);
                    }}
                    disabled={isResolved}
                    className="rounded-lg text-xs"
                  >
                    <CheckCircle className="mr-1 size-3.5" />
                    {isResolved ? "Resolved" : "Mark Resolved"}
                  </Button>
                </div>
              </motion.div>
            );
          })}
        </div>
      ) : (
        <div className="surface flex flex-col items-center justify-center py-24 text-center text-muted-foreground">
          <ShieldAlert className="size-10 text-muted-foreground/35 mb-2.5 animate-pulse" />
          <p className="text-sm font-semibold">
            No active mismatches found.
          </p>
          <p className="text-xs text-muted-foreground mt-0.5">
            Your data-room documents are completely reconciled.
          </p>
        </div>
      )}
    </div>
  );
}

/* ────────────────────────────────────────────────────────
   Inline Issue Detail Panel (was a separate view/tab)
   ──────────────────────────────────────────────────────── */
function IssueDetailInline({
  issue,
  allIssues,
  isResolved: initialResolved,
  onResolve,
  onClose,
  onSelectIssue,
  mapSeverity,
}: {
  issue: any;
  allIssues: any[];
  isResolved: boolean;
  onResolve: () => void;
  onClose: () => void;
  onSelectIssue: (id: string) => void;
  mapSeverity: (sev: string) => "High" | "Medium" | "Low";
}) {
  const uiSeverity = mapSeverity(issue.severity);
  const resolvedState = initialResolved;

  const docExcerpts = Object.entries(issue.source_values || {}).map(
    ([filename, val], idx) => ({
      name: (filename || "").replace(".json", "").replace(/_/g, " "),
      value: String(val),
      idx,
    })
  );

  return (
    <div className="surface border-l-4 border-l-primary space-y-6 p-6 mb-2">
      {/* Top Bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-muted-foreground">
                {issue.id}
              </span>
              <span
                className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                  resolvedState
                    ? "bg-verified-soft text-verified"
                    : "bg-critical-soft text-critical"
                }`}
              >
                {resolvedState ? "Resolved" : "Open"}
              </span>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-foreground capitalize">
              {(issue.field_path || "").split(".").pop()?.replace(/_/g, " ")}{" "}
              Mismatch
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Issue selector */}
          {allIssues.length > 1 && (
            <select
              value={issue.id}
              onChange={(e) => onSelectIssue(e.target.value)}
              className="h-9 rounded-xl border border-border bg-card px-3 text-xs font-semibold focus:outline-none"
            >
              {allIssues.map((i: any) => (
                <option key={i.id} value={i.id}>
                  {i.id}:{" "}
                  {(i.field_path || "")
                    .split(".")
                    .pop()
                    ?.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="rounded-xl"
          >
            <X className="size-4" />
          </Button>
        </div>
      </div>

      {/* Side-by-side Document Excerpt Comparison */}
      <div className="grid gap-4 md:grid-cols-2">
        {docExcerpts.map((doc) => (
          <motion.div
            key={doc.name}
            initial={{ opacity: 0, x: doc.idx % 2 === 0 ? -12 : 12 }}
            animate={{ opacity: 1, x: 0 }}
            className="rounded-2xl border border-border bg-card p-5"
          >
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                {doc.idx % 2 === 0 ? (
                  <FileText className="size-4 text-primary" />
                ) : (
                  <FileCode className="size-4 text-primary" />
                )}
                <span className="font-semibold text-foreground text-sm capitalize">
                  {doc.name}
                </span>
              </div>
              <span className="rounded bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground uppercase">
                Source Document
              </span>
            </div>
            <div className="mt-3 rounded-xl border border-border bg-muted/40 p-4 font-mono text-xs text-foreground leading-relaxed">
              Extracted Value:{" "}
              <span className="font-bold text-primary">{doc.value}</span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* AI Analysis & Actions Row */}
      <div className="grid gap-4 md:grid-cols-3">
        {/* AI Analysis */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:col-span-2 rounded-2xl border border-border bg-card p-5"
        >
          <div className="flex items-start gap-4">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-2xl bg-primary-soft text-primary">
              <Bot className="size-5" />
            </span>
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-3">
                <h3 className="font-bold text-foreground text-sm">
                  AI Cause Analysis
                </h3>
                <span className="rounded-full bg-warning-soft px-2.5 py-0.5 text-xs font-bold text-warning capitalize">
                  {issue.classification}
                </span>
                <span className="rounded-full bg-critical-soft px-2.5 py-0.5 text-xs font-bold text-critical">
                  Severity: {uiSeverity}
                </span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {issue.description}
              </p>
            </div>
          </div>

          {/* Mini audit trail */}
          <div className="mt-5 pt-4 border-t border-border space-y-3">
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
              Audit Trail
            </h4>
            {[
              { title: "Auto-Extraction Completed", status: "done" },
              { title: "Cross-Document Delta Flagged", status: "done" },
              { title: "AI Root Cause Diagnosis Generated", status: "done" },
              { title: "Auditor Verification Pending", status: "current" },
            ].map((step, idx) => (
              <div key={idx} className="flex items-center gap-2.5">
                <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary-soft text-primary">
                  {step.status === "done" ? (
                    <CheckCircle2 className="size-3.5" />
                  ) : (
                    <GitCommit className="size-3.5" />
                  )}
                </span>
                <p className="text-xs font-medium text-foreground">
                  {step.title}
                </p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Resolution Actions */}
        <div className="rounded-2xl border border-border bg-card p-5 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-foreground text-sm">
              Resolution Actions
            </h3>
            <p className="mt-1 text-xs text-muted-foreground">
              Reconcile differences across documents.
            </p>
          </div>

          <div className="mt-5 space-y-2.5">
            <Button
              onClick={onResolve}
              disabled={resolvedState}
              className="w-full rounded-xl shadow-[var(--shadow-glow)]"
            >
              <Check className="mr-2 size-4" />
              {resolvedState ? "Issue Resolved" : "Accept Reconciled Value"}
            </Button>

            <Button
              variant="outline"
              onClick={() =>
                toast.info("Clarification request sent to founders.")
              }
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
