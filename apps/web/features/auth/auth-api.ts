import { csrfHeaders } from "@/lib/csrf-client";
import type { ApiProblem, SessionView } from "@/types/generated-auth";

const JSON_HEADERS = { "Content-Type": "application/json" };
export const SESSION_EXPIRED_EVENT = "applypilot:session-expired";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly retryAfter: number | null = null,
  ) {
    super(message);
  }
}

function notifyIfSessionExpired(response: Response): void {
  if (response.status === 401 && typeof window !== "undefined") {
    window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
  }
}

async function problem(response: Response): Promise<Error> {
  const body = (await response.json().catch(() => ({}))) as ApiProblem;
  const retryHeader = response.headers.get("Retry-After");
  const retryAfter = retryHeader ? Number.parseInt(retryHeader, 10) : null;
  return new ApiError(
    body.detail ?? "The request could not be completed.",
    Number.isFinite(retryAfter) ? retryAfter : null,
  );
}

export async function initializationRequired(): Promise<boolean> {
  const response = await fetch("/api/initialization/status", {
    credentials: "same-origin",
  });
  if (!response.ok) throw await problem(response);
  return ((await response.json()) as { required: boolean }).required;
}

export async function initialize(
  password: string,
  confirmation: string,
): Promise<void> {
  const response = await fetch("/api/initialization", {
    method: "POST",
    credentials: "same-origin",
    headers: JSON_HEADERS,
    body: JSON.stringify({ password, password_confirmation: confirmation }),
  });
  if (!response.ok) throw await problem(response);
}

export async function login(password: string): Promise<void> {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    credentials: "same-origin",
    headers: JSON_HEADERS,
    body: JSON.stringify({ password }),
  });
  if (!response.ok) throw await problem(response);
}

export async function authenticated(): Promise<boolean> {
  const response = await fetch("/api/auth/status", {
    credentials: "same-origin",
  });
  return response.ok;
}

export async function logout(): Promise<void> {
  const response = await fetch("/api/auth/logout", {
    method: "POST",
    credentials: "same-origin",
    headers: csrfHeaders(),
  });
  notifyIfSessionExpired(response);
  if (!response.ok) throw await problem(response);
}

export async function sessions(): Promise<SessionView[]> {
  const response = await fetch("/api/sessions", { credentials: "same-origin" });
  notifyIfSessionExpired(response);
  if (!response.ok) throw await problem(response);
  return ((await response.json()) as { sessions: SessionView[] }).sessions;
}

export async function revokeSession(id: string): Promise<void> {
  const response = await fetch(`/api/sessions/${encodeURIComponent(id)}`, {
    method: "DELETE",
    credentials: "same-origin",
    headers: csrfHeaders(),
  });
  notifyIfSessionExpired(response);
  if (!response.ok) throw await problem(response);
}

export async function revokeOtherSessions(): Promise<void> {
  const response = await fetch("/api/sessions/revoke-others", {
    method: "POST",
    credentials: "same-origin",
    headers: csrfHeaders(),
  });
  notifyIfSessionExpired(response);
  if (!response.ok) throw await problem(response);
}
