"use client";

import { motion } from "motion/react";
import {
  UploadCloud,
  FileText,
  FileSpreadsheet,
  PieChart,
  TrendingUp,
  BarChart3,
  CheckCircle2,
  X,
  ArrowRight,
  Sparkles,
  FileCode,
  Loader2,
  type LucideIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { MOCK_FILES, type Classified, type DocType } from "@/data/mock";
import { useDuelensData } from "@/context/DuelensDataContext";
import { apiFetch, getBaseApiUrl } from "@/lib/api";
import { toast } from "sonner";

type DocSlot = {
  id: string;
  name: string;
  description: string;
  formats: string[];
  sampleFile: string;
  icon: LucideIcon;
};

const DOC_SLOTS: DocSlot[] = [
  {
    id: "pitch-deck",
    name: "Pitch Deck",
    description: "Investor pitch presentation deck outlining vision & traction",
    formats: ["PDF", "PPTX"],
    sampleFile: "PitchDeck.pdf",
    icon: FileText,
  },
  {
    id: "financial-statements",
    name: "Historical Financial Statements",
    description: "Audited P&L statements, balance sheets & cash flow",
    formats: ["PDF", "XLSX"],
    sampleFile: "FinancialStatements.pdf",
    icon: BarChart3,
  },
  {
    id: "monthly-mis",
    name: "Monthly MIS",
    description: "Management information system reports & actuals",
    formats: ["XLSX", "CSV"],
    sampleFile: "MIS.xlsx",
    icon: FileSpreadsheet,
  },
  {
    id: "financial-projections",
    name: "Financial Projections",
    description: "Multi-year forecast model & unit economics",
    formats: ["XLSX", "CSV"],
    sampleFile: "FinancialProjection.xlsx",
    icon: TrendingUp,
  },
  {
    id: "cap-table",
    name: "Cap Table",
    description: "Shareholding structure, ESOP pool & equity ownership",
    formats: ["CSV", "XLSX", "PDF"],
    sampleFile: "CapTable.csv",
    icon: PieChart,
  },
];

export function UploadCard({
  files,
  setFiles,
  onContinue,
  onRowsClassified,
}: {
  files: string[];
  setFiles: (f: string[]) => void;
  onContinue: () => void;
  onRowsClassified: (rows: Classified[]) => void;
}) {
  const { companyId, setCompanyId, resetState } = useDuelensData();
  const [uploading, setUploading] = useState(false);
  const [uploadedFileObjects, setUploadedFileObjects] = useState<Record<string, File>>({});

  const [uploadedMap, setUploadedMap] = useState<Record<string, string>>(() => {
    const map: Record<string, string> = {};
    if (files.length > 0) {
      DOC_SLOTS.forEach((slot, i) => {
        if (files[i]) map[slot.id] = files[i];
      });
    }
    return map;
  });

  const handleUploadSlot = (slotId: string, file: File) => {
    setUploadedFileObjects(prev => ({ ...prev, [slotId]: file }));
    const updated = { ...uploadedMap, [slotId]: file.name };
    setUploadedMap(updated);
    setFiles(Object.values(updated));
  };

  const handleRemoveSlot = (slotId: string) => {
    const updated = { ...uploadedMap };
    delete updated[slotId];
    setUploadedMap(updated);
    setFiles(Object.values(updated));
    setUploadedFileObjects(prev => {
      const updatedObjs = { ...prev };
      delete updatedObjs[slotId];
      return updatedObjs;
    });
  };

  const loadAllSamples = () => {
    resetState();
    setCompanyId("zestful");
    const map: Record<string, string> = {};
    DOC_SLOTS.forEach((slot) => {
      map[slot.id] = slot.sampleFile;
    });
    setUploadedMap(map);
    setFiles(MOCK_FILES);
    setUploadedFileObjects({});
  };

  const handleContinue = async () => {
    setUploading(true);
    try {
      let activeCompanyId = companyId;
      const fileCount = Object.keys(uploadedFileObjects).length;

      // Handle custom files upload
      if (fileCount > 0) {
        if (activeCompanyId === "zestful") {
          const generatedId = `company_${Date.now()}`;
          activeCompanyId = generatedId;
          setCompanyId(generatedId);
        }

        const formData = new FormData();
        formData.append("company_id", activeCompanyId);
        Object.values(uploadedFileObjects).forEach((file) => {
          formData.append("files", file);
        });

        const API_BASE_URL = getBaseApiUrl();
        const uploadRes = await fetch(`${API_BASE_URL}/api/v1/parse/upload`, {
          method: "POST",
          body: formData,
        });

        if (!uploadRes.ok) {
          throw new Error("Failed to upload fundraising documents to backend.");
        }
      }

      // Re-trigger parse flow
      const parseRes = await apiFetch<{ files: Array<{ file_name: string; document_type: string; errors: string[] }> }>(`/api/v1/parse/${activeCompanyId}`, {
        method: "POST",
      });

      const docTypeMapping: Record<string, string> = {
        pitch_deck: "Pitch Deck",
        historical_financial_statements: "Historical Financial Statements",
        monthly_mis_report: "Monthly MIS",
        mis_report: "Monthly MIS",
        financial_projections: "Financial Projections",
        cap_table: "Cap Table",
      };

      const mappedRows: Classified[] = parseRes.files.map((fileObj) => ({
        file: fileObj.file_name,
        type: (docTypeMapping[fileObj.document_type] || "Unknown") as DocType,
        confidence: fileObj.errors.length === 0 ? 100 : 80,
        status: fileObj.errors.length === 0 ? "Verified" : "Error",
      }));

      onRowsClassified(mappedRows);
      onContinue();
    } catch (err: unknown) {
      console.error(err);
      const errMsg = err instanceof Error ? err.message : "Failed to parse/classify uploaded documents.";
      toast.error(errMsg);
    } finally {
      setUploading(false);
    }
  };

  const uploadedCount = Object.keys(uploadedMap).length;

  return (
    <section id="upload" className="mx-auto max-w-5xl px-5 py-12 md:py-16">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary">
          <Sparkles className="size-3.5" />
          Data-Room Intake Engine
        </span>
        <h2 className="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
          Upload Fundraising Documents
        </h2>
        <p className="mx-auto mt-2 max-w-xl text-sm text-muted-foreground">
          Upload each document into its designated slot below to enable cross-document financial consistency checking.
        </p>

        <div className="mt-4 flex items-center justify-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={loadAllSamples}
            disabled={uploading}
            className="rounded-full text-xs border-primary/30 text-primary hover:bg-primary-soft"
          >
            <Sparkles className="mr-1.5 size-3.5" />
            Use Sample Data-Room Documents
          </Button>
        </div>
      </motion.div>

      {/* 5 Cards Grid */}
      <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {DOC_SLOTS.map((slot, index) => {
          const Icon = slot.icon;
          const uploadedFile = uploadedMap[slot.id];
          const isUploaded = Boolean(uploadedFile);

          return (
            <motion.div
              key={slot.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.07 }}
              className={`surface relative flex flex-col justify-between p-6 transition-all ${
                isUploaded
                  ? "border-verified/40 bg-linear-to-b from-card to-verified-soft/20 shadow-sm"
                  : "hover:border-primary/40 hover:shadow-md"
              }`}
            >
              <div>
                {/* Top Badge & Icon */}
                <div className="flex items-start justify-between gap-3">
                  <span
                    className={`flex size-11 items-center justify-center rounded-2xl transition-colors ${
                      isUploaded
                        ? "bg-verified-soft text-verified"
                        : "bg-primary-soft text-primary"
                    }`}
                  >
                    {isUploaded ? (
                      <CheckCircle2 className="size-5" />
                    ) : (
                      <Icon className="size-5" />
                    )}
                  </span>

                  {/* Formats Badges */}
                  <div className="flex flex-wrap items-center gap-1">
                    {slot.formats.map((fmt) => (
                      <span
                        key={fmt}
                        className="rounded-md border border-border bg-muted/60 px-2 py-0.5 text-[10px] font-bold text-muted-foreground uppercase"
                      >
                        {fmt}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Title & Description */}
                <h3 className="mt-4 font-bold text-foreground text-base leading-snug">
                  {slot.name}
                </h3>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                  {slot.description}
                </p>
              </div>

              {/* Upload Drop Zone / State */}
              <div className="mt-6">
                {isUploaded ? (
                  <div className="flex items-center justify-between rounded-xl border border-verified/30 bg-card p-3 shadow-xs">
                    <div className="flex items-center gap-2.5 overflow-hidden">
                      <FileCode className="size-4 shrink-0 text-verified" />
                      <div className="overflow-hidden">
                        <p className="truncate text-xs font-bold text-foreground">
                          {uploadedFile}
                        </p>
                        <p className="text-[10px] font-semibold text-verified">
                          Uploaded & Verified
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => handleRemoveSlot(slot.id)}
                      disabled={uploading}
                      className="rounded-lg p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
                      title="Remove file"
                    >
                      <X className="size-4" />
                    </button>
                  </div>
                ) : (
                  <label className="group flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border bg-muted/30 px-4 py-3.5 text-center transition-colors hover:border-primary hover:bg-primary-soft/50">
                    <UploadCloud className="size-4 text-muted-foreground group-hover:text-primary" />
                    <span className="text-xs font-semibold text-muted-foreground group-hover:text-foreground">
                      Upload {slot.name}
                    </span>
                    <input
                      type="file"
                      className="hidden"
                      accept={slot.formats.map((f) => `.${f.toLowerCase()}`).join(",")}
                      onChange={(e) => {
                        const f = e.target.files?.[0];
                        if (f) handleUploadSlot(slot.id, f);
                      }}
                    />
                  </label>
                )}
              </div>
            </motion.div>
          );
        })}

        {/* Action Card to continue */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 5 * 0.07 }}
          className="surface flex flex-col justify-between p-6 bg-linear-to-br from-card via-card to-primary-soft/40 border-primary/30"
        >
          <div>
            <span className="text-[11px] font-extrabold uppercase tracking-widest text-primary">
              Status Summary
            </span>
            <h3 className="mt-2 text-2xl font-extrabold text-foreground">
              {uploadedCount} of 5 Ready
            </h3>
            <p className="mt-1 text-xs text-muted-foreground">
              {uploadedCount === 0
                ? "Upload document cards or load sample files to proceed."
                : uploadedCount < 5
                  ? "You can proceed with current files or add remaining document slots."
                  : "All 5 core data-room documents uploaded!"}
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-border">
            <Button
              onClick={handleContinue}
              disabled={uploadedCount === 0 || uploading}
              className="w-full h-11 rounded-xl shadow-[var(--shadow-glow)] text-xs font-bold"
            >
              {uploading ? (
                <>
                  <Loader2 className="mr-1.5 size-4 animate-spin" />
                  Parsing Documents...
                </>
              ) : (
                <>
                  Continue to Classification
                  <ArrowRight className="ml-1.5 size-4" />
                </>
              )}
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
