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
  ArrowRight,
  Filter,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { MATRIX_FULL_DATA } from "@/data/mock";
import { toast } from "sonner";

export function ComparisonMatrixView({
  onSelectIssue,
}: {
  onSelectIssue?: (issueId: string) => void;
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("High Severity");
  const [dismissAlert, setDismissAlert] = useState(false);

  const filteredData = MATRIX_FULL_DATA.filter((row) =>
    row.metric.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
            Side-by-side reconciliation across Trial Balance, Bank Statements, GL Extracts, Tax Docs, and Audit Checklists.
          </p>
        </div>

        <Button
          onClick={() => toast.success("Exporting Integrity Matrix CSV Report...")}
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
            <p className="text-lg font-bold text-foreground">12 Compared</p>
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
            <p className="text-lg font-bold text-foreground">3 Verified</p>
          </div>
        </div>

        <div className="surface flex items-center gap-3.5 p-4 border-l-4 border-l-warning">
          <div className="flex size-10 items-center justify-center rounded-xl bg-warning-soft text-warning">
            <Clock className="size-5" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-warning">
              Unresolved
            </p>
            <p className="text-lg font-bold text-foreground">2 Flagged</p>
          </div>
        </div>

        <div className="surface flex items-center gap-3.5 p-4">
          <div className="flex size-10 items-center justify-center rounded-xl bg-muted text-muted-foreground">
            <EyeOff className="size-5" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Missing Data
            </p>
            <p className="text-lg font-bold text-foreground">1 Data Point</p>
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
            <span className="size-2.5 rounded-full bg-warning" /> Unresolved
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
              <option>Confidence Score</option>
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
                <th className="px-4 py-4 text-center font-semibold">Trial Balance (v2.1)</th>
                <th className="px-4 py-4 text-center font-semibold">Bank Statement (Mar)</th>
                <th className="px-4 py-4 text-center font-semibold">GL Extract (Sales)</th>
                <th className="px-4 py-4 text-center font-semibold">Tax Provision Doc</th>
                <th className="px-4 py-4 text-center font-semibold">Audit Checklist</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredData.map((row) => (
                <tr key={row.metric} className="transition-colors hover:bg-muted/30">
                  <td className="px-6 py-4 font-semibold text-foreground">{row.metric}</td>

                  {/* Trial Balance */}
                  <td className="px-4 py-4 text-center">
                    <span className="inline-block rounded-lg bg-verified-soft px-3 py-1.5 font-mono text-xs font-semibold text-verified border border-verified/20">
                      {row.trialBalance}
                    </span>
                  </td>

                  {/* Bank Statement */}
                  <td className="px-4 py-4 text-center">
                    {row.highlight ? (
                      <button
                        onClick={() => onSelectIssue?.("INV-204")}
                        className="group inline-flex cursor-pointer items-center justify-center rounded-lg bg-critical-soft px-3 py-1.5 font-mono text-xs font-bold text-critical border-2 border-critical shadow-xs animate-pulse hover:scale-105 transition-transform"
                      >
                        {row.bankStatement}
                      </button>
                    ) : (
                      <span className="inline-block rounded-lg bg-verified-soft px-3 py-1.5 font-mono text-xs font-semibold text-verified border border-verified/20">
                        {row.bankStatement}
                      </span>
                    )}
                  </td>

                  {/* GL Extract */}
                  <td className="px-4 py-4 text-center">
                    {row.glExtract === "Missing" ? (
                      <span className="inline-block rounded-lg bg-muted px-3 py-1.5 font-mono text-xs font-medium text-muted-foreground italic border border-border">
                        Missing
                      </span>
                    ) : row.glExtract === "418" ? (
                      <span className="inline-block rounded-lg bg-critical-soft px-3 py-1.5 font-mono text-xs font-bold text-critical border border-critical/30">
                        {row.glExtract}
                      </span>
                    ) : (
                      <span className="inline-block rounded-lg bg-verified-soft px-3 py-1.5 font-mono text-xs font-semibold text-verified border border-verified/20">
                        {row.glExtract}
                      </span>
                    )}
                  </td>

                  {/* Tax Provision Doc */}
                  <td className="px-4 py-4 text-center">
                    {row.taxDoc === "$1,190,000.00" ? (
                      <span className="inline-block rounded-lg bg-critical-soft px-3 py-1.5 font-mono text-xs font-bold text-critical border border-critical/30">
                        {row.taxDoc}
                      </span>
                    ) : (
                      <span className="inline-block rounded-lg bg-verified-soft px-3 py-1.5 font-mono text-xs font-semibold text-verified border border-verified/20">
                        {row.taxDoc}
                      </span>
                    )}
                  </td>

                  {/* Audit Checklist */}
                  <td className="px-4 py-4 text-center">
                    <span className="inline-block rounded-lg bg-verified-soft px-3 py-1.5 font-mono text-xs font-semibold text-verified border border-verified/20">
                      {row.auditChecklist}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Floating Context Panel for Critical Mismatch */}
      {!dismissAlert && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed bottom-6 right-6 z-50 max-w-sm rounded-2xl border border-critical/30 bg-card p-5 shadow-2xl backdrop-blur-xl"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2">
              <AlertOctagon className="size-5 text-critical" />
              <h4 className="text-xs font-extrabold uppercase tracking-wider text-critical">
                Critical Mismatch Detected
              </h4>
            </div>
            <button
              onClick={() => setDismissAlert(true)}
              className="text-muted-foreground hover:text-foreground text-xs"
            >
              ✕
            </button>
          </div>
          <p className="mt-2.5 text-xs text-muted-foreground leading-relaxed">
            Revenue delta detected between Bank Statement ($4,248,500.00) and Trial Balance ($4,250,000.00). Transaction log indicates 3 missing entries from the GL.
          </p>
          <div className="mt-4 flex items-center justify-between gap-3">
            <Button
              size="sm"
              onClick={() => onSelectIssue?.("INV-204")}
              className="w-full rounded-xl bg-critical text-destructive-foreground hover:bg-critical/90 shadow-sm text-xs"
            >
              Inspect Issue #INV-204
              <ArrowRight className="ml-1.5 size-3.5" />
            </Button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
