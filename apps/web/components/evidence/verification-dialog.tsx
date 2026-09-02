export function VerificationDialog({
  open,
  onCancel,
  onConfirm,
}: {
  open: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  if (!open) return null;
  return (
    <div className="dialog-backdrop" role="presentation">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="verify-title"
        className="candidate-dialog"
      >
        <h2 id="verify-title">Verify this exact fact version?</h2>
        <p>
          This deliberate action confirms the displayed value as owner-verified.
          Source agreement alone never verifies it.
        </p>
        <div>
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
          <button className="primary-action" type="button" onClick={onConfirm}>
            Verify exact version
          </button>
        </div>
      </div>
    </div>
  );
}
