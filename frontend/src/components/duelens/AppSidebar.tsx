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
  | "readiness"
  | "history";

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
  { id: "history",    label: "Audit History",        icon: Clock,        description: "Past audit sessions" },
];

export function AppSidebar({
  currentTab,
  onTabChange,
  history,
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
        select-none overflow-hidden justify-between
      "
    >
      <div>
        {/* ── Brand ─────────────────────────────────────────── */}
        <div className="flex items-center gap-2.5 px-5 py-5 border-b border-border/40">
          <Link href="/" className="flex items-center gap-2.5 group">
            <img
              src="/DueLens.png"
              alt="DueLens Logo"
              className="size-9 rounded-xl object-contain shadow-[var(--shadow-glow)] transition-transform group-hover:scale-105"
            />
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
                    {item.id === "history" && history.length > 0 && (
                      <span className={`rounded-full px-1.5 py-0.5 text-[9px] font-bold ${active ? "bg-primary-foreground/20 text-primary-foreground" : "bg-muted text-muted-foreground"}`}>
                        {history.length}
                      </span>
                    )}
                    {active && item.id !== "history" && (
                      <ChevronRight className="size-3.5 text-primary-foreground/70" />
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>

      {/* ── Bottom Section & Active Context ───────────────────── */}
      <div className="p-3 border-t border-border/40 space-y-2">
        {currentCompanyId && (
          <button
            onClick={() => onTabChange("history")}
            className="w-full flex items-center justify-between p-2.5 rounded-xl border border-primary/20 bg-primary-soft/40 hover:bg-primary-soft/80 transition-all text-left group cursor-pointer"
          >
            <div className="flex items-center gap-2 min-w-0">
              <Building2 className="size-4 text-primary shrink-0" />
              <div className="min-w-0">
                <p className="text-[10px] font-extrabold uppercase tracking-wider text-primary">
                  Active Session
                </p>
                <p className="text-xs font-bold text-foreground truncate">
                  {currentCompanyId}
                </p>
              </div>
            </div>
            <ArrowUpRight className="size-3.5 text-primary opacity-70 group-hover:opacity-100 transition-opacity shrink-0" />
          </button>
        )}

        <Link
          href="/"
          className="flex items-center gap-1.5 px-2 py-1.5 text-[11px] font-semibold text-muted-foreground transition-colors hover:text-foreground"
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

