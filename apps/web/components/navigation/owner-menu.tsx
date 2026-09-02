"use client";

import { ChevronUp, CircleUserRound } from "lucide-react";
import { useState } from "react";
import { SessionList } from "@/components/sessions/session-list";
import { useOptionalAuth } from "@/features/auth/auth-provider";

export function OwnerMenu() {
  const [open, setOpen] = useState(false);
  const auth = useOptionalAuth();
  return (
    <>
      <button
        className="owner-menu"
        type="button"
        aria-label="Open owner and session menu"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        <CircleUserRound aria-hidden="true" size={22} />
        <span>
          <strong>Local owner</strong>
          <small>Private workspace</small>
        </span>
        <ChevronUp aria-hidden="true" size={16} />
      </button>
      {open && auth && (
        <div className="owner-popover">
          <SessionList onCurrentRevoked={() => void auth.refresh()} />
          <button
            className="logout-button"
            type="button"
            onClick={() => void auth.logout()}
          >
            Sign out
          </button>
        </div>
      )}
    </>
  );
}
