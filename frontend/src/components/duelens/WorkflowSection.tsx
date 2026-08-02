import { motion } from "motion/react";
import { UploadCloud, Cpu, LayoutDashboard, Download, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const steps = [
  {
    icon: UploadCloud,
    step: "01",
    title: "Upload your data room",
    body: "Drop in up to 5 documents — pitch deck, financial statements, MIS, projections, and cap table. Files never leave your device.",
  },
  {
    icon: Cpu,
    step: "02",
    title: "AI classifies each document",
    body: "Duelens auto-detects document types by filename and content patterns. You can review and override any classification before proceeding.",
  },
  {
    icon: LayoutDashboard,
    step: "03",
    title: "Cross-document analysis",
    body: "Every financial metric is reconciled across all documents. Mismatches, warnings, and missing data are surfaced with severity scores.",
  },
  {
    icon: Download,
    step: "04",
    title: "Export the investor report",
    body: "Download a full consistency report with discrepancy log and AI-generated follow-up questions — ready for your investment committee.",
  },
];

export function WorkflowSection() {
  return (
    <section id="workflow" className="border-b border-border py-24">
      <div className="mx-auto max-w-5xl px-5">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <p className="text-xs font-semibold tracking-[0.18em] text-primary uppercase">
            How it works
          </p>
          <h2 className="mt-3 text-3xl font-bold md:text-4xl">
            From upload to insight in four steps
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-muted-foreground">
            No setup, no integrations. Just drop your documents and get a consistency report.
          </p>
        </motion.div>

        <div className="mt-14 grid gap-6 md:grid-cols-2">
          {steps.map((s, i) => (
            <motion.div
              key={s.step}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.15 }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              whileHover={{ y: -4 }}
              className="surface flex gap-5 p-6"
            >
              <div className="flex flex-col items-center gap-3">
                <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-[var(--shadow-glow)]">
                  <s.icon className="size-5" />
                </span>
                <span className="text-xs font-bold tabular-nums text-muted-foreground">
                  {s.step}
                </span>
              </div>
              <div>
                <h3 className="text-base font-semibold">{s.title}</h3>
                <p className="mt-1.5 text-sm text-muted-foreground">{s.body}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-10 text-center"
        >
          <Button size="lg" asChild className="group h-12 rounded-full px-8 shadow-[var(--shadow-glow)]">
            <Link href="/dashboard">
              Try it now
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
