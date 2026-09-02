"use client";

import { useEffect, useRef } from "react";
import type { FactCandidate } from "@/features/resumes/resume-types";

export function CandidateReviewDialog({
  candidate,
  onCancel,
  onAccept,
  onReject,
}: {
  candidate: FactCandidate | null;
  onCancel: () => void;
  onAccept: () => void;
  onReject: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    if (candidate && dialog.current && !dialog.current.open)
      dialog.current.showModal();
    if (!candidate && dialog.current?.open) dialog.current.close();
  }, [candidate]);
  return (
    <dialog ref={dialog} className="candidate-dialog" onCancel={onCancel}>
      {candidate && (
        <div>
          <p className="eyebrow">Unverified candidate</p>
          <h2>Review extracted item</h2>
          <dl>
            <dt>Proposed value</dt>
            <dd>{String(candidate.proposed_value)}</dd>
            <dt>Source citation</dt>
            <dd>{candidate.evidence_citation}</dd>
          </dl>
          <p className="dialog-note">
            Accept creates an ordinary unverified fact. To verify it, open
            Evidence and take the separate explicit Verify action.
          </p>
          <div className="dialog-actions">
            <button type="button" onClick={onCancel}>
              Cancel
            </button>
            <button type="button" className="danger-action" onClick={onReject}>
              Reject candidate
            </button>
            <button type="button" className="primary-action" onClick={onAccept}>
              Accept candidate
            </button>
          </div>
        </div>
      )}
    </dialog>
  );
}
