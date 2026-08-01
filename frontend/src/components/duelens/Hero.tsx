import { motion } from "motion/react";
import { ArrowRight, Sparkles, FileSearch, ScanLine, GitCompare } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.1, ease: "easeOut" as const },
  }),
};

export function Hero() {
  return (
    <section id="top" className="grid-canvas relative overflow-hidden border-b border-border">
      <div className="mx-auto max-w-5xl px-5 pt-20 pb-24 text-center md:pt-28 md:pb-32">
        <motion.div variants={fadeUp} initial="hidden" animate="show" custom={0}>
          <span className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5 text-xs font-medium text-muted-foreground shadow-[var(--shadow-soft)]">
            <Sparkles className="size-3.5 text-primary" />
            Due diligence, in minutes not weeks
          </span>
        </motion.div>

        <motion.h1
          variants={fadeUp}
          initial="hidden"
          animate="show"
          custom={1}
          className="mx-auto mt-7 max-w-4xl text-4xl leading-[1.08] font-extrabold text-balance md:text-6xl"
        >
          AI-Powered Cross-Document Financial Consistency Checker
        </motion.h1>

        <motion.p
          variants={fadeUp}
          initial="hidden"
          animate="show"
          custom={2}
          className="mx-auto mt-6 max-w-2xl text-base text-pretty text-muted-foreground md:text-lg"
        >
          Upload fundraising documents and instantly verify financial consistency before making
          investment decisions.
        </motion.p>

        <motion.div
          variants={fadeUp}
          initial="hidden"
          animate="show"
          custom={3}
          className="mt-9 flex flex-wrap items-center justify-center gap-3"
        >
          <Button
            size="lg"
            asChild
            className="group h-12 rounded-full px-7 text-sm shadow-[var(--shadow-glow)]"
          >
            <Link href="/app">
              Get Started
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </Button>
          <Button
            size="lg"
            variant="outline"
            asChild
            className="h-12 rounded-full border-border px-7 text-sm"
          >
            <a href="#workflow">See how it works</a>
          </Button>
        </motion.div>

        <motion.div
          variants={fadeUp}
          initial="hidden"
          animate="show"
          custom={4}
          id="features"
          className="mt-16 grid gap-4 text-left sm:grid-cols-3"
        >
          {[
            {
              icon: FileSearch,
              title: "Document intelligence",
              body: "Auto-detects decks, MIS, projections and cap tables.",
            },
            {
              icon: GitCompare,
              title: "Cross-doc matching",
              body: "Every metric reconciled across all five documents.",
            },
            {
              icon: ScanLine,
              title: "Investor report",
              body: "A readiness score with flagged risks and questions.",
            },
          ].map((f) => (
            <motion.div
              key={f.title}
              whileHover={{ y: -4 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              className="surface p-6"
            >
              <span className="flex size-10 items-center justify-center rounded-xl bg-primary-soft text-primary">
                <f.icon className="size-5" />
              </span>
              <h3 className="mt-4 text-sm font-semibold">{f.title}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground">{f.body}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
