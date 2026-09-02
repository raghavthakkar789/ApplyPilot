"use client";

import { useEffect, useRef, useState } from "react";

const MAX_BYTES = 10 * 1024 * 1024;
const ACCEPT =
  ".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain";

export function ResumeUploadDialog({
  open,
  existingName,
  onCancel,
  onUpload,
}: {
  open: boolean;
  existingName?: string;
  onCancel: () => void;
  onUpload: (file: File, name: string, purpose: string) => Promise<void>;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    if (open && dialog.current && !dialog.current.open)
      dialog.current.showModal();
    if (!open && dialog.current?.open) dialog.current.close();
  }, [open]);
  return (
    <dialog ref={dialog} className="candidate-dialog" onCancel={onCancel}>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          const file = form.get("resume") as File;
          if (!file?.size) return setError("Choose a document to upload.");
          if (file.size > MAX_BYTES)
            return setError("The file exceeds 10 MiB.");
          setBusy(true);
          void onUpload(
            file,
            String(form.get("displayName") ?? ""),
            String(form.get("purpose") ?? ""),
          ).finally(() => setBusy(false));
        }}
      >
        <p className="eyebrow">Protected document storage</p>
        <h2>{existingName ? "Upload a new version" : "Add resume"}</h2>
        <p>PDF, DOCX, or UTF-8 TXT, up to 10 MiB. OCR is not performed.</p>
        {!existingName && (
          <>
            <label>
              Display name
              <input name="displayName" required maxLength={160} />
            </label>
            <label>
              Purpose or label
              <input name="purpose" maxLength={160} />
            </label>
          </>
        )}
        <label>
          Resume file
          <input
            name="resume"
            type="file"
            accept={ACCEPT}
            required
            onChange={(event) => {
              const file = event.currentTarget.files?.[0];
              setError(
                file && file.size > MAX_BYTES ? "The file exceeds 10 MiB." : "",
              );
            }}
          />
        </label>
        {error && <p role="alert">{error}</p>}
        <p className="dialog-note">
          A newer resume never overwrites or verifies existing candidate facts.
        </p>
        <div className="dialog-actions">
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
          <button className="primary-action" disabled={busy}>
            {busy ? "Validating and extracting…" : "Upload securely"}
          </button>
        </div>
      </form>
    </dialog>
  );
}
