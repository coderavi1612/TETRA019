"use client";

import { motion } from "motion/react";
import {
  ShieldCheck,
  ArrowLeft,
  UploadCloud,
  FileSearch,
  Grid,
  ShieldAlert,
  Search,
  HelpCircle,
  Award,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";

export type ViewTab =
  | "intake"
  | "extraction"
  | "matrix"
  | "exceptions"
  | "issue"
  | "questions"
  | "readiness";

export function AppNavbar({
  currentTab,
  onTabChange,
}: {
  currentTab: ViewTab;
  onTabChange: (tab: ViewTab) => void;
}) {
  const tabs: { id: ViewTab; label: string; icon: LucideIcon }[] = [
    { id: "intake", label: "Upload & Intake", icon: UploadCloud },
    { id: "extraction", label: "Extraction Review", icon: FileSearch },
    { id: "matrix", label: "Comparison Matrix", icon: Grid },
    { id: "exceptions", label: "Exceptions Dashboard", icon: ShieldAlert },
    { id: "issue", label: "Issue Detail", icon: Search },
    { id: "questions", label: "Follow-up Questions", icon: HelpCircle },
    { id: "readiness", label: "Readiness Summary", icon: Award },
  ];

  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="sticky top-0 z-40 border-b border-border/80 bg-background/85 backdrop-blur-xl"
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex size-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-[var(--shadow-glow)]">
            <ShieldCheck className="size-5" />
          </span>
          <div>
            <span className="font-display text-lg font-bold tracking-tight text-foreground">
              Duelens
            </span>
            <span className="ml-2 rounded-full bg-primary-soft px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-widest text-primary">
              Integrity Engine
            </span>
          </div>
        </Link>

        {/* Back to Home Link */}
        <Link
          href="/"
          className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="size-3.5" />
          Back to landing
        </Link>
      </div>

      {/* Primary Module Navigation Tabs */}
      <div className="border-t border-border/50 bg-muted/30">
        <div className="mx-auto flex max-w-7xl items-center gap-1 overflow-x-auto px-5 py-2 no-scrollbar">
          {tabs.map((t) => {
            const Icon = t.icon;
            const active = currentTab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => onTabChange(t.id)}
                className={`flex shrink-0 items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-bold transition-all ${
                  active
                    ? "bg-primary text-primary-foreground shadow-xs"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <Icon className="size-3.5" />
                {t.label}
              </button>
            );
          })}
        </div>
      </div>
    </motion.header>
  );
}
