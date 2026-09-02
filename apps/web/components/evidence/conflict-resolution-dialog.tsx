import { useState } from "react";
import type { ConflictDetail } from "@/features/candidate/candidate-types";

export function ConflictResolutionDialog({
  conflict,
  onCancel,
  onConfirm,
}: {
  conflict: ConflictDetail | null;
  onCancel: () => void;
  onConfirm: (version: string, reason: string) => void;
}) {
  const [selected, setSelected] = useState("");
  const [reason, setReason] = useState("");
  if (!conflict) return null;
  return (
    <div className="dialog-backdrop" role="presentation">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="conflict-title"
        className="candidate-dialog"
      >
        <h2 id="conflict-title">Resolve competing values</h2>
        <p>
          ApplyPilot will not choose based on confidence, recency, or majority
          agreement.
        </p>
        {conflict.members.map((member) => (
          <label className="conflict-option" key={member.id}>
            <input
              type="radio"
              name="winner"
              value={member.id}
              checked={selected === member.id}
              onChange={() => setSelected(member.id)}
            />
            <span>
              {JSON.stringify(member.value)}
              <small>
                {member.source_type} · version {member.version_number}
              </small>
            </span>
          </label>
        ))}
        <label>
          Resolution reason
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
            className="primary-action"
            disabled={!selected || !reason.trim()}
            type="button"
            onClick={() => onConfirm(selected, reason)}
          >
            Resolve explicitly
          </button>
        </div>
      </div>
    </div>
  );
}
