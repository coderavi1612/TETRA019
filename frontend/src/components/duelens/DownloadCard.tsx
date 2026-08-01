"use client";

import { motion } from "motion/react";
import { Download, FileText, Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { toast } from "sonner";
import { downloadPDF } from "@/lib/download";

export function DownloadCard() {
  const [state, setState] = useState<"idle" | "loading" | "done">("idle");

  const handleDownload = async () => {
    setState("loading");
    try {
      await downloadPDF();
      setState("done");
      toast.success("Report downloaded");
      setTimeout(() => setState("idle"), 2500);
    } catch {
      toast.error("Download failed — please try again");
      setState("idle");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.6 }}
      className="surface grid gap-8 p-6 md:grid-cols-[1fr_auto] md:items-center md:p-10"
    >
      <div>
        <span className="flex size-11 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-[var(--shadow-glow)]">
          <Download className="size-5" />
        </span>
        <h3 className="mt-4 text-xl font-bold">Take the report with you</h3>
        <p className="mt-2 max-w-lg text-sm text-muted-foreground">
          Export the full consistency analysis, discrepancy log and follow-up questions as a
          formatted PDF for your investment committee.
        </p>
      </div>

      <Button
        size="lg"
        className="h-12 rounded-full px-8"
        onClick={handleDownload}
        disabled={state === "loading"}
      >
        {state === "loading" ? (
          <Loader2 className="size-4 animate-spin" />
        ) : state === "done" ? (
          <Check className="size-4" />
        ) : (
          <FileText className="size-4" />
        )}
        {state === "loading" ? "Generating…" : state === "done" ? "Downloaded" : "Download Investor Report (PDF)"}
      </Button>
    </motion.div>
  );
}
