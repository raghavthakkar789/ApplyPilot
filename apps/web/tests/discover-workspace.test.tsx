import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DiscoverWorkspace } from "@/features/discover/discover-workspace";

const jobs = [
  {
    id: "job-1",
    title: "Synthetic Platform Engineer",
    employer: "Example Labs",
    description: "Build safe systems",
    location: "Remote",
    work_mode: "remote",
    employment_type: "full-time",
    freshness_state: "fresh",
    saved: false,
    created_at: "2026-09-02T00:00:00Z",
    sources: [
      {
        provider: "greenhouse",
        source_url: "https://boards.greenhouse.io/example/jobs/1",
        attribution: "Source: Greenhouse",
        retrieved_at: "2026-09-02T00:00:00Z",
      },
    ],
  },
  {
    id: "job-2",
    title: "Synthetic Support Engineer",
    employer: "Remote Example",
    description: "Help customers",
    location: "Worldwide",
    work_mode: "remote",
    employment_type: "contract",
    freshness_state: "possibly_stale",
    saved: false,
    created_at: "2026-09-01T00:00:00Z",
    sources: [
      {
        provider: "remotive",
        source_url: "https://remotive.com/remote-jobs/software-dev/example-1",
        attribution: "Source: Remotive",
        retrieved_at: "2026-09-01T00:00:00Z",
      },
    ],
  },
  {
    id: "job-3",
    title: "Manually Recorded Role",
    employer: "Sample Company",
    description: "Owner supplied details",
    location: null,
    work_mode: null,
    employment_type: null,
    freshness_state: "manually_entered",
    saved: false,
    created_at: "2026-09-01T00:00:00Z",
    sources: [
      {
        provider: "manual",
        source_url: "manual-entry",
        attribution: "Manually entered — source not automatically verified",
        retrieved_at: "2026-09-01T00:00:00Z",
      },
    ],
  },
];

describe("DiscoverWorkspace", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async (_input: RequestInfo | URL, init?: RequestInit) =>
          new Response(
            JSON.stringify(
              init?.method ? jobs[0] : { jobs, partial_failures: [] },
            ),
            { status: 200, headers: { "Content-Type": "application/json" } },
          ),
      ),
    );
    render(<DiscoverWorkspace />);
  });

  it("loads the catalog and has no basic axe violations", async () => {
    expect(
      (await screen.findAllByText("Synthetic Platform Engineer")).length,
    ).toBeGreaterThan(0);
    expect(screen.getAllByText("Not evaluated").length).toBeGreaterThan(0);
    expect((await axe(document.body)).violations).toHaveLength(0);
  });

  it("searches and filters API data", async () => {
    const user = userEvent.setup();
    await screen.findAllByText("Synthetic Platform Engineer");
    await user.type(
      screen.getByRole("textbox", { name: "Search opportunities" }),
      "Support",
    );
    expect(
      within(screen.getByLabelText("1 opportunities")).getByText(
        "Synthetic Support Engineer",
      ),
    ).toBeInTheDocument();
    await user.clear(
      screen.getByRole("textbox", { name: "Search opportunities" }),
    );
    await user.selectOptions(
      screen.getByRole("combobox", { name: "Source filter" }),
      "Remotive",
    );
    expect(
      screen.getAllByText("Synthetic Support Engineer").length,
    ).toBeGreaterThan(0);
  });

  it("preserves Remotive and manual attribution", async () => {
    const user = userEvent.setup();
    await user.click(
      await screen.findByRole("button", {
        name: /Synthetic Support Engineer at Remote Example/,
      }),
    );
    expect(screen.getByText("Source: Remotive")).toBeInTheDocument();
    await user.click(
      screen.getByRole("button", {
        name: /Manually Recorded Role at Sample Company/,
      }),
    );
    expect(
      screen.getByText("Manually entered — source not automatically verified"),
    ).toBeInTheDocument();
  });

  it("saves through a CSRF mutation", async () => {
    document.cookie = "applypilot_csrf=synthetic-csrf";
    const user = userEvent.setup();
    const save = await screen.findByRole("button", {
      name: "Save Synthetic Platform Engineer",
    });
    await user.click(save);
    expect(save).toHaveAttribute("aria-pressed", "true");
    expect(fetch).toHaveBeenCalledWith(
      "/api/jobs/job-1/save",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "X-ApplyPilot-CSRF": "synthetic-csrf",
        }),
      }),
    );
  });
});
