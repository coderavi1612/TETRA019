"use client";

import { motion, AnimatePresence } from "motion/react";
import {
  ShieldCheck,
  UploadCloud,
  FileSearch,
  Grid3X3,
  ShieldAlert,
  HelpCircle,
  Award,
  Clock,
  ChevronRight,
  Building2,
  Trash2,
  ArrowUpRight,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";

export type ViewTab =
  | "intake"
  | "extraction"
  | "matrix"
  | "exceptions"
  | "questions"
  | "readiness";

export interface UploadHistoryEntry {
  id: string;
  companyId: string;
  label: string;
  uploadedAt: string; // ISO string
  fileCount: number;
  status: "completed" | "processing" | "failed";
}

interface AppSidebarProps {
  currentTab: ViewTab;
  onTabChange: (tab: ViewTab) => void;
  history: UploadHistoryEntry[];
  onLoadHistory: (entry: UploadHistoryEntry) => void;
  onDeleteHistory: (id: string) => void;
  currentCompanyId: string;
}

const NAV_ITEMS: { id: ViewTab; label: string; icon: LucideIcon; description: string }[] = [
  { id: "intake",     label: "Upload & Intake",      icon: UploadCloud,  description: "Document ingestion" },
  { id: "extraction", label: "Extraction Review",    icon: FileSearch,   description: "AI fact extraction"  },
  { id: "matrix",     label: "Comparison Matrix",    icon: Grid3X3,      description: "Cross-doc analysis"  },
  { id: "exceptions", label: "Exceptions Dashboard", icon: ShieldAlert,  description: "Flagged issues"      },
  { id: "questions",  label: "Follow-up Questions",  icon: HelpCircle,   description: "Clarification items" },
  { id: "readiness",  label: "Readiness Summary",    icon: Award,        description: "Final audit score"   },
];

const STATUS_DOT: Record<UploadHistoryEntry["status"], string> = {
  completed:  "bg-emerald-400",
  processing: "bg-amber-400 animate-pulse",
  failed:     "bg-red-400",
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins  = Math.floor(diff / 60_000);
  const hours = Math.floor(diff / 3_600_000);
  const days  = Math.floor(diff / 86_400_000);
  if (mins  < 1)   return "Just now";
  if (mins  < 60)  return `${mins}m ago`;
  if (hours < 24)  return `${hours}h ago`;
  return `${days}d ago`;
}

export function AppSidebar({
  currentTab,
  onTabChange,
  history,
  onLoadHistory,
  onDeleteHistory,
  currentCompanyId,
}: AppSidebarProps) {
  return (
    <motion.aside
      initial={{ x: -280, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] }}
      className="
        fixed left-0 top-0 z-40 flex h-screen w-64 flex-col
        border-r border-border/60 bg-background/95 backdrop-blur-xl
        select-none overflow-hidden
      "
    >
      {/* ── Brand ─────────────────────────────────────────── */}
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-border/40">
        <Link href="/" className="flex items-center gap-2.5 group">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-[var(--shadow-glow)] transition-transform group-hover:scale-105">
            <ShieldCheck className="size-5" />
          </span>
          <div className="leading-none">
            <p className="font-display text-[15px] font-bold tracking-tight text-foreground">
              Duelens
            </p>
            <p className="mt-0.5 text-[9px] font-extrabold uppercase tracking-[0.12em] text-primary">
              Integrity Engine
            </p>
          </div>
        </Link>
      </div>

      {/* ── Navigation ────────────────────────────────────── */}
      <nav className="px-3 pt-4 pb-2">
        <p className="mb-2 px-2 text-[9px] font-extrabold uppercase tracking-[0.14em] text-muted-foreground/60">
          Modules
        </p>
        <ul className="space-y-0.5">
          {NAV_ITEMS.map((item) => {
            const Icon  = item.icon;
            const active = currentTab === item.id;
            return (
              <li key={item.id}>
                <button
                  onClick={() => onTabChange(item.id)}
                  className={`
                    group relative flex w-full items-center gap-3 rounded-xl px-3 py-2.5
                    text-left text-sm font-semibold transition-all duration-150 cursor-pointer
                    ${active
                      ? "bg-primary text-primary-foreground shadow-[var(--shadow-glow)]"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    }
                  `}
                >
                  <Icon className={`size-4 shrink-0 ${active ? "text-primary-foreground" : "text-muted-foreground group-hover:text-foreground"}`} />
                  <span className="flex-1 leading-none">{item.label}</span>
                  {active && (
                    <ChevronRight className="size-3.5 text-primary-foreground/70" />
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* ── Divider ───────────────────────────────────────── */}
      <div className="mx-5 my-2 h-px bg-border/40" />

      {/* ── Upload History ────────────────────────────────── */}
      <div className="flex flex-1 flex-col overflow-hidden px-3 pb-3">
        <div className="mb-2 flex items-center justify-between px-2">
          <p className="text-[9px] font-extrabold uppercase tracking-[0.14em] text-muted-foreground/60 flex items-center gap-1.5">
            <Clock className="size-3" />
            Upload History
          </p>
          {history.length > 0 && (
            <span className="rounded-full bg-muted px-1.5 py-0.5 text-[9px] font-bold text-muted-foreground">
              {history.length}
            </span>
          )}
        </div>

        <div className="flex-1 overflow-y-auto space-y-1 pr-0.5 overscroll-contain scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
          <AnimatePresence initial={false}>
            {history.length === 0 ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="rounded-xl border border-dashed border-border/50 px-3 py-5 text-center"
              >
                <Building2 className="mx-auto size-6 text-muted-foreground/30" />
                <p className="mt-2 text-[11px] font-medium text-muted-foreground/50">
                  No uploads yet
                </p>
                <p className="mt-0.5 text-[10px] text-muted-foreground/40">
                  Completed audits will appear here
                </p>
              </motion.div>
            ) : (
              history.map((entry, i) => {
                const isCurrent = entry.companyId === currentCompanyId;
                return (
                  <motion.div
                    key={entry.id}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -12, height: 0, marginBottom: 0 }}
                    transition={{ delay: i * 0.04 }}
                    className={`
                      group relative rounded-xl border px-3 py-2.5 transition-all duration-150
                      ${isCurrent
                        ? "border-primary/30 bg-primary-soft/60"
                        : "border-border/60 bg-card/60 hover:border-border hover:bg-muted/50 cursor-pointer"
                      }
                    `}
                    onClick={() => !isCurrent && onLoadHistory(entry)}
                  >
                    {/* Status dot + label */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className={`mt-0.5 size-1.5 shrink-0 rounded-full ${STATUS_DOT[entry.status]}`} />
                        <p className="truncate text-xs font-bold text-foreground leading-snug">
                          {entry.label}
                        </p>
                      </div>
                      <div className="flex shrink-0 items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        {!isCurrent && (
                          <button
                            title="Load this session"
                            onClick={(e) => { e.stopPropagation(); onLoadHistory(entry); }}
                            className="rounded-lg p-1 text-muted-foreground hover:text-primary hover:bg-primary-soft cursor-pointer"
                          >
                            <ArrowUpRight className="size-3" />
                          </button>
                        )}
                        <button
                          title="Delete"
                          onClick={(e) => { e.stopPropagation(); onDeleteHistory(entry.id); }}
                          className="rounded-lg p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50 cursor-pointer"
                        >
                          <Trash2 className="size-3" />
                        </button>
                      </div>
                    </div>

                    {/* Meta */}
                    <div className="mt-1.5 flex items-center justify-between">
                      <span className="text-[10px] text-muted-foreground font-medium">
                        {entry.fileCount} doc{entry.fileCount !== 1 ? "s" : ""}
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        {timeAgo(entry.uploadedAt)}
                      </span>
                    </div>

                    {isCurrent && (
                      <span className="mt-1.5 inline-flex items-center gap-1 text-[9px] font-extrabold uppercase tracking-wider text-primary">
                        <span className="size-1 rounded-full bg-primary" />
                        Active session
                      </span>
                    )}
                  </motion.div>
                );
              })
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* ── Footer ────────────────────────────────────────── */}
      <div className="border-t border-border/40 px-5 py-3">
        <Link
          href="/"
          className="flex items-center gap-1.5 text-[11px] font-semibold text-muted-foreground transition-colors hover:text-foreground"
        >
          <svg className="size-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
          Back to landing
        </Link>
      </div>
    </motion.aside>
  );
}
