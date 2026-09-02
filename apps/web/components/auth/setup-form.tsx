"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/features/auth/auth-provider";

export function SetupForm() {
  const { initialize } = useAuth();
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <form
      className="auth-form"
      onSubmit={async (event) => {
        event.preventDefault();
        setError("");
        if (password !== confirmation) {
          setError("Passwords do not match.");
          return;
        }
        setBusy(true);
        try {
          await initialize(password, confirmation);
          router.replace("/");
        } catch (caught) {
          setError(
            caught instanceof Error
              ? caught.message
              : "Setup could not be completed.",
          );
        } finally {
          setBusy(false);
        }
      }}
    >
      <label>
        Owner password
        <input
          name="password"
          type="password"
          autoComplete="new-password"
          maxLength={1024}
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
      </label>
      <label>
        Confirm password
        <input
          name="password-confirmation"
          type="password"
          autoComplete="new-password"
          maxLength={1024}
          required
          value={confirmation}
          onChange={(event) => setConfirmation(event.target.value)}
        />
      </label>
      <p className="form-help">
        Use at least 12 characters. Long password-manager-generated passwords
        are supported.
      </p>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      <button type="submit" disabled={busy}>
        {busy ? "Creating owner…" : "Create private owner"}
      </button>
    </form>
  );
}
