"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { AppNavbar } from "@/components/duelens/AppNavbar";
import { UploadCard } from "@/components/duelens/UploadCard";
import { ClassificationTable } from "@/components/duelens/ClassificationTable";
import { ClassificationModal } from "@/components/duelens/ClassificationModal";
import { ProcessingCard } from "@/components/duelens/ProcessingCard";
import { Dashboard } from "@/components/duelens/Dashboard";
import { Footer } from "@/components/duelens/Footer";
import { Toaster } from "@/components/ui/sonner";
import { CLASSIFICATION, type Classified } from "@/data/mock";

type Stage = "upload" | "classify" | "processing" | "dashboard";

export function AppPage() {
  const [files, setFiles] = useState<string[]>([]);
  const [stage, setStage] = useState<Stage>("upload");
  const [rows, setRows] = useState<Classified[]>(CLASSIFICATION);
  const [modalOpen, setModalOpen] = useState(false);
  const scrollTarget = useRef<Stage | null>(null);

  const scrollTo = (id: string) =>
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });

  useEffect(() => {
    if (!scrollTarget.current) return;
    const id = requestAnimationFrame(() => {
      scrollTo(stage === "dashboard" ? "dashboard" : "classification");
      scrollTarget.current = null;
    });
    return () => cancelAnimationFrame(id);
  }, [stage]);

  const advance = (next: Stage) => {
    scrollTarget.current = next;
    setStage(next);
  };

  const onDone = useCallback(() => advance("dashboard"), []);

  return (
    <main>
      <AppNavbar />

      {/* Step indicator */}
      <div className="border-b border-border bg-muted/40">
        <div className="mx-auto flex max-w-6xl items-center gap-2 overflow-x-auto px-5 py-3">
          {(["upload", "classify", "processing", "dashboard"] as Stage[]).map((s, i) => {
            const labels: Record<Stage, string> = {
              upload: "Upload",
              classify: "Classify",
              processing: "Analyzing",
              dashboard: "Results",
            };
            const idx = ["upload", "classify", "processing", "dashboard"].indexOf(stage);
            const done = i < idx;
            const active = s === stage;
            return (
              <div key={s} className="flex items-center gap-2">
                {i > 0 && <div className="h-px w-8 shrink-0 bg-border" />}
                <span
                  className={`flex items-center gap-1.5 whitespace-nowrap rounded-full px-3 py-1 text-xs font-semibold transition-colors ${
                    active
                      ? "bg-primary text-primary-foreground"
                      : done
                        ? "bg-verified-soft text-verified"
                        : "text-muted-foreground"
                  }`}
                >
                  <span className="tabular-nums">{i + 1}</span>
                  {labels[s]}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div id="workflow" className="pt-4">
        <UploadCard
          files={files}
          setFiles={(f) => {
            setFiles(f);
            if (f.length === 0) setStage("upload");
          }}
          onContinue={() => advance("classify")}
        />
      </div>

      <AnimatePresence mode="wait">
        {stage === "classify" && (
          <motion.div key="classify" exit={{ opacity: 0, y: -16 }}>
            <ClassificationTable
              rows={rows}
              onContinue={() => advance("processing")}
              onEdit={() => setModalOpen(true)}
            />
          </motion.div>
        )}
        {stage === "processing" && (
          <motion.div key="processing" exit={{ opacity: 0, y: -16 }}>
            <ProcessingCard onDone={onDone} />
          </motion.div>
        )}
        {stage === "dashboard" && (
          <motion.div key="dashboard">
            <Dashboard />
          </motion.div>
        )}
      </AnimatePresence>

      <ClassificationModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        rows={rows}
        onSave={setRows}
      />
      <Footer />
      <Toaster />
    </main>
  );
}
