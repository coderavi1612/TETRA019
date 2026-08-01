"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { HelpCircle, Sparkles, Copy, Download, Check, MessageSquareText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { QUESTIONS } from "@/data/mock";
import { toast } from "sonner";

export function FollowUpQuestionsView() {
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [draftAnswers, setDraftAnswers] = useState<Record<string, string>>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const filtered = QUESTIONS.filter(
    (q) => categoryFilter === "All" || q.category === categoryFilter
  );

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    toast.success("Question copied to clipboard.");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const generateAIAnswer = (id: string, defaultAnswer: string) => {
    setDraftAnswers((prev) => ({ ...prev, [id]: defaultAnswer }));
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
          onClick={() => toast.success("Exported Due Diligence Question Sheet (PDF).")}
          className="rounded-xl shadow-[var(--shadow-glow)]"
        >
          <Download className="mr-2 size-4" />
          Export Question Sheet
        </Button>
      </div>

      {/* Category Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-border bg-muted/40 p-1.5">
        {["All", "Financial Performance", "Cap Table & Equity", "Operational Metrics"].map((cat) => (
          <button
            key={cat}
            onClick={() => setCategoryFilter(cat)}
            className={`rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all ${
              categoryFilter === cat
                ? "bg-primary text-primary-foreground shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Questions List */}
      <div className="space-y-6">
        {filtered.map((item, idx) => (
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
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-muted-foreground">{item.id}</span>
                    <span className="rounded-full bg-muted px-2.5 py-0.5 text-[10px] font-semibold text-muted-foreground">
                      {item.category}
                    </span>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                        item.priority === "Urgent"
                          ? "bg-critical-soft text-critical"
                          : item.priority === "High"
                            ? "bg-warning-soft text-warning"
                            : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {item.priority} Priority
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
              <span className="font-semibold text-foreground">Flagged Context: </span>
              {item.context}
            </div>

            {/* Draft Response Box */}
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-foreground flex items-center gap-1.5">
                  <Sparkles className="size-3.5 text-primary" />
                  Management / Founder Answer Draft:
                </span>
                <button
                  onClick={() => generateAIAnswer(item.id, item.suggestedAnswer)}
                  className="font-bold text-primary hover:underline text-xs"
                >
                  Generate Draft Answer
                </button>
              </div>

              <div className="relative">
                <textarea
                  rows={2}
                  value={draftAnswers[item.id] ?? item.suggestedAnswer}
                  onChange={(e) =>
                    setDraftAnswers({ ...draftAnswers, [item.id]: e.target.value })
                  }
                  placeholder="Draft response..."
                  className="w-full rounded-xl border border-border bg-background p-3 text-xs focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
