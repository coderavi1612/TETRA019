import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { Check, Loader2, Cpu } from "lucide-react";
import { PROCESS_MESSAGES } from "@/data/mock";

export function ProcessingCard({ onDone }: { onDone: () => void }) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const start = Date.now();
    const id = setInterval(() => {
      const p = Math.min(100, ((Date.now() - start) / 5000) * 100);
      setProgress(p);
      if (p >= 100) clearInterval(id);
    }, 50);
    const t = setTimeout(onDone, 5200);
    return () => {
      clearInterval(id);
      clearTimeout(t);
    };
  }, [onDone]);

  const activeIndex = Math.min(
    PROCESS_MESSAGES.length - 1,
    Math.floor((progress / 100) * PROCESS_MESSAGES.length),
  );

  return (
    <section className="mx-auto max-w-3xl px-5 pb-20 md:pb-24">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="surface p-6 md:p-10"
      >
        <div className="flex items-center gap-3">
          <span className="flex size-10 items-center justify-center rounded-xl bg-primary-soft text-primary">
            <Cpu className="size-5" />
          </span>
          <div>
            <h2 className="text-xl font-bold">Analyzing documents</h2>
            <p className="text-sm text-muted-foreground">
              Reconciling metrics across 5 documents
            </p>
          </div>
          <span className="ml-auto text-2xl font-bold tabular-nums">{Math.round(progress)}%</span>
        </div>

        <div className="mt-6 h-2 overflow-hidden rounded-full bg-muted">
          <motion.div
            className="h-full rounded-full bg-primary"
            animate={{ width: `${progress}%` }}
            transition={{ ease: "linear", duration: 0.05 }}
          />
        </div>

        <ul className="mt-8 space-y-3">
          {PROCESS_MESSAGES.map((m, i) => {
            const complete = i < activeIndex || progress >= 100;
            const active = i === activeIndex && progress < 100;
            return (
              <li
                key={m}
                className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-sm transition-colors ${
                  complete
                    ? "border-verified/30 bg-verified-soft/60"
                    : active
                      ? "border-primary/30 bg-primary-soft"
                      : "border-border bg-card opacity-55"
                }`}
              >
                {complete ? (
                  <Check className="size-4 text-verified" />
                ) : active ? (
                  <Loader2 className="size-4 animate-spin text-primary" />
                ) : (
                  <span className="size-4 rounded-full border border-border" />
                )}
                <span className="font-medium">{m}</span>
              </li>
            );
          })}
        </ul>
      </motion.div>
    </section>
  );
}
