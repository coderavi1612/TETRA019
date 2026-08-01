"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { FileSearch, Sparkles, Search, ChevronDown, ChevronRight } from "lucide-react";
import { useDuelensData } from "@/context/DuelensDataContext";

// Custom Collapsible JSON Tree Node
function JSONNode({ name, value, searchTerm }: { name: string; value: unknown; searchTerm: string }) {
  const [collapsed, setCollapsed] = useState(false);
  const isObject = typeof value === "object" && value !== null;

  if (isObject) {
    const objVal = value as Record<string, unknown>;
    const keys = Object.keys(objVal);
    const isArray = Array.isArray(value);
    const summary = isArray ? `Array(${keys.length})` : `Object { ${keys.length} keys }`;

    return (
      <div className="pl-4 font-mono text-xs my-1 select-none">
        <span
          onClick={() => setCollapsed(!collapsed)}
          className="inline-flex items-center gap-1 cursor-pointer font-bold text-primary hover:text-primary/80 transition-colors"
        >
          {collapsed ? <ChevronRight className="size-3" /> : <ChevronDown className="size-3" />}
          <span className="text-foreground">{name}</span>:{" "}
          <span className="text-muted-foreground text-[10px] font-semibold bg-muted px-1.5 py-0.5 rounded">
            {summary}
          </span>
        </span>
        {!collapsed && (
          <div className="border-l border-border pl-3 mt-1 ml-1.5 space-y-1">
            {keys.map((k) => (
              <JSONNode key={k} name={k} value={objVal[k]} searchTerm={searchTerm} />
            ))}
          </div>
        )}
      </div>
    );
  } else {
    const strVal = String(value);
    const matches =
      searchTerm &&
      (name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        strVal.toLowerCase().includes(searchTerm.toLowerCase()));

    return (
      <div
        className={`pl-6 font-mono text-xs my-0.5 transition-colors rounded px-2 py-0.5 ${
          matches ? "bg-primary-soft border-l-2 border-primary font-semibold" : ""
        }`}
      >
        <span className="text-muted-foreground font-semibold">{name}</span>:{" "}
        <span className={typeof value === "number" || typeof value === "boolean" ? "text-indigo-500 font-bold" : "text-verified font-medium"}>
          {typeof value === "string" ? `"${value}"` : strVal}
        </span>
      </div>
    );
  }
}

export function ExtractionReviewView() {
  const { extractedDocs, metadata } = useDuelensData();
  const [selectedDoc, setSelectedDoc] = useState<string>("pitch_deck");
  const [searchTerm, setSearchTerm] = useState("");

  const docMapping = {
    pitch_deck: "Pitch Deck",
    cap_table: "Cap Table",
    mis: "Monthly MIS",
    financial_projections: "Financial Projections",
    historical_financial_statements: "Historical Financial Statements",
  };

  const documentKeys = Object.keys(docMapping);
  const currentJSON = (extractedDocs?.[selectedDoc] || {}) as Record<string, unknown>;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary">
            <FileSearch className="size-3.5" />
            Auto-Extraction Engine
          </span>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Extraction Review
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Cross-referencing auto-extracted metrics and parameters parsed from core documents.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="surface flex flex-col px-4 py-2.5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Analyzed Documents
            </span>
            <span className="text-xl font-extrabold text-primary tabular-nums">
              {metadata?.documents || 0} Total
            </span>
          </div>
          <div className="surface flex flex-col px-4 py-2.5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Total Artifacts
            </span>
            <span className="text-xl font-extrabold text-verified tabular-nums">
              {metadata?.artifacts || 0} Saved
            </span>
          </div>
        </div>
      </div>

      {/* Selector Tabs & Search */}
      <div className="surface p-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-1.5 bg-muted/40 p-1.5 rounded-2xl border border-border">
          {documentKeys.map((key) => {
            const active = selectedDoc === key;
            return (
              <button
                key={key}
                onClick={() => setSelectedDoc(key)}
                className={`rounded-xl px-3.5 py-1.5 text-xs font-bold transition-all ${
                  active
                    ? "bg-primary text-primary-foreground shadow-xs"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {docMapping[key as keyof typeof docMapping]}
              </button>
            );
          })}
        </div>

        <div className="relative shrink-0">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search metric keys or values..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="h-10 w-full sm:w-64 rounded-xl border border-border bg-background pl-9 pr-3 text-xs focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
        </div>
      </div>

      {/* JSON Viewer Console */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="surface p-6 font-mono border-t-4 border-t-primary min-h-[320px] bg-linear-to-b from-card to-muted/20"
      >
        <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
          <span className="text-xs font-bold text-muted-foreground uppercase flex items-center gap-1.5">
            <Sparkles className="size-3.5 text-primary" />
            Dynamic Extraction Data Console
          </span>
          <span className="text-[10px] font-bold text-primary bg-primary-soft px-2 py-0.5 rounded">
            JSON format
          </span>
        </div>

        {Object.keys(currentJSON).length > 0 ? (
          <div className="space-y-1 overflow-x-auto max-h-[600px] pr-2">
            {Object.keys(currentJSON).map((k) => (
              <JSONNode key={k} name={k} value={currentJSON[k]} searchTerm={searchTerm} />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 text-center text-muted-foreground">
            <FileSearch className="size-10 text-muted-foreground/35 mb-2.5 animate-pulse" />
            <p className="text-sm font-semibold">No extracted data found for this document slot.</p>
            <p className="text-xs text-muted-foreground mt-0.5">Please ensure the pipeline completed parsing successfully.</p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
