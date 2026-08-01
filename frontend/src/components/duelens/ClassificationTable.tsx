import { motion, AnimatePresence } from "motion/react";
import { useEffect, useState } from "react";
import { Loader2, CheckCircle2, Pencil, ArrowRight, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CLASSIFY_MESSAGES, type Classified } from "@/data/mock";

export function ClassificationTable({
  rows,
  onContinue,
  onEdit,
}: {
  rows: Classified[];
  onContinue: () => void;
  onEdit: () => void;
}) {
  const [step, setStep] = useState(0);
  const done = step >= CLASSIFY_MESSAGES.length;

  useEffect(() => {
    if (done) return;
    const t = setTimeout(() => setStep((s) => s + 1), 1000);
    return () => clearTimeout(t);
  }, [step, done]);

  return (
    <section id="classification" className="mx-auto max-w-5xl px-5 pb-20 md:pb-24">
      <motion.div
        initial={{ opacity: 0, y: 28 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="surface p-6 md:p-10"
      >
        <p className="text-xs font-semibold tracking-[0.18em] text-primary uppercase">Step 02</p>
        <h2 className="mt-3 text-2xl font-bold md:text-3xl">AI document classification</h2>

        <AnimatePresence mode="wait">
          {!done ? (
            <motion.div
              key="loading"
              exit={{ opacity: 0 }}
              className="flex flex-col items-center py-16"
            >
              <Loader2 className="size-8 animate-spin text-primary" />
              <AnimatePresence mode="wait">
                <motion.p
                  key={step}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  className="mt-5 text-sm font-medium text-muted-foreground"
                >
                  {CLASSIFY_MESSAGES[Math.min(step, CLASSIFY_MESSAGES.length - 1)]}
                </motion.p>
              </AnimatePresence>
              <div className="mt-6 h-1.5 w-64 overflow-hidden rounded-full bg-muted">
                <motion.div
                  className="h-full rounded-full bg-primary"
                  animate={{ width: `${((step + 1) / CLASSIFY_MESSAGES.length) * 100}%` }}
                  transition={{ duration: 0.8 }}
                />
              </div>
            </motion.div>
          ) : (
            <motion.div key="table" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
              <div className="mt-6 overflow-x-auto rounded-2xl border border-border">
                <table className="w-full min-w-[640px] text-left text-sm">
                  <thead className="bg-muted/70 text-xs tracking-wide text-muted-foreground uppercase">
                    <tr>
                      {["Uploaded File", "Detected Type", "Confidence", "Status"].map((h) => (
                        <th key={h} className="px-5 py-3 font-semibold">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((r, i) => (
                      <motion.tr
                        key={r.file}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.07 }}
                        className="border-t border-border"
                      >
                        <td className="px-5 py-4 font-medium">
                          <span className="flex items-center gap-2.5">
                            <FileText className="size-4 text-primary" />
                            {r.file}
                          </span>
                        </td>
                        <td className="px-5 py-4 text-muted-foreground">{r.type}</td>
                        <td className="px-5 py-4">
                          <div className="flex items-center gap-2">
                            <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
                              <motion.div
                                className="h-full bg-verified"
                                initial={{ width: 0 }}
                                animate={{ width: `${r.confidence}%` }}
                                transition={{ delay: 0.2 + i * 0.07, duration: 0.6 }}
                              />
                            </div>
                            <span className="text-xs font-semibold">{r.confidence}%</span>
                          </div>
                        </td>
                        <td className="px-5 py-4">
                          <span className="inline-flex items-center gap-1.5 rounded-full bg-verified-soft px-2.5 py-1 text-xs font-semibold text-verified">
                            <CheckCircle2 className="size-3.5" />
                            {r.status}
                          </span>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-8 rounded-2xl bg-muted/60 p-6">
                <h3 className="text-base font-semibold">Review AI Classification</h3>
                <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground">
                  We've automatically identified each uploaded document using filename and document
                  patterns. Please review before continuing.
                </p>
                <div className="mt-5 flex flex-wrap gap-3">
                  <Button onClick={onContinue} className="group h-11 rounded-full px-6">
                    Continue with Analysis
                    <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
                  </Button>
                  <Button
                    variant="outline"
                    onClick={onEdit}
                    className="h-11 rounded-full border-border px-6"
                  >
                    <Pencil className="size-4" />
                    Edit Classification
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </section>
  );
}
