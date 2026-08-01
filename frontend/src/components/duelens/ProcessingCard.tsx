"use client";

import { motion } from "motion/react";
import { useEffect, useState, useRef } from "react";
import { Check, Loader2, Cpu, AlertCircle } from "lucide-react";
import { useDuelensData } from "@/context/DuelensDataContext";
import { startPipeline, getPipelineStatus } from "@/lib/api";

export function ProcessingCard({ onDone }: { onDone: () => void }) {
  const { companyId } = useDuelensData();
  
  const [progress, setProgress] = useState(0);
  const [currentStageName, setCurrentStageName] = useState("Initializing...");
  const [status, setStatus] = useState<string>("ACCEPTED");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  const [stages, setStages] = useState<Array<{ name: string; status: string; duration_ms: number }>>([
    { name: "parse", status: "pending", duration_ms: 0 },
    { name: "extract", status: "pending", duration_ms: 0 },
    { name: "reason", status: "pending", duration_ms: 0 },
    { name: "verify", status: "pending", duration_ms: 0 },
    { name: "readiness", status: "pending", duration_ms: 0 },
  ]);

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const didTriggerRef = useRef(false);

  useEffect(() => {
    if (didTriggerRef.current) return;
    didTriggerRef.current = true;

    const triggerAndPoll = async () => {
      try {
        // 1. POST /api/v1/pipeline/{company_id}
        const runRes = await startPipeline(companyId);
        const jobId = runRes.job_id;
        setStatus("RUNNING");

        // 2. Poll GET /api/v1/pipeline/{company_id}/status
        pollIntervalRef.current = setInterval(async () => {
          try {
            const statusRes = await getPipelineStatus(companyId, jobId);
            
            // Map stages state
            if (statusRes.stages) {
              setStages(statusRes.stages);
            }
            
            setProgress(statusRes.progress);
            setStatus(statusRes.status);
            setCurrentStageName(statusRes.current_stage || "Running...");

            if (statusRes.status === "COMPLETED") {
              if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
              // Wait 500ms to allow progress bar visual feedback, then trigger complete
              setTimeout(onDone, 500);
            } else if (statusRes.status === "FAILED") {
              if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
              setErrorMsg(statusRes.error || "Pipeline execution failed.");
            }
          } catch (pollErr: unknown) {
            console.error("Error polling pipeline status:", pollErr);
          }
        }, 1000);

      } catch (triggerErr: unknown) {
        console.error("Failed to start pipeline runner:", triggerErr);
        setStatus("FAILED");
        const errMsg = triggerErr instanceof Error ? triggerErr.message : "Failed to initiate deep integrity audit.";
        setErrorMsg(errMsg);
      }
    };

    triggerAndPoll();

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [companyId, onDone]);

  const stageLabels: Record<string, string> = {
    parse: "Document Ingestion & Parsing",
    extract: "AI Fact Extraction & Specifications",
    reason: "Local AI Semantic Reasoning Audit",
    verify: "Cross-document Deterministic Verification",
    readiness: "AI Readiness & Scoring Evaluation",
  };

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
              {status === "FAILED" ? "Audit aborted due to an error" : `Current Stage: ${currentStageName}`}
            </p>
          </div>
          <span className="ml-auto text-2xl font-bold tabular-nums">
            {status === "FAILED" ? "Error" : `${Math.round(progress)}%`}
          </span>
        </div>

        {status !== "FAILED" ? (
          <div className="mt-6 h-2 overflow-hidden rounded-full bg-muted">
            <motion.div
              className="h-full rounded-full bg-primary"
              animate={{ width: `${progress}%` }}
              transition={{ ease: "linear", duration: 0.2 }}
            />
          </div>
        ) : (
          <div className="mt-6 flex items-start gap-2.5 rounded-xl border border-critical/30 bg-critical-soft/50 p-4 text-xs text-critical">
            <AlertCircle className="size-4 shrink-0" />
            <div>
              <p className="font-bold">Audit Error</p>
              <p className="mt-1 font-medium">{errorMsg}</p>
            </div>
          </div>
        )}

        <ul className="mt-8 space-y-3">
          {stages.map((stage) => {
            const complete = stage.status === "completed";
            const active = stage.status === "running";
            const failed = stage.status === "failed";
            const label = stageLabels[stage.name] || stage.name;

            return (
              <li
                key={stage.name}
                className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-sm transition-colors ${
                  complete
                    ? "border-verified/30 bg-verified-soft/60"
                    : active
                      ? "border-primary/30 bg-primary-soft"
                      : failed
                        ? "border-critical/30 bg-critical-soft"
                        : "border-border bg-card opacity-55"
                }`}
              >
                {complete ? (
                  <Check className="size-4 text-verified" />
                ) : active ? (
                  <Loader2 className="size-4 animate-spin text-primary" />
                ) : failed ? (
                  <AlertCircle className="size-4 text-critical" />
                ) : (
                  <span className="size-4 rounded-full border border-border" />
                )}
                <span className="font-medium flex-1 capitalize">{label}</span>
                {stage.duration_ms > 0 && (
                  <span className="text-[10px] font-bold text-muted-foreground tabular-nums">
                    {(stage.duration_ms / 1000).toFixed(2)}s
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      </motion.div>
    </section>
  );
}
