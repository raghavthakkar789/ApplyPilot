export function RevokeSessionsDialog({
  onConfirm,
  onCancel,
}: {
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div
      className="confirm-dialog"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="revoke-title"
    >
      <h3 id="revoke-title">Revoke other sessions?</h3>
      <p>Every other active ApplyPilot session will be signed out.</p>
      <div>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
        <button type="button" onClick={onConfirm}>
          Revoke other sessions
        </button>
      </div>
    </div>
  );
}
