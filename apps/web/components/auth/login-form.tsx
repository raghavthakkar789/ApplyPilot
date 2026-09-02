"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/features/auth/auth-provider";
import { ApiError } from "@/features/auth/auth-api";

export function LoginForm() {
  const { login } = useAuth();
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <form
      className="auth-form"
      onSubmit={async (event) => {
        event.preventDefault();
        setBusy(true);
        setError("");
        try {
          await login(password);
          router.replace("/");
        } catch (caught) {
          setError(
            caught instanceof ApiError && caught.retryAfter
              ? `Authentication could not be completed. Try again in ${caught.retryAfter} seconds.`
              : "Authentication could not be completed. Check the password or wait before retrying.",
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
          autoComplete="current-password"
          required
          maxLength={1024}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
      </label>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      <button type="submit" disabled={busy}>
        {busy ? "Signing in…" : "Sign in"}
      </button>
      <p className="auth-recovery-note">
        Passwords cannot be retrieved. To reset your password, use the local
        ApplyPilot recovery command on your Fedora computer.
      </p>
    </form>
  );
}
