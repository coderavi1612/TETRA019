import { motion, AnimatePresence } from "motion/react";
import { UploadCloud, FileText, FileSpreadsheet, X, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRef, useState } from "react";
import { MOCK_FILES } from "@/data/mock";

function iconFor(name: string) {
  return name.endsWith(".xlsx") || name.endsWith(".csv") ? FileSpreadsheet : FileText;
}

export function UploadCard({
  files,
  setFiles,
  onContinue,
}: {
  files: string[];
  setFiles: (f: string[]) => void;
  onContinue: () => void;
}) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const select = (picked?: FileList | null) => {
    const names = picked && picked.length ? Array.from(picked).map((f) => f.name) : MOCK_FILES;
    setFiles(names);
  };

  return (
    <section id="upload" className="mx-auto max-w-4xl px-5 py-20 md:py-24">
      <motion.div
        initial={{ opacity: 0, y: 28 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ duration: 0.6 }}
        className="text-center"
      >
        <p className="text-xs font-semibold tracking-[0.18em] text-primary uppercase">Step 01</p>
        <h2 className="mt-3 text-3xl font-bold md:text-4xl">Upload fundraising documents</h2>
        <p className="mx-auto mt-3 max-w-xl text-muted-foreground">
          Add the full data-room set. Files stay on your device in this demo — nothing is uploaded.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 28 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="surface mt-10 p-6 md:p-10"
      >
        <div
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            select(e.dataTransfer.files);
          }}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-14 text-center transition-colors ${
            dragging ? "border-primary bg-primary-soft" : "border-border bg-muted/50"
          }`}
        >
          <motion.span
            animate={{ y: dragging ? -4 : 0 }}
            className="flex size-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-[var(--shadow-glow)]"
          >
            <UploadCloud className="size-6" />
          </motion.span>
          <p className="mt-5 text-base font-semibold">Drag & drop your documents here</p>
          <p className="mt-1 text-sm text-muted-foreground">or click to browse your files</p>
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            {["PDF", "PPTX", "DOCX", "CSV", "XLSX"].map((f) => (
              <span
                key={f}
                className="rounded-full border border-border bg-card px-3 py-1 text-[11px] font-semibold text-muted-foreground"
              >
                {f}
              </span>
            ))}
          </div>
          <input
            ref={inputRef}
            type="file"
            multiple
            className="hidden"
            accept=".pdf,.pptx,.docx,.csv,.xlsx"
            onChange={(e) => select(e.target.files)}
          />
        </div>

        <div className="mt-4 text-center">
          <button
            onClick={() => setFiles(MOCK_FILES)}
            className="text-xs font-semibold text-primary hover:underline"
          >
            Use sample data-room documents
          </button>
        </div>


        <AnimatePresence>
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-7 flex items-center justify-between">
                <p className="text-sm font-semibold">{files.length} Files Selected</p>
                <button
                  onClick={() => setFiles([])}
                  className="text-xs font-medium text-muted-foreground hover:text-foreground"
                >
                  Clear all
                </button>
              </div>
              <ul className="mt-3 space-y-2">
                {files.map((name, i) => {
                  const Icon = iconFor(name);
                  return (
                    <motion.li
                      key={name}
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.06 }}
                      className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3"
                    >
                      <span className="flex size-9 items-center justify-center rounded-lg bg-primary-soft text-primary">
                        <Icon className="size-4" />
                      </span>
                      <span className="flex-1 truncate text-sm font-medium">{name}</span>
                      <span className="hidden text-xs text-muted-foreground sm:block">Ready</span>
                      <button
                        aria-label={`Remove ${name}`}
                        onClick={() => setFiles(files.filter((f) => f !== name))}
                        className="rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                      >
                        <X className="size-4" />
                      </button>
                    </motion.li>
                  );
                })}
              </ul>

              <div className="mt-7 flex justify-end">
                <Button onClick={onContinue} className="group h-11 rounded-full px-6">
                  Continue
                  <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </section>
  );
}
