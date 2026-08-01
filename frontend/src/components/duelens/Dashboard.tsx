"use client";

import { motion } from "motion/react";
import { Building2, Gauge, BadgeCheck, CheckCircle2, AlertTriangle, ShieldAlert, FileQuestion } from "lucide-react";
import { SummaryCard } from "./SummaryCard";
import { ComparisonTable } from "./ComparisonTable";
import { DiscrepancyCard } from "./DiscrepancyCard";
import { QuestionCard } from "./QuestionCard";
import { VerdictCard } from "./VerdictCard";
import { DownloadCard } from "./DownloadCard";
import { useDuelensData } from "@/context/DuelensDataContext";

const icons = [CheckCircle2, AlertTriangle, ShieldAlert, FileQuestion];

export function Dashboard() {
  const { readinessResults, issues, companyId } = useDuelensData();

  const companyName = readinessResults?.summary?.company_name || (readinessResults?.summary?.company_id 
    ? readinessResults.summary.company_id.charAt(0).toUpperCase() + readinessResults.summary.company_id.slice(1)
    : companyId.charAt(0).toUpperCase() + companyId.slice(1));
    
  const score = readinessResults?.summary?.readiness_score !== undefined 
    ? `${readinessResults.summary.readiness_score}%` 
    : "0%";

  const rawStatus = readinessResults?.summary?.overall_status || "PENDING";
  const statusLabel = rawStatus.replace(/_/g, ' ');

  const matchesCount = readinessResults?.summary?.verified_matches ?? 0;
  const criticalCount = issues.filter(i => i.severity === 'CRITICAL').length;
  const warningCount = issues.filter(i => i.severity === 'WARNING').length;
  const missingCount = readinessResults?.summary?.missing_information ?? 0;

  const dynamicSummary = [
    { label: "Verified Matches", value: matchesCount, tone: "verified" as const },
    { label: "Warnings", value: warningCount, tone: "warning" as const },
    { label: "Critical Issues", value: criticalCount, tone: "critical" as const },
    { label: "Missing Information", value: missingCount, tone: "muted" as const },
  ];

  const dynamicDiscrepancies = issues.map(issue => {
    const pairs = Object.entries(issue.source_values || {}).map(([doc, val]) => ({
      label: doc.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
      value: val !== null && val !== undefined ? String(val) : "—"
    }));

    return {
      id: issue.id,
      title: issue.field_path.split('.').pop()?.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') || issue.field_path,
      kind: issue.classification,
      severity: issue.severity === 'CRITICAL' ? ('High' as const) : issue.severity === 'WARNING' ? ('Medium' as const) : ('Low' as const),
      pairs,
      note: issue.description
    };
  });

  const dynamicQuestions = (readinessResults?.questions || []).map(q => ({
    id: q.id,
    question: q.question
  }));

  return (
    <section id="dashboard" className="mx-auto max-w-6xl space-y-12 px-5 pb-24">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="surface grid gap-6 p-6 md:grid-cols-3 md:p-8"
      >
        <div className="flex items-center gap-3">
          <span className="flex size-11 items-center justify-center rounded-2xl bg-primary-soft text-primary">
            <Building2 className="size-5" />
          </span>
          <div>
            <p className="text-xs text-muted-foreground">Company</p>
            <p className="text-lg font-bold">{companyName}</p>
          </div>
        </div>
        <div className="flex items-center gap-3 md:justify-center">
          <span className="flex size-11 items-center justify-center rounded-2xl bg-primary-soft text-primary">
            <Gauge className="size-5" />
          </span>
          <div>
            <p className="text-xs text-muted-foreground">Consistency Score</p>
            <p className="text-lg font-bold tabular-nums">{score}</p>
          </div>
        </div>
        <div className="flex items-center gap-3 md:justify-end">
          <span className="flex size-11 items-center justify-center rounded-2xl bg-verified-soft text-verified">
            <BadgeCheck className="size-5" />
          </span>
          <div>
            <p className="text-xs text-muted-foreground">Status</p>
            <p className="text-lg font-bold text-verified capitalize">{statusLabel.toLowerCase()}</p>
          </div>
        </div>
      </motion.div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {dynamicSummary.map((s, i) => (
          <SummaryCard key={s.label} {...s} icon={icons[i] ?? CheckCircle2} index={i} />
        ))}
      </div>

      <ComparisonTable />

      <div>
        <h3 className="text-lg font-semibold">Discrepancies</h3>
        {dynamicDiscrepancies.length > 0 ? (
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            {dynamicDiscrepancies.map((d, i) => (
              <DiscrepancyCard key={d.id} {...d} index={i} />
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-muted-foreground">No discrepancies identified.</p>
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold">AI follow-up questions</h3>
        {dynamicQuestions.length > 0 ? (
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            {dynamicQuestions.map((q, i) => (
              <QuestionCard key={q.id} question={q.question} index={i} />
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-muted-foreground">No follow-up questions required.</p>
        )}
      </div>

      <VerdictCard />
      <DownloadCard />
    </section>
  );
}
