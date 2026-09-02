export function ReconfirmationDialog({
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
        aria-labelledby="reconfirm-title"
        className="candidate-dialog"
      >
        <h2 id="reconfirm-title">Reconfirm current information?</h2>
        <p>
          Confirm that this exact value remains current. A new auditable
          confirmation is added without rewriting history.
        </p>
        <div>
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
          <button className="primary-action" type="button" onClick={onConfirm}>
            Reconfirm
          </button>
        </div>
      </div>
    </div>
  );
}
