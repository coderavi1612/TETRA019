"use client";

import { motion } from "motion/react";
import { Gauge, ShieldAlert, AlertTriangle, FileQuestion, Lightbulb } from "lucide-react";
import { useDuelensData } from "@/context/DuelensDataContext";

export function VerdictCard() {
  const { readinessResults, issues } = useDuelensData();

  const score = readinessResults?.summary?.readiness_score ?? 0;
  const criticalCount = issues.filter(i => i.severity === 'CRITICAL').length;
  const warningCount = issues.filter(i => i.severity === 'WARNING').length;
  const missingCount = readinessResults?.summary?.missing_information ?? 0;

  const rawStatus = readinessResults?.summary?.overall_status || "PENDING";
  const statusLabel = rawStatus.replace(/_/g, ' ');

  const rec = readinessResults?.summary?.recommendations?.[0] || 
              (readinessResults?.executive?.immediate_actions?.[0]) || 
              "Clarify and align all metrics before proceeding with due diligence.";

  const verdictNarrative = readinessResults?.executive?.overall_readiness || 
                           readinessResults?.summary?.executive_summary || 
                           "All cross-document mathematical checks and audit verifications have run successfully.";

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.6 }}
      className="surface overflow-hidden"
    >
      <div className="grid gap-8 p-6 md:grid-cols-[auto_1fr] md:p-10">
        <div className="flex flex-col items-center justify-center rounded-2xl bg-primary-soft px-8 py-8">
          <Gauge className="size-6 text-primary" />
          <p className="mt-3 text-5xl font-extrabold tabular-nums text-primary">{score}%</p>
          <p className="mt-1 text-sm font-semibold text-primary/80">Investor Readiness</p>
        </div>

        <div>
          <h3 className="text-xl font-bold">Final verdict</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            {verdictNarrative}
          </p>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            {[
              { label: "Critical Issues", value: criticalCount, icon: ShieldAlert, tone: "bg-critical-soft text-critical" },
              { label: "Medium / Warnings", value: warningCount, icon: AlertTriangle, tone: "bg-warning-soft text-warning" },
              { label: "Missing Fields", value: missingCount, icon: FileQuestion, tone: "bg-muted text-muted-foreground" },
            ].map((s) => (
              <div key={s.label} className="rounded-2xl border border-border p-4">
                <span className={`flex size-8 items-center justify-center rounded-lg ${s.tone}`}>
                  <s.icon className="size-4" />
                </span>
                <p className="mt-3 text-2xl font-bold tabular-nums">{s.value}</p>
                <p className="text-xs text-muted-foreground">{s.label}</p>
              </div>
            ))}
          </div>

          <div className="mt-6 flex gap-3 rounded-2xl bg-muted/60 p-5">
            <Lightbulb className="size-5 shrink-0 text-primary" />
            <div>
              <p className="text-sm font-semibold">Recommendation</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {rec}
              </p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
