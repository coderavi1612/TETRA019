"use client";

import { Navbar } from "@/components/duelens/Navbar";
import { Hero } from "@/components/duelens/Hero";
import { WorkflowSection } from "@/components/duelens/WorkflowSection";
import { Footer } from "@/components/duelens/Footer";

export function HomePage() {
  return (
    <main>
      <Navbar />
      <Hero />
      <WorkflowSection />
      <Footer />
    </main>
  );
}
