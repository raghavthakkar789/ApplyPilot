"use client";

import { useEffect, useState } from "react";
import { sessions } from "@/features/auth/auth-api";

export function SessionExpiryWarning() {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    void sessions()
      .then((items) => {
        const current = items.find((item) => item.current);
        if (!current) return;
        const delay =
          Date.parse(current.idle_expires_at) - Date.now() - 5 * 60 * 1000;
        if (delay <= 0) setVisible(true);
        else timer = setTimeout(() => setVisible(true), delay);
      })
      .catch(() => undefined);
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, []);
  return visible ? (
    <div className="session-warning" role="status">
      Your session may expire in about five minutes. Save active work through
      ApplyPilot.
    </div>
  ) : null;
}
