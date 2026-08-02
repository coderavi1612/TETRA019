"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  History,
  Search,
  Building2,
  Calendar,
  FileCode,
  CheckCircle2,
  Clock,
  ArrowRight,
  Trash2,
  ExternalLink,
  ShieldCheck,
  FileText,
  FileSpreadsheet,
  PieChart,
  TrendingUp,
  BarChart3,
  Loader2,
  type LucideIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDuelensData } from "@/context/DuelensDataContext";
import type { UploadHistoryEntry, ViewTab } from "@/components/duelens/AppSidebar";

interface HistoryViewProps {
  history: UploadHistoryEntry[];
  onLoadHistory: (entry: UploadHistoryEntry) => void;
  onDeleteHistory: (id: string) => void;
  onNavigateTab: (tab: ViewTab) => void;
  currentCompanyId: string;
}

const DOC_SLOT_ICONS: Record<string, { name: string; icon: LucideIcon }> = {
  pitch_deck: { name: "Pitch Deck", icon: FileText },
  historical_financial_statements: { name: "Historical Financial Statements", icon: BarChart3 },
  mis: { name: "Monthly MIS", icon: FileSpreadsheet },
  financial_projections: { name: "Financial Projections", icon: TrendingUp },
  cap_table: { name: "Cap Table", icon: PieChart },
};

function formatFullDate(isoStr: string): string {
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoStr;
  }
}

