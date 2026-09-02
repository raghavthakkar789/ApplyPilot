import { useState } from "react";

export function RevocationDialog({
  open,
  onCancel,
  onConfirm,
}: {
  open: boolean;
  onCancel: () => void;
  onConfirm: (reason: string) => void;
}) {
  const [reason, setReason] = useState("");
  if (!open) return null;
  return (
    <div className="dialog-backdrop" role="presentation">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="revoke-title"
        className="candidate-dialog"
      >
        <h2 id="revoke-title">Revoke this fact version?</h2>
        <p>Revocation blocks future use immediately and preserves history.</p>
        <label>
          Reason
          <textarea
            value={reason}
            onChange={(event) => setReason(event.target.value)}
          />
        </label>
        <div>
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
          <button
            className="danger-action"
            disabled={!reason.trim()}
            type="button"
            onClick={() => onConfirm(reason)}
          >
            Revoke version
          </button>
        </div>
      </div>
    </div>
  );
}
