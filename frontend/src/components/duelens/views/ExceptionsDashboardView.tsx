"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { AlertTriangle, AlertOctagon, HelpCircle, ArrowRight, CheckCircle, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDuelensData } from "@/context/DuelensDataContext";
import { toast } from "sonner";

export function ExceptionsDashboardView({
  onSelectIssue,
}: {
  onSelectIssue?: (issueId: string) => void;
}) {
  const { issues } = useDuelensData();
  const [activeFilter, setActiveFilter] = useState<string>("All");
  const [resolvedIds, setResolvedIds] = useState<string[]>([]);

  // Map backend severities (CRITICAL/WARNING/NOTICE) to UI severities (High/Medium/Low)
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
            All flagged inconsistencies, financial discrepancies, and structural anomalies verified across submitted documents.
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
                {filter === "All" ? `All (${issues.length})` : `${filter} Severity`}
              </button>
            );
          })}
        </div>
      </div>

      {/* Discrepancy Cards Grid */}
      {filtered.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((item, idx) => {
            const isResolved = resolvedIds.includes(item.id) || item.resolved;
            const uiSeverity = mapSeverity(item.severity);

            // Build comparison pairs from source values
            const pairs = Object.entries(item.source_values || {}).map(([doc, val]) => ({
              label: (doc || "").replace(".json", "").replace(/_/g, " "),
              value: String(val),
            }));

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08 }}
                className={`surface flex flex-col justify-between p-6 transition-all ${
                  isResolved ? "opacity-60 border-emerald-500/30 bg-emerald-500/5" : ""
                }`}
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
                        <p className="text-xs font-bold text-muted-foreground">{item.id}</p>
                        <h3 className="font-semibold text-foreground text-sm leading-snug capitalize">
                          {(item.field_path || "").split(".").pop()?.replace(/_/g, " ")}
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
                        <div key={p.label} className="flex items-center gap-1.5 shrink-0">
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
                    onClick={() => onSelectIssue?.(item.id)}
                    className="text-xs font-bold text-primary hover:underline flex items-center gap-1"
                  >
                    View Details
                    <ArrowRight className="size-3" />
                  </button>

                  <Button
                    size="sm"
                    variant={isResolved ? "outline" : "secondary"}
                    onClick={() => markResolved(item.id)}
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
          <p className="text-sm font-semibold">No active mismatches found.</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            Your data-room documents are completely reconciled.
          </p>
        </div>
      )}
    </div>
  );
}
