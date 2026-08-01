import { motion } from "motion/react";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { COMPARISON, type RowStatus } from "@/data/mock";

const statusStyles: Record<RowStatus, string> = {
  Verified: "bg-verified-soft text-verified",
  Warning: "bg-warning-soft text-warning",
  Mismatch: "bg-critical-soft text-critical",
};

const statusIcon = {
  Verified: CheckCircle2,
  Warning: AlertTriangle,
  Mismatch: XCircle,
};

const columns = ["Metric", "Pitch Deck", "Financials", "MIS", "Projection", "Cap Table", "Status"];

export function ComparisonTable() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.15 }}
      transition={{ duration: 0.6 }}
      className="surface overflow-hidden"
    >
      <div className="border-b border-border px-6 py-5">
        <h3 className="text-lg font-semibold">Cross-document comparison</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Every metric traced back to its source document.
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] text-left text-sm">
          <thead className="bg-muted/70 text-xs tracking-wide text-muted-foreground uppercase">
            <tr>
              {columns.map((c) => (
                <th key={c} className="px-6 py-3 font-semibold">
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {COMPARISON.map((row, i) => {
              const Icon = statusIcon[row.status];
              return (
                <motion.tr
                  key={row.metric}
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.06 }}
                  className="border-t border-border transition-colors hover:bg-muted/40"
                >
                  <td className="px-6 py-4 font-semibold">{row.metric}</td>
                  {row.values.map((v, idx) => (
                    <td
                      key={idx}
                      className={`px-6 py-4 tabular-nums ${v === "—" ? "text-muted-foreground/60" : ""}`}
                    >
                      {v}
                    </td>
                  ))}
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${statusStyles[row.status]}`}
                    >
                      <Icon className="size-3.5" />
                      {row.status}
                    </span>
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
