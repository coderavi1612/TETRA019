"use client";

import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { AppSidebar, type ViewTab, type UploadHistoryEntry } from "@/components/duelens/AppSidebar";
import { UploadCard } from "@/components/duelens/UploadCard";
import { ClassificationTable } from "@/components/duelens/ClassificationTable";
import { ClassificationModal } from "@/components/duelens/ClassificationModal";
import { ProcessingCard } from "@/components/duelens/ProcessingCard";
import { Footer } from "@/components/duelens/Footer";
import { Toaster } from "@/components/ui/sonner";
import { Classified } from "@/data/mock";
import { DuelensDataProvider, useDuelensData } from "@/context/DuelensDataContext";
import { listAllCompanies } from "@/lib/api";

// Views
import { ExtractionReviewView } from "@/components/duelens/views/ExtractionReviewView";
import { ComparisonMatrixView } from "@/components/duelens/views/ComparisonMatrixView";
import { ExceptionsDashboardView } from "@/components/duelens/views/ExceptionsDashboardView";
import { FollowUpQuestionsView } from "@/components/duelens/views/FollowUpQuestionsView";
import { ReadinessSummaryView } from "@/components/duelens/views/ReadinessSummaryView";
import { HistoryView } from "@/components/duelens/views/HistoryView";

type IntakeStage = "upload" | "classify" | "processing";

export function AppPage() {
  return (
    <DuelensDataProvider>
      <AppPageContent />
    </DuelensDataProvider>
  );
}

