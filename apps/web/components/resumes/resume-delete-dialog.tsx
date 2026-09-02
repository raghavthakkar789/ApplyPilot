"use client";

import { useEffect, useRef } from "react";
import type { ResumeRecord } from "@/features/resumes/resume-types";

export function ResumeDeleteDialog({
  resume,
  permanent,
  onCancel,
  onConfirm,
}: {
  resume: ResumeRecord | null;
  permanent: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    if (resume && dialog.current && !dialog.current.open)
      dialog.current.showModal();
    if (!resume && dialog.current?.open) dialog.current.close();
  }, [resume]);
  return (
    <dialog ref={dialog} className="candidate-dialog" onCancel={onCancel}>
      {resume && (
        <div>
          <p className="eyebrow">Deletion scope</p>
          <h2>
            {permanent ? "Permanently delete resume?" : "Move resume to trash?"}
          </h2>
          <p>
            {permanent
              ? "The original and extracted text will be removed when no retained dependency requires them. This cannot be undone. Export first if needed."
              : "The resume enters recoverable trash for 30 days and can be restored."}
          </p>
          <div className="dialog-actions">
            <button type="button" onClick={onCancel}>
              Cancel
            </button>
            <button type="button" className="danger-action" onClick={onConfirm}>
              {permanent ? "Permanently delete" : "Move to trash"}
            </button>
          </div>
        </div>
      )}
    </dialog>
  );
}
