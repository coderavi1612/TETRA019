"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { HelpCircle, Copy, Download, Check, MessageSquareText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDuelensData } from "@/context/DuelensDataContext";
import { getBaseApiUrl } from "@/lib/api/client";
import { toast } from "sonner";

export function FollowUpQuestionsView() {
  const { readinessResults } = useDuelensData();
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const questionsPdfDownload = readinessResults?.downloads?.find(
    (d: any) => d.name.toLowerCase().includes("questions") && d.type === "pdf"
  ) || readinessResults?.downloads?.find((d: any) => d.type === "pdf");

  const handleExportPDF = () => {
    if (questionsPdfDownload) {
      const fullUrl = `${getBaseApiUrl()}${questionsPdfDownload.url}`;
      window.open(fullUrl, "_blank");
      toast.success("Opening Follow-up Questions PDF...");
    } else {
      window.print();
    }
  };

  const rawQuestions = readinessResults?.questions || [];
  const questions = rawQuestions.map((q: any) => ({
    id: q.id || q.question_id || "",
    question: q.question || "",
    rationale: q.rationale || q.why_it_matters || "",
    target_document: q.target_document || q.required_document || "",
    priority: q.priority || "MEDIUM",
    target_metric: q.target_metric || q.related_issue || ""
  }));

  // Map category filter to target documents dynamically, filtering out null/empty values
  const categories = [
    "All",
    ...Array.from(
      new Set(
        questions
          .map((q) => q.target_document)
          .filter((doc): doc is string => typeof doc === "string" && doc.trim().length > 0)
      )
    )
  ];

  const filtered = questions.filter(
    (q) => categoryFilter === "All" || q.target_document === categoryFilter
  );

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    toast.success("Question copied to clipboard.");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const generateAIAnswer = (id: string, metric: string, doc: string) => {
    const draftText = `Reconciling the metric value for '${metric}' in '${doc}' against other fundraising materials. The delta is due to a timeline difference in billing calculations, and the updated figures will be reflected in the next data-room patch.`;
    setDraftAnswers((prev) => ({ ...prev, [id]: draftText }));
    toast.success("AI generated a recommended founder response draft.");
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary">
            <MessageSquareText className="size-3.5" />
            Due Diligence Question Generator
          </span>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Follow-up Questions for Management
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Automatically formulated inquiries derived from detected cross-document inconsistencies for investment committee prep.
          </p>
        </div>

        <Button
          onClick={handleExportPDF}
          className="rounded-xl shadow-[var(--shadow-glow)]"
        >
          <Download className="mr-2 size-4" />
          Export Question Sheet (PDF)
        </Button>
      </div>

      {/* Category Filter Tabs */}
      {categories.length > 1 && (
        <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-border bg-muted/40 p-1.5 w-fit">
          {categories.map((cat, idx) => (
            <button
              key={`${cat}-${idx}`}
              onClick={() => setCategoryFilter(cat)}
              className={`rounded-xl px-3.5 py-1.5 text-xs font-semibold capitalize transition-all ${
                categoryFilter === cat
                  ? "bg-primary text-primary-foreground shadow-xs"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {cat === "All" ? "All" : (cat || "").replace(/_/g, " ").replace(".json", "")}
            </button>
          ))}
        </div>
      )}

      {/* Questions List */}
      {filtered.length > 0 ? (
        <div className="space-y-6">
          {filtered.map((item, idx) => {
            const formattedCategory = (item.target_document || "").replace(/_/g, " ").replace(".json", "");
            const uiPriority = item.priority === "HIGH" ? "Urgent" : item.priority === "MEDIUM" ? "High" : "Low";

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08 }}
                className="surface p-6 space-y-4"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="flex items-start gap-3">
                    <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary-soft text-primary">
                      <HelpCircle className="size-5" />
                    </span>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-bold text-muted-foreground">{item.id}</span>
                        <span className="rounded-full bg-muted px-2.5 py-0.5 text-[10px] font-semibold text-muted-foreground capitalize">
                          {formattedCategory}
                        </span>
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase ${
                            item.priority === "HIGH"
                              ? "bg-critical-soft text-critical"
                              : item.priority === "MEDIUM"
                                ? "bg-warning-soft text-warning"
                                : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {uiPriority} Priority
                        </span>
                      </div>
                      <h3 className="mt-1.5 text-base font-bold text-foreground leading-snug">
                        {item.question}
                      </h3>
                    </div>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopy(item.id, item.question)}
                    className="shrink-0 rounded-xl text-xs"
                  >
                    {copiedId === item.id ? <Check className="mr-1.5 size-3.5 text-verified" /> : <Copy className="mr-1.5 size-3.5" />}
                    {copiedId === item.id ? "Copied" : "Copy"}
                  </Button>
                </div>

                {/* Context snippet */}
                <div className="rounded-xl border border-border bg-muted/40 p-3.5 text-xs text-muted-foreground leading-relaxed">
                  <span className="font-semibold text-foreground">Flagged Context / Rationale: </span>
                  {item.rationale}
                </div>
              </motion.div>
            );
          })}
        </div>
      ) : (
        <div className="surface flex flex-col items-center justify-center py-24 text-center text-muted-foreground">
          <MessageSquareText className="size-10 text-muted-foreground/35 mb-2.5 animate-pulse" />
          <p className="text-sm font-semibold">No follow-up questions generated.</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            Your data-room documents did not generate any critical due diligence follow-up questions.
          </p>
        </div>
      )}
    </div>
  );
}