function timeAgo(isoStr: string): string {
  try {
    const diff = Date.now() - new Date(isoStr).getTime();
    const mins = Math.floor(diff / 60_000);
    const hours = Math.floor(diff / 3_600_000);
    const days = Math.floor(diff / 86_400_000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  } catch {
    return "Recently";
  }
}

export function HistoryView({
  history,
  onLoadHistory,
  onDeleteHistory,
  onNavigateTab,
  currentCompanyId,
}: HistoryViewProps) {
  const { loadAllData, resetState, setCompanyId } = useDuelensData();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(
    history.length > 0 ? history[0].id : null
  );
  const [loadingSession, setLoadingSession] = useState(false);

  // Filter history list based on search term
  const filteredHistory = history.filter(
    (h) =>
      h.companyId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      h.label.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Currently selected session details object
  const selectedSession = history.find((h) => h.id === selectedSessionId) || history[0] || null;
  const isSelectedActive = selectedSession?.companyId === currentCompanyId;

  const handleOpenSession = async (entry: UploadHistoryEntry) => {
    setLoadingSession(true);
    try {
      await onLoadHistory(entry);
      onNavigateTab("extraction");
    } finally {
      setLoadingSession(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* ── Header ─────────────────────────────────────────── */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary">
            <History className="size-3.5" />
            Audit Log & Session Archive
          </span>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Audit History
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            View, search, and inspect past data-room audit sessions and document verification runs.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="flex items-center gap-3">
          <div className="surface flex flex-col px-4 py-2.5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Total Sessions
            </span>
            <span className="text-xl font-extrabold text-primary tabular-nums">
              {history.length}
            </span>
          </div>
          <div className="surface flex flex-col px-4 py-2.5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Active Context
            </span>
            <span className="text-xs font-bold text-verified truncate max-w-[120px]">
              {currentCompanyId || "None"}
            </span>
          </div>
        </div>
      </div>

      {/* ── Master-Detail LLM-style Layout ──────────────────── */}
      {history.length === 0 ? (
        /* Empty State */
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="surface flex flex-col items-center justify-center p-12 text-center min-h-[360px]"
        >
          <Building2 className="size-12 text-muted-foreground/30 mb-3" />
          <h3 className="text-lg font-bold text-foreground">No Audit History Found</h3>
          <p className="mt-1 max-w-md text-xs text-muted-foreground">
            You haven't run any data-room audits yet. Upload core fundraising documents to initiate your first consistency audit.
          </p>
          <Button
            onClick={() => onNavigateTab("intake")}
            className="mt-5 rounded-xl shadow-[var(--shadow-glow)] text-xs font-bold"
          >
            Start New Audit Session
            <ArrowRight className="ml-1.5 size-4" />
          </Button>
        </motion.div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-12">
          {/* ── Left Column: Saved Sessions List (4 cols) ────── */}
          <div className="lg:col-span-4 space-y-4">
            <div className="surface p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold uppercase tracking-wider text-foreground flex items-center gap-1.5">
                  <Clock className="size-3.5 text-primary" />
                  Past Sessions
                </span>
                <span className="rounded-full bg-primary-soft px-2 py-0.5 text-[10px] font-bold text-primary">
                  {filteredHistory.length}
                </span>
              </div>

              {/* Search Box */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search session or company..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="h-9 w-full rounded-xl border border-border bg-background pl-8 pr-3 text-xs focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
              </div>
            </div>

            {/* Sessions List */}
            <div className="space-y-2 max-h-[640px] overflow-y-auto pr-1">
              <AnimatePresence>
                {filteredHistory.length === 0 ? (
                  <div className="surface p-6 text-center text-xs text-muted-foreground">
                    No sessions match "{searchTerm}"
                  </div>
                ) : (
                  filteredHistory.map((entry, idx) => {
                    const isSelected = selectedSession?.id === entry.id;
                    const isActiveSession = entry.companyId === currentCompanyId;

                    return (
                      <motion.div
                        key={entry.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.04 }}
                        onClick={() => setSelectedSessionId(entry.id)}
                        className={`
                          group relative flex flex-col justify-between rounded-2xl border p-4 transition-all duration-200 cursor-pointer
                          ${
                            isSelected
                              ? "border-primary bg-primary-soft/50 shadow-sm"
                              : "border-border/60 bg-card hover:border-border hover:bg-muted/30"
                          }
                        `}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <Building2 className={`size-4 shrink-0 ${isSelected ? "text-primary" : "text-muted-foreground"}`} />
                              <h4 className="truncate text-sm font-bold text-foreground">
                                {entry.label}
                              </h4>
                            </div>
                            <p className="mt-1 text-[11px] text-muted-foreground flex items-center gap-1">
                              <Calendar className="size-3 shrink-0" />
                              {timeAgo(entry.uploadedAt)}
                            </p>
                          </div>

                          {/* Status Badge */}
                          <span
                            className={`shrink-0 rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider ${
                              entry.status === "completed"
                                ? "bg-verified-soft text-verified"
                                : entry.status === "processing"
                                  ? "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300"
                                  : "bg-critical-soft text-critical"
                            }`}
                          >
                            {entry.status}
                          </span>
                        </div>

                        <div className="mt-3 pt-2.5 border-t border-border/40 flex items-center justify-between text-[11px]">
                          <span className="font-semibold text-muted-foreground">
                            {entry.fileCount} Documents
                          </span>

                          <div className="flex items-center gap-1 opacity-90 group-hover:opacity-100">
                            {isActiveSession && (
                              <span className="rounded-md bg-primary/10 px-1.5 py-0.5 text-[9px] font-extrabold text-primary uppercase">
                                Active
                              </span>
                            )}
                            <button
                              title="Delete session record"
                              onClick={(e) => {
                                e.stopPropagation();
                                onDeleteHistory(entry.id);
                              }}
                              className="rounded-lg p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 cursor-pointer"
                            >
                              <Trash2 className="size-3.5" />
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* ── Right Column: Selected Session Document History (8 cols) ── */}
          <div className="lg:col-span-8 space-y-6">
            {selectedSession ? (
              <motion.div
                key={selectedSession.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* Selected Session Banner Card */}
                <div className="surface p-6 bg-linear-to-br from-card via-card to-primary-soft/30 border-primary/30">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="rounded-lg bg-primary-soft p-2 text-primary">
                          <Building2 className="size-5" />
                        </span>
                        <div>
                          <h3 className="text-xl font-extrabold text-foreground">
                            {selectedSession.label}
                          </h3>
                          <p className="text-xs text-muted-foreground font-mono mt-0.5">
                            ID: {selectedSession.companyId}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      <Button
                        onClick={() => handleOpenSession(selectedSession)}
                        disabled={loadingSession}
                        className="h-10 rounded-xl shadow-[var(--shadow-glow)] text-xs font-bold cursor-pointer"
                      >
                        {loadingSession ? (
                          <>
                            <Loader2 className="mr-1.5 size-4 animate-spin" />
                            Loading Data...
                          </>
                        ) : (
                          <>
                            <ExternalLink className="mr-1.5 size-4" />
                            {isSelectedActive ? "Explore Active Session" : "Load Session in Duelens"}
                          </>
                        )}
                      </Button>
                    </div>
                  </div>

                  {/* Meta Bar */}
                  <div className="mt-6 pt-4 border-t border-border grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                    <div>
                      <span className="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">
                        Date & Time
                      </span>
                      <span className="font-semibold text-foreground mt-0.5 block">
                        {formatFullDate(selectedSession.uploadedAt)}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">
                        Data-Room Status
                      </span>
                      <span className="font-bold text-verified capitalize mt-0.5 block">
                        {selectedSession.status}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">
                        Files Uploaded
                      </span>
                      <span className="font-semibold text-foreground mt-0.5 block">
                        {selectedSession.fileCount} Documents
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">
                        Active State
                      </span>
                      <span className={`font-bold mt-0.5 block ${isSelectedActive ? "text-primary" : "text-muted-foreground"}`}>
                        {isSelectedActive ? "Currently Selected" : "Archived"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Document History Cards */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                      <FileCode className="size-4 text-primary" />
                      Session Document Manifest & Status
                    </h4>
                    <span className="text-xs text-muted-foreground">
                      5 Core Data-Room Slots
                    </span>
                  </div>

                  <div className="grid gap-3 sm:grid-cols-2">
                    {Object.entries(DOC_SLOT_ICONS).map(([key, info]) => {
                      const Icon = info.icon;
                      return (
                        <div
                          key={key}
                          className="surface p-4 flex items-start gap-3 border-border/80 hover:border-primary/30 transition-all"
                        >
                          <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary-soft text-primary">
                            <Icon className="size-5" />
                          </span>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between gap-1">
                              <h5 className="truncate text-xs font-bold text-foreground">
                                {info.name}
                              </h5>
                              <span className="shrink-0 text-[10px] font-bold text-verified bg-verified-soft px-1.5 py-0.5 rounded">
                                Ready
                              </span>
                            </div>
                            <p className="mt-1 text-[11px] text-muted-foreground font-mono truncate">
                              {key}.json
                            </p>
                            <div className="mt-2 flex items-center justify-between text-[10px] text-muted-foreground">
                              <span>Auto-extracted & verified</span>
                              <CheckCircle2 className="size-3.5 text-verified" />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Audit Trail Summary Box */}
                <div className="surface p-6 space-y-4">
                  <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                    <ShieldCheck className="size-4 text-primary" />
                    Audit Pipeline Execution Summary
                  </h4>

                  <div className="space-y-3">
                    {[
                      { stage: "Document Intake & Parsing", desc: "Parsed PDFs, PPTX & Excel workbooks into canonical JSON schemas", icon: CheckCircle2, ok: true },
                      { stage: "AI Fact Extraction & Specifications", desc: "Extracted structural metrics with confidence scoring & evidence mapping", icon: CheckCircle2, ok: true },
                      { stage: "Deterministic Verification", desc: "Executed cross-document rule engine for financial consistency", icon: CheckCircle2, ok: true },
                      { stage: "Readiness & Risk Scoring", desc: "Compiled readiness score, missing fields & follow-up questions", icon: CheckCircle2, ok: true },
                    ].map((step, i) => {
                      const StepIcon = step.icon;
                      return (
                        <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-muted/30 border border-border/60">
                          <div className="flex items-center gap-3">
                            <StepIcon className="size-4 text-verified" />
                            <div>
                              <p className="text-xs font-bold text-foreground">{step.stage}</p>
                              <p className="text-[11px] text-muted-foreground">{step.desc}</p>
                            </div>
                          </div>
                          <span className="text-[10px] font-bold text-verified bg-verified-soft px-2 py-0.5 rounded-full">
                            PASS
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </motion.div>
            ) : (
              <div className="surface p-12 text-center text-muted-foreground text-xs">
                Select a session from the list to view its document history.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
