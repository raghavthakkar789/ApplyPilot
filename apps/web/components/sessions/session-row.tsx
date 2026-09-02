import type { SessionView } from "@/types/generated-auth";

export function SessionRow({
  session,
  onRevoke,
}: {
  session: SessionView;
  onRevoke: (id: string) => void;
}) {
  return (
    <li className="session-row">
      <div>
        <strong>
          {session.client_label ?? "Local browser"}
          {session.current ? " · Current" : ""}
        </strong>
        <span>
          Last active {new Date(session.last_activity_at).toLocaleString()}
        </span>
        <span>
          Expires {new Date(session.absolute_expires_at).toLocaleString()}
        </span>
      </div>
      <button type="button" onClick={() => onRevoke(session.id)}>
        {session.current ? "Sign out" : "Revoke"}
      </button>
    </li>
  );
}
