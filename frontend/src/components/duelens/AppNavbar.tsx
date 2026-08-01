"use client";

import { motion } from "motion/react";
import { ShieldCheck, ArrowLeft } from "lucide-react";
import Link from "next/link";

export function AppNavbar() {
  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="sticky top-0 z-40 border-b border-border/70 bg-background/80 backdrop-blur-xl"
    >
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex size-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-[var(--shadow-glow)]">
            <ShieldCheck className="size-5" />
          </span>
          <span className="font-display text-lg font-bold tracking-tight">Duelens</span>
        </Link>

        <Link
          href="/"
          className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="size-4" />
          Back to home
        </Link>
      </nav>
    </motion.header>
  );
}
