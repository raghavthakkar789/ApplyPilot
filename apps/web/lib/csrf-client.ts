export const CSRF_HEADER = "X-ApplyPilot-CSRF";

export function readCsrfCookie(): string | null {
  if (typeof document === "undefined") return null;
  const entry = document.cookie
    .split(";")
    .map((value) => value.trim())
    .find((value) => value.startsWith("applypilot_csrf="));
  return entry
    ? decodeURIComponent(entry.slice("applypilot_csrf=".length))
    : null;
}

export function csrfHeaders(): HeadersInit {
  const token = readCsrfCookie();
  return token ? { [CSRF_HEADER]: token } : {};
}
