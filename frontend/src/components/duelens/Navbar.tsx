import { motion } from "motion/react";
import { ShieldCheck, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function Navbar() {
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

        <div className="hidden items-center gap-8 md:flex">
          {[
            { label: "Features", href: "#features" },
            { label: "Workflow", href: "#workflow" },
            { label: "About", href: "#about" },
          ].map((l) => (
            <a
              key={l.label}
              href={l.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {l.label}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <Button asChild className="rounded-full px-5">
            <Link href="/app">Get Started</Link>
          </Button>
          <button className="rounded-lg p-2 text-muted-foreground md:hidden" aria-label="Menu">
            <Menu className="size-5" />
          </button>
        </div>
      </nav>
    </motion.header>
  );
}
