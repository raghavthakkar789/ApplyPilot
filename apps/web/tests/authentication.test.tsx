import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LoginPage from "@/app/login/page";
import SetupPage from "@/app/setup/page";
import { ProtectedRouteBoundary } from "@/components/auth/protected-route-boundary";
import { SessionExpiryWarning } from "@/components/auth/session-expiry-warning";
import { SessionList } from "@/components/sessions/session-list";
import { AuthProvider } from "@/features/auth/auth-provider";
import { logout } from "@/features/auth/auth-api";
import { SESSION_EXPIRED_EVENT } from "@/features/auth/auth-api";

const replace = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));

function response(
  body: unknown,
  status = 200,
  headers: Record<string, string> = {},
): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });
}

function mockApi(
  options: {
    setup?: boolean;
    authenticated?: boolean;
    loginStatus?: number;
  } = {},
) {
  const fetchMock = vi.fn(
    async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/api/initialization/status"))
        return response({ required: options.setup ?? false });
      if (url.endsWith("/api/auth/status"))
        return response({}, options.authenticated ? 200 : 401);
      if (url.endsWith("/api/initialization") && init?.method === "POST")
        return response({ authenticated: true }, 201);
      if (url.endsWith("/api/auth/login"))
        return response(
          options.loginStatus === 401
            ? { detail: "Authentication could not be completed." }
            : { authenticated: true },
          options.loginStatus ?? 200,
          options.loginStatus === 429 ? { "Retry-After": "30" } : {},
        );
      if (url.endsWith("/api/auth/logout"))
        return new Response(null, { status: 204 });
      if (url.endsWith("/api/sessions"))
        return response({
          sessions: [
            {
              id: "one",
              created_at: new Date().toISOString(),
              last_activity_at: new Date().toISOString(),
              idle_expires_at: new Date(Date.now() + 4 * 60_000).toISOString(),
              absolute_expires_at: new Date(
                Date.now() + 60 * 60_000,
              ).toISOString(),
              client_label: "Chrome browser",
              current: true,
            },
            {
              id: "two",
              created_at: new Date().toISOString(),
              last_activity_at: new Date().toISOString(),
              idle_expires_at: new Date(Date.now() + 30 * 60_000).toISOString(),
              absolute_expires_at: new Date(
                Date.now() + 60 * 60_000,
              ).toISOString(),
              client_label: "Firefox browser",
              current: false,
            },
          ],
        });
      if (url.includes("/api/sessions/"))
        return new Response(null, { status: 204 });
      return response({}, 404);
    },
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("M1 authentication UI", () => {
  beforeEach(() => {
    replace.mockReset();
    document.cookie = "applypilot_csrf=; Max-Age=0; Path=/";
  });

  it("completes setup only after matching password confirmation and passes axe", async () => {
    const fetchMock = mockApi({ setup: true });
    render(
      <AuthProvider>
        <SetupPage />
      </AuthProvider>,
    );
    const user = userEvent.setup();
    await screen.findByRole("heading", { name: "Create the local owner" });
    const fields = screen.getAllByLabelText(/password/i);
    await user.type(fields[0], "a sufficiently long password");
    await user.type(fields[1], "different long password");
    await user.click(
      screen.getByRole("button", { name: "Create private owner" }),
    );
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Passwords do not match",
    );
    await user.clear(fields[1]);
    await user.type(fields[1], "a sufficiently long password");
    await user.click(
      screen.getByRole("button", { name: "Create private owner" }),
    );
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/initialization",
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect((await axe(document.body)).violations).toHaveLength(0);
  });

  it("shows a generic login failure and supports keyboard submission", async () => {
    mockApi({ loginStatus: 401 });
    render(
      <AuthProvider>
        <LoginPage />
      </AuthProvider>,
    );
    expect(
      await screen.findByRole("button", { name: "Forgot password?" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByText(/Your password cannot be retrieved/i),
    ).not.toBeInTheDocument();
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Forgot password?" }));
    expect(
      await screen.findByText(
        /Your password cannot be retrieved.*ApplyPilot password-reset command/s,
      ),
    ).toBeInTheDocument();
    expect(screen.queryByLabelText(/recovery phrase/i)).not.toBeInTheDocument();
    const password = await screen.findByLabelText("Owner password");
    await user.type(password, "incorrect but long password{Enter}");
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Authentication could not be completed",
    );
  });

  it("announces safe throttling feedback", async () => {
    mockApi({ loginStatus: 429 });
    render(
      <AuthProvider>
        <LoginPage />
      </AuthProvider>,
    );
    const user = userEvent.setup();
    const password = await screen.findByLabelText("Owner password");
    await user.type(password, "incorrect but long password{Enter}");
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Try again in 30 seconds",
    );
  });

  it("redirects an anonymous protected route without rendering its content", async () => {
    mockApi({ authenticated: false });
    render(
      <AuthProvider>
        <ProtectedRouteBoundary>
          <p>Private content</p>
        </ProtectedRouteBoundary>
      </AuthProvider>,
    );
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
    expect(screen.queryByText("Private content")).not.toBeInTheDocument();
  });

  it("returns an expired authenticated view to login", async () => {
    mockApi({ authenticated: true });
    render(
      <AuthProvider>
        <ProtectedRouteBoundary>
          <p>Private content</p>
        </ProtectedRouteBoundary>
      </AuthProvider>,
    );
    expect(await screen.findByText("Private content")).toBeInTheDocument();
    window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });

  it("sends the CSRF cookie in the custom header and never uses browser storage", async () => {
    const fetchMock = mockApi();
    const localSpy = vi.spyOn(Storage.prototype, "setItem");
    document.cookie = "applypilot_csrf=csrf-value; Path=/";
    await logout();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/auth/logout",
      expect.objectContaining({
        headers: { "X-ApplyPilot-CSRF": "csrf-value" },
      }),
    );
    expect(localSpy).not.toHaveBeenCalled();
  });

  it("lists sessions, confirms bulk revocation, and exposes the idle warning", async () => {
    mockApi();
    const user = userEvent.setup();
    render(
      <>
        <SessionList onCurrentRevoked={vi.fn()} />
        <SessionExpiryWarning />
      </>,
    );
    expect(
      await screen.findByText(/Chrome browser · Current/),
    ).toBeInTheDocument();
    expect(await screen.findByText(/session may expire/i)).toBeInTheDocument();
    await user.click(
      screen.getByRole("button", { name: "Revoke all other sessions" }),
    );
    expect(
      screen.getByRole("alertdialog", { name: "Revoke other sessions?" }),
    ).toBeInTheDocument();
  });
});
