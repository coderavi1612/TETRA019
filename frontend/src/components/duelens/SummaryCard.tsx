import { motion } from "motion/react";
import type { LucideIcon } from "lucide-react";

const tones = {
  verified: "bg-verified-soft text-verified",
  warning: "bg-warning-soft text-warning",
  critical: "bg-critical-soft text-critical",
  muted: "bg-muted text-muted-foreground",
} as const;

export function SummaryCard({
  label,
  value,
  tone,
  icon: Icon,
  index,
}: {
  label: string;
  value: number;
  tone: keyof typeof tones;
  icon: LucideIcon;
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      whileHover={{ y: -4 }}
      className="surface p-6"
    >
      <span className={`flex size-10 items-center justify-center rounded-xl ${tones[tone]}`}>
        <Icon className="size-5" />
      </span>
      <p className="mt-4 text-3xl font-bold tabular-nums">{value}</p>
      <p className="mt-1 text-sm text-muted-foreground">{label}</p>
    </motion.div>
  );
}
