"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { AlertTriangle, AlertOctagon, HelpCircle, ArrowRight, CheckCircle, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DISCREPANCIES } from "@/data/mock";
import { toast } from "sonner";

export function ExceptionsDashboardView({
  onSelectIssue,
}: {
  onSelectIssue?: (issueId: string) => void;
}) {
  const [activeFilter, setActiveFilter] = useState<string>("All");
  const [resolvedIds, setResolvedIds] = useState<string[]>([]);

  const filtered = DISCREPANCIES.filter((item) => {
    if (activeFilter === "All") return true;
    return item.severity === activeFilter;
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
            All flagged inconsistencies, financial deltas, and missing parameters across submitted pitch deck & MIS files.
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
                {filter === "All" ? "All Exceptions (5)" : `${filter} Severity`}
              </button>
            );
          })}
        </div>
      </div>

      {/* Discrepancy Cards Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filtered.map((item, idx) => {
          const isResolved = resolvedIds.includes(item.id);
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
                  <div className="flex items-center gap-2.5">
                    <span
                      className={`flex size-9 items-center justify-center rounded-xl ${
                        item.severity === "High"
                          ? "bg-critical-soft text-critical"
                          : item.severity === "Medium"
                            ? "bg-warning-soft text-warning"
                            : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {item.severity === "High" ? (
                        <AlertOctagon className="size-4" />
                      ) : item.severity === "Medium" ? (
                        <AlertTriangle className="size-4" />
                      ) : (
                        <HelpCircle className="size-4" />
                      )}
                    </span>
                    <div>
                      <p className="text-xs font-bold text-muted-foreground">{item.id}</p>
                      <h3 className="font-semibold text-foreground">{item.title}</h3>
                    </div>
                  </div>

                  <span
                    className={`rounded-full px-2.5 py-1 text-[11px] font-bold ${
                      item.severity === "High"
                        ? "bg-critical-soft text-critical"
                        : item.severity === "Medium"
                          ? "bg-warning-soft text-warning"
                          : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {item.severity}
                  </span>
                </div>

                <p className="mt-2 text-xs font-medium text-muted-foreground">{item.kind}</p>

                {/* Values comparison */}
                {item.pairs.length > 0 && (
                  <div className="mt-4 flex items-center gap-2">
                    {item.pairs.map((p, i) => (
                      <div key={p.label} className="flex flex-1 items-center gap-2">
                        <div className="flex-1 rounded-xl border border-border bg-muted/40 p-2.5">
                          <p className="text-[10px] text-muted-foreground">{p.label}</p>
                          <p className="text-sm font-bold text-foreground tabular-nums">{p.value}</p>
                        </div>
                        {i < item.pairs.length - 1 && (
                          <ArrowRight className="size-3.5 shrink-0 text-muted-foreground" />
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Note */}
                <p className="mt-4 text-xs text-muted-foreground leading-relaxed">{item.note}</p>
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
    </div>
  );
}