function AppPageContent() {
  const [currentTab, setCurrentTab] = useState<ViewTab>("intake");
  const [intakeStage, setIntakeStage] = useState<IntakeStage>("upload");
  const [files, setFiles] = useState<string[]>([]);
  const [rows, setRows] = useState<Classified[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [history, setHistory] = useState<UploadHistoryEntry[]>([]);

  const { loadAllData, companyId, setCompanyId, resetState } = useDuelensData();

  // Load history from database
  const loadGlobalHistory = useCallback(async () => {
    try {
      const dbCompanies = await listAllCompanies();
      const list = Array.isArray(dbCompanies) ? dbCompanies : [];
      const mapped: UploadHistoryEntry[] = list.map((c) => ({
        id: c.job_id && c.job_id !== "none" ? c.job_id : c.company_id,
        companyId: c.company_id,
        label: c.company_id,
        uploadedAt: c.updated_at || new Date().toISOString(),
        fileCount: c.file_count || 0,
        status: (c.status?.toLowerCase() === "running" || c.status?.toLowerCase() === "accepted" ? "processing" : c.status?.toLowerCase() === "failed" ? "failed" : "completed") as "completed" | "processing" | "failed",
      }));
      setHistory(mapped);
    } catch (err) {
      console.error("Failed to load global history:", err);
    }
  }, []);

  // Load history on mount
  useEffect(() => {
    loadGlobalHistory();
  }, [loadGlobalHistory]);

  const onDoneProcessing = useCallback(async () => {
    // Re-fetch all backend generated files once pipeline processing finishes
    await loadAllData(companyId);

    // Refresh history list from DB
    await loadGlobalHistory();

    setCurrentTab("extraction");
  }, [companyId, loadAllData, loadGlobalHistory]);

  const handleLoadHistory = useCallback(
    async (entry: UploadHistoryEntry) => {
      resetState();
      setCompanyId(entry.companyId);
      await loadAllData(entry.companyId);
      setCurrentTab("extraction");
    },
    [loadAllData, resetState, setCompanyId]
  );

  const handleDeleteHistory = useCallback((id: string) => {
    setHistory((prev) => prev.filter((h) => h.id !== id));
  }, []);

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* ── Sidebar ───────────────────────────────────────── */}
      <AppSidebar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        history={history}
        onLoadHistory={handleLoadHistory}
        onDeleteHistory={handleDeleteHistory}
        currentCompanyId={companyId}
      />

      {/* ── Main content (offset by sidebar width = 256px) ── */}
      <main className="flex flex-1 flex-col pl-64">

      <div className="flex-1 px-6 py-6">
        <AnimatePresence mode="wait">
          {/* Tab 1: Upload & Intake */}
          {currentTab === "intake" && (
            <motion.div
              key="tab-intake"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              className="space-y-4"
            >
              {/* Pipeline Stepper */}
              <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-sm p-5">
                <div className="flex items-center justify-between">
                  {[
                    { id: "upload", num: 1, label: "Document Intake", desc: "Upload fundraising files" },
                    { id: "classify", num: 2, label: "Classification", desc: "Verify document types" },
                    { id: "processing", num: 3, label: "Deep Integrity Audit", desc: "AI-powered analysis" },
                  ].map((s, idx) => {
                    const stages = ["upload", "classify", "processing"];
                    const currentIdx = stages.indexOf(intakeStage);
                    const stepIdx = stages.indexOf(s.id);
                    const isActive = intakeStage === s.id;
                    const isCompleted = stepIdx < currentIdx;

                    return (
                      <div key={s.id} className="flex items-center flex-1 last:flex-initial">
                        {/* Step circle + label */}
                        <button
                          onClick={() => setIntakeStage(s.id as IntakeStage)}
                          className="flex items-center gap-3 group"
                        >
                          <span
                            className={`flex size-10 shrink-0 items-center justify-center rounded-full text-sm font-bold transition-all duration-300 ${
                              isActive
                                ? "bg-primary text-primary-foreground shadow-[var(--shadow-glow)] scale-110"
                                : isCompleted
                                  ? "bg-primary/15 text-primary ring-2 ring-primary/30"
                                  : "bg-muted text-muted-foreground"
                            }`}
                          >
                            {isCompleted ? (
                              <svg className="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                              </svg>
                            ) : (
                              s.num
                            )}
                          </span>
                          <div className="text-left hidden sm:block">
                            <p
                              className={`text-xs font-bold transition-colors ${
                                isActive
                                  ? "text-foreground"
                                  : isCompleted
                                    ? "text-primary"
                                    : "text-muted-foreground"
                              }`}
                            >
                              {s.label}
                            </p>
                            <p className="text-[10px] text-muted-foreground mt-0.5">
                              {isCompleted ? "Completed" : s.desc}
                            </p>
                          </div>
                        </button>

                        {/* Connector line */}
                        {idx < 2 && (
                          <div className="flex-1 mx-4 hidden sm:block">
                            <div className="h-[2px] rounded-full bg-border relative overflow-hidden">
                              <div
                                className={`absolute inset-y-0 left-0 rounded-full transition-all duration-500 ease-out ${
                                  isCompleted
                                    ? "w-full bg-primary/50"
                                    : isActive
                                      ? "w-1/2 bg-primary/30"
                                      : "w-0"
                                }`}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {intakeStage === "upload" && (
                <UploadCard
                  files={files}
                  setFiles={(f) => {
                    setFiles(f);
                    if (f.length === 0) setIntakeStage("upload");
                  }}
                  onContinue={() => setIntakeStage("classify")}
                  onRowsClassified={setRows}
                />
              )}

              {intakeStage === "classify" && (
                <ClassificationTable
                  rows={rows}
                  onContinue={() => setIntakeStage("processing")}
                  onEdit={() => setModalOpen(true)}
                />
              )}

              {intakeStage === "processing" && (
                <ProcessingCard onDone={onDoneProcessing} />
              )}
            </motion.div>
          )}

          {/* Tab 2: Extraction Review */}
          {currentTab === "extraction" && (
            <motion.div
              key="tab-extraction"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <ExtractionReviewView />
            </motion.div>
          )}

          {/* Tab 3: Comparison Matrix */}
          {currentTab === "matrix" && (
            <motion.div
              key="tab-matrix"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <ComparisonMatrixView />
            </motion.div>
          )}

          {/* Tab 4: Exceptions Dashboard */}
          {currentTab === "exceptions" && (
            <motion.div
              key="tab-exceptions"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <ExceptionsDashboardView />
            </motion.div>
          )}



          {/* Tab 6: Follow-up Questions */}
          {currentTab === "questions" && (
            <motion.div
              key="tab-questions"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <FollowUpQuestionsView />
            </motion.div>
          )}

          {/* Tab 7: Readiness Summary */}
          {currentTab === "readiness" && (
            <motion.div
              key="tab-readiness"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <ReadinessSummaryView />
            </motion.div>
          )}

          {/* Tab 8: Audit History */}
          {currentTab === "history" && (
            <motion.div
              key="tab-history"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <HistoryView
                history={history}
                onLoadHistory={handleLoadHistory}
                onDeleteHistory={handleDeleteHistory}
                onNavigateTab={setCurrentTab}
                currentCompanyId={companyId}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

        <ClassificationModal
          open={modalOpen}
          onOpenChange={setModalOpen}
          rows={rows}
          onSave={setRows}
        />

        <Footer />
        <Toaster />
      </main>
    </div>
  );
}
