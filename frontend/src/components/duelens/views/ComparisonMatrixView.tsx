"use client";

import { useState } from "react";
import { motion } from "motion/react";
import {
  Grid,
  Download,
  AlertOctagon,
  CheckCircle2,
  Clock,
  EyeOff,
  Search,
  Filter,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDuelensData } from "@/context/DuelensDataContext";
import { toast } from "sonner";

export function ComparisonMatrixView({
  onSelectIssue,
}: {
  onSelectIssue?: (issueId: string) => void;
}) {
  const { matrixData, issues } = useDuelensData();
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("High Severity");

  // Extract dynamically headers from values keys in matrixData rows
  const documentKeys = Array.from(
    new Set(
      matrixData?.fields?.flatMap((row) => Object.keys(row.values || {})) || []
    )
  );

  const filteredData = (matrixData?.fields || []).filter((row) =>
    row.field_path.toLowerCase().includes(searchTerm.toLowerCase()) ||
    row.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Sort logic
  if (sortBy === "High Severity") {
    filteredData.sort((a, b) => (a.is_consistent === b.is_consistent ? 0 : a.is_consistent ? 1 : -1));
  } else if (sortBy === "Alpha (A-Z)") {
    filteredData.sort((a, b) => a.field_path.localeCompare(b.field_path));
  }

  const mismatchCount = (matrixData?.fields || []).filter((f) => !f.is_consistent).length;
  const totalCompared = (matrixData?.fields || []).length;

  return (
    <div className="space-y-8 relative pb-20">
      {/* Top Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary">
            <Grid className="size-3.5" />
            Integrity Matrix Engine
          </span>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Cross-Document Comparison Matrix
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Side-by-side reconciliation and verification of metric values extracted across Trial Balance, Projections, and MIS reports.
          </p>
        </div>

        <Button
          onClick={() => toast.success("Exporting Integrity Matrix Report...")}
          className="rounded-xl shadow-[var(--shadow-glow)]"
        >
          <Download className="mr-2 size-4" />
          Export Matrix Report
        </Button>
      </div>

      {/* Summary Stat Chips */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="surface flex items-center gap-3.5 p-4">
          <div className="flex size-10 items-center justify-center rounded-xl bg-primary-soft text-primary">
            <CheckCircle2 className="size-5" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Total Metrics
            </p>
            <p className="text-lg font-bold text-foreground">{totalCompared} Compared</p>
          </div>
        </div>

        <div className="surface flex items-center gap-3.5 p-4 border-l-4 border-l-critical">
          <div className="flex size-10 items-center justify-center rounded-xl bg-critical-soft text-critical">
            <AlertOctagon className="size-5" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-critical">
              Mismatches
            </p>
            <p className="text-lg font-bold text-foreground">{mismatchCount} Verified</p>
          </div>
        </div>

        <div className="surface flex items-center gap-3.5 p-4 border-l-4 border-l-warning">
          <div className="flex size-10 items-center justify-center rounded-xl bg-warning-soft text-warning">
            <Clock className="size-5" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-warning">
              Unresolved Flags
            </p>
            <p className="text-lg font-bold text-foreground">{issues.length} Active</p>
          </div>
        </div>

        <div className="surface flex items-center gap-3.5 p-4">
          <div className="flex size-10 items-center justify-center rounded-xl bg-muted text-muted-foreground">
            <EyeOff className="size-5" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Coverage
            </p>
            <p className="text-lg font-bold text-foreground">
              {documentKeys.length} Doc Types
            </p>
          </div>
        </div>
      </div>

      {/* Controls & Search */}
      <div className="surface flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
            <span className="size-2.5 rounded-full bg-verified" /> Consistent
          </div>
          <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
            <span className="size-2.5 rounded-full bg-critical" /> Mismatch
          </div>
          <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
            <span className="size-2.5 rounded-full bg-muted-foreground/40" /> Missing
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search metric..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="h-9 w-48 rounded-xl border border-border bg-background pl-9 pr-3 text-xs focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>

          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Filter className="size-3.5" />
            <span>Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="h-9 rounded-xl border border-border bg-background px-2.5 text-xs font-medium focus:outline-none"
            >
              <option>High Severity</option>
              <option>Alpha (A-Z)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Matrix Table */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="surface overflow-hidden"
      >
        <div className="overflow-x-auto">
          <table className="w-full min-w-[960px] text-left text-sm">
            <thead className="bg-muted/70 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-6 py-4 font-semibold">Metric / Data Point</th>
                {documentKeys.map((docKey) => (
                  <th key={docKey} className="px-4 py-4 text-center font-semibold capitalize">
                    {(docKey || "").replace(".json", "").replace(/_/g, " ")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredData.map((row) => (
                <tr key={row.field_path} className="transition-colors hover:bg-muted/30">
                  <td className="px-6 py-4">
                    <p className="font-semibold text-foreground capitalize">
                      {(row.field_path || "").split(".").pop()?.replace(/_/g, " ")}
                    </p>
                    <p className="text-[10px] text-muted-foreground font-mono">{row.field_path}</p>
                  </td>

                  {documentKeys.map((docKey) => {
                    const cell = row.values[docKey];
                    if (!cell) {
                      return (
                        <td key={docKey} className="px-4 py-4 text-center">
                          <span className="inline-block rounded-lg bg-muted px-3 py-1.5 font-mono text-xs font-medium text-muted-foreground italic border border-border">
                            —
                          </span>
                        </td>
                      );
                    }

                    const isMismatch = !row.is_consistent;
                    
                    return (
                      <td key={docKey} className="px-4 py-4 text-center">
                        {isMismatch ? (
                          <button
                            onClick={() => {
                              // Match this field path to a flagged issue
                              const matchingIssue = issues.find(
                                (issue) => issue.field_path === row.field_path
                              );
                              if (matchingIssue && onSelectIssue) {
                                onSelectIssue(matchingIssue.id);
                              } else {
                                toast.info("Check Exceptions Dashboard for details on this mismatch.");
                              }
                            }}
                            className="group inline-flex cursor-pointer items-center justify-center rounded-lg bg-critical-soft px-3 py-1.5 font-mono text-xs font-bold text-critical border-2 border-critical shadow-xs animate-pulse hover:scale-105 transition-transform"
                          >
                            {String(cell.value)}
                          </button>
                        ) : (
                          <span className="inline-block rounded-lg bg-verified-soft px-3 py-1.5 font-mono text-xs font-semibold text-verified border border-verified/20">
                            {String(cell.value)}
                          </span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
