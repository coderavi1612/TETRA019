"use client";

import { useCallback, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { AppNavbar, type ViewTab } from "@/components/duelens/AppNavbar";
import { UploadCard } from "@/components/duelens/UploadCard";
import { ClassificationTable } from "@/components/duelens/ClassificationTable";
import { ClassificationModal } from "@/components/duelens/ClassificationModal";
import { ProcessingCard } from "@/components/duelens/ProcessingCard";
import { Footer } from "@/components/duelens/Footer";
import { Toaster } from "@/components/ui/sonner";
import { Classified } from "@/data/mock";
import { DuelensDataProvider, useDuelensData } from "@/context/DuelensDataContext";

// Views
import { ExtractionReviewView } from "@/components/duelens/views/ExtractionReviewView";
import { ComparisonMatrixView } from "@/components/duelens/views/ComparisonMatrixView";
import { ExceptionsDashboardView } from "@/components/duelens/views/ExceptionsDashboardView";
import { IssueDetailView } from "@/components/duelens/views/IssueDetailView";
import { FollowUpQuestionsView } from "@/components/duelens/views/FollowUpQuestionsView";
import { ReadinessSummaryView } from "@/components/duelens/views/ReadinessSummaryView";

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
  const [selectedIssueId, setSelectedIssueId] = useState<string>("");

  const { loadAllData, companyId } = useDuelensData();

  const onDoneProcessing = useCallback(async () => {
    // Re-fetch all backend generated files once pipeline processing finishes
    await loadAllData(companyId);
    setCurrentTab("extraction");
  }, [companyId, loadAllData]);

  const handleSelectIssue = (issueId: string) => {
    setSelectedIssueId(issueId);
    setCurrentTab("issue");
  };

  return (
    <main className="min-h-screen bg-background text-foreground flex flex-col">
      <AppNavbar currentTab={currentTab} onTabChange={setCurrentTab} />

      <div className="mx-auto w-full max-w-7xl flex-1 px-5 py-8">
        <AnimatePresence mode="wait">
          {/* Tab 1: Upload & Intake */}
          {currentTab === "intake" && (
            <motion.div
              key="tab-intake"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              className="space-y-8"
            >
              {/* Step Bar for Intake */}
              <div className="flex items-center gap-2 overflow-x-auto rounded-2xl border border-border bg-muted/40 p-2">
                {[
                  { id: "upload", label: "1. Document Intake" },
                  { id: "classify", label: "2. Document Classification" },
                  { id: "processing", label: "3. Deep Integrity Audit" },
                ].map((s) => {
                  const active = intakeStage === s.id;
                  return (
                    <button
                      key={s.id}
                      onClick={() => setIntakeStage(s.id as IntakeStage)}
                      className={`rounded-xl px-4 py-2 text-xs font-bold transition-all ${
                        active
                          ? "bg-primary text-primary-foreground shadow-xs"
                          : "text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      {s.label}
                    </button>
                  );
                })}
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
              <ComparisonMatrixView onSelectIssue={handleSelectIssue} />
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
              <ExceptionsDashboardView onSelectIssue={handleSelectIssue} />
            </motion.div>
          )}

          {/* Tab 5: Issue Detail */}
          {currentTab === "issue" && (
            <motion.div
              key="tab-issue"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <IssueDetailView
                issueId={selectedIssueId}
                onBack={() => setCurrentTab("exceptions")}
              />
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
  );
}
