"use client";

import { useEffect, useState } from "react";
import {
  revokeOtherSessions,
  revokeSession,
  sessions,
} from "@/features/auth/auth-api";
import type { SessionView } from "@/types/generated-auth";
import { RevokeSessionsDialog } from "./revoke-sessions-dialog";
import { SessionRow } from "./session-row";

export function SessionList({
  onCurrentRevoked,
}: {
  onCurrentRevoked: () => void;
}) {
  const [items, setItems] = useState<SessionView[]>([]);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState("");
  const load = () =>
    void sessions()
      .then(setItems)
      .catch(() => setError("Sessions could not be loaded."));
  useEffect(load, []);
  const revoke = async (id: string) => {
    const current = items.find((item) => item.id === id)?.current;
    try {
      await revokeSession(id);
      if (current) onCurrentRevoked();
      else load();
    } catch {
      setError("Session could not be revoked.");
    }
  };
  const revokeOthers = async () => {
    try {
      await revokeOtherSessions();
      setConfirming(false);
      load();
    } catch {
      setError("Other sessions could not be revoked.");
    }
  };
  return (
    <section className="sessions-panel" aria-labelledby="sessions-title">
      <h2 id="sessions-title">Active sessions</h2>
      <p>At most three local sessions may remain active.</p>
      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}
      <ul>
        {items.map((item) => (
          <SessionRow key={item.id} session={item} onRevoke={revoke} />
        ))}
      </ul>
      <button
        type="button"
        onClick={() => setConfirming(true)}
        disabled={items.filter((item) => !item.current).length === 0}
      >
        Revoke all other sessions
      </button>
      {confirming && (
        <RevokeSessionsDialog
          onCancel={() => setConfirming(false)}
          onConfirm={() => void revokeOthers()}
        />
      )}
    </section>
  );
}
