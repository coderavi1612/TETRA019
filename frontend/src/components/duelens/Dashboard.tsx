import { motion } from "motion/react";
import { Building2, Gauge, BadgeCheck, CheckCircle2, AlertTriangle, ShieldAlert, FileQuestion } from "lucide-react";
import { SummaryCard } from "./SummaryCard";
import { ComparisonTable } from "./ComparisonTable";
import { DiscrepancyCard } from "./DiscrepancyCard";
import { QuestionCard } from "./QuestionCard";
import { VerdictCard } from "./VerdictCard";
import { DownloadCard } from "./DownloadCard";
import { DISCREPANCIES, QUESTIONS, SUMMARY } from "@/data/mock";

const icons = [CheckCircle2, AlertTriangle, ShieldAlert, FileQuestion];

export function Dashboard() {
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
            <p className="text-lg font-bold">TechNova Pvt Ltd</p>
          </div>
        </div>
        <div className="flex items-center gap-3 md:justify-center">
          <span className="flex size-11 items-center justify-center rounded-2xl bg-primary-soft text-primary">
            <Gauge className="size-5" />
          </span>
          <div>
            <p className="text-xs text-muted-foreground">Consistency Score</p>
            <p className="text-lg font-bold tabular-nums">88%</p>
          </div>
        </div>
        <div className="flex items-center gap-3 md:justify-end">
          <span className="flex size-11 items-center justify-center rounded-2xl bg-verified-soft text-verified">
            <BadgeCheck className="size-5" />
          </span>
          <div>
            <p className="text-xs text-muted-foreground">Status</p>
            <p className="text-lg font-bold text-verified">Investor Ready</p>
          </div>
        </div>
      </motion.div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {SUMMARY.map((s, i) => (
          <SummaryCard key={s.label} {...s} icon={icons[i] ?? CheckCircle2} index={i} />
        ))}
      </div>

      <ComparisonTable />

      <div>
        <h3 className="text-lg font-semibold">Discrepancies</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {DISCREPANCIES.map((d, i) => (
            <DiscrepancyCard key={d.title} {...d} index={i} />
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold">AI follow-up questions</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {QUESTIONS.map((q, i) => (
            <QuestionCard key={q.id} question={q.question} index={i} />
          ))}
        </div>
      </div>

      <VerdictCard />
      <DownloadCard />
    </section>
  );
}
