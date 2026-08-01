import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { DOC_TYPES, type Classified, type DocType } from "@/data/mock";

export function ClassificationModal({
  open,
  onOpenChange,
  rows,
  onSave,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  rows: Classified[];
  onSave: (rows: Classified[]) => void;
}) {
  const [draft, setDraft] = useState(rows);
  useEffect(() => {
    if (open) setDraft(rows);
  }, [open, rows]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg rounded-3xl">
        <DialogHeader>
          <DialogTitle>Edit classification</DialogTitle>
          <DialogDescription>
            Override the detected document type for any file before analysis.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {draft.map((row, i) => (
            <div key={row.file} className="space-y-1.5">
              <label className="text-sm font-medium">{row.file}</label>
              <Select
                value={row.type}
                onValueChange={(v) =>
                  setDraft((d) =>
                    d.map((r, idx) => (idx === i ? { ...r, type: v as DocType } : r)),
                  )
                }
              >
                <SelectTrigger className="w-full rounded-xl">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DOC_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          ))}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            className="rounded-full"
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>
          <Button
            className="rounded-full px-6"
            onClick={() => {
              onSave(draft);
              onOpenChange(false);
            }}
          >
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
