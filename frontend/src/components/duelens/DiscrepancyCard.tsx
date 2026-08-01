import { motion } from "motion/react";
import { AlertTriangle, ArrowRight, HelpCircle } from "lucide-react";

const severityStyles = {
  High: "bg-critical-soft text-critical",
  Medium: "bg-warning-soft text-warning",
  Low: "bg-muted text-muted-foreground",
} as const;

export function DiscrepancyCard({
  title,
  kind,
  severity,
  pairs,
  note,
  index,
}: {
  title: string;
  kind: string;
  severity: keyof typeof severityStyles;
  pairs: { label: string; value: string }[];
  note?: string;
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 22 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      whileHover={{ y: -4 }}
      className="surface flex h-full flex-col p-6"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className={`flex size-9 items-center justify-center rounded-xl ${severityStyles[severity]}`}>
            {severity === "Low" ? (
              <HelpCircle className="size-4" />
            ) : (
              <AlertTriangle className="size-4" />
            )}
          </span>
          <div>
            <p className="text-sm font-semibold">{title}</p>
            <p className="text-xs text-muted-foreground">{kind}</p>
          </div>
        </div>
        <span
          className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${severityStyles[severity]}`}
        >
          {severity}
        </span>
      </div>

      {pairs.length > 0 && (
        <div className="mt-5 flex items-center gap-3">
          {pairs.map((p, i) => (
            <div key={p.label} className="flex flex-1 items-center gap-3">
              <div className="flex-1 rounded-xl border border-border bg-muted/50 px-3 py-2.5">
                <p className="text-[11px] text-muted-foreground">{p.label}</p>
                <p className="text-base font-bold tabular-nums">{p.value}</p>
              </div>
              {i < pairs.length - 1 && (
                <ArrowRight className="size-4 shrink-0 text-muted-foreground" />
              )}
            </div>
          ))}
        </div>
      )}

      {note && <p className="mt-5 text-sm text-muted-foreground">{note}</p>}
    </motion.div>
  );
}
