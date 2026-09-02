import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { FactEditorDialog } from "@/components/evidence/fact-editor-dialog";
import { FactHistory } from "@/components/evidence/fact-history";
import { RevocationDialog } from "@/components/evidence/revocation-dialog";
import { VerificationDialog } from "@/components/evidence/verification-dialog";
import { ProfileEditor } from "@/components/profile/profile-editor";
import { createFact } from "@/features/candidate/candidate-api";
import type {
  FactVersion,
  ProfileSections,
} from "@/features/candidate/candidate-types";

const sections: ProfileSections = {
  identity: {},
  contact: {},
  current_location: {},
  professional_summary: {},
  desired_roles: [],
  skills: [],
  employment_history: [],
  education: [],
  projects: [],
  certifications: [],
  languages: [],
  portfolio_links: [],
  work_preferences: {},
  availability: {},
  compensation: {},
  relocation: {},
  work_authorization: {},
};

const version: FactVersion = {
  id: "synthetic-version",
  version_number: 1,
  value: "Synthetic evidence",
  lifecycle_state: "unverified",
  source_type: "owner_entry",
  source_reference: null,
  source_version: null,
  evidence_citation: null,
  created_at: "2026-09-02T00:00:00Z",
  owner_confirmed_at: null,
  reconfirmation_policy: "days_90",
  confirmation_due_at: null,
  sensitivity: "standard",
  current: true,
};

describe("candidate profile and evidence UI", () => {
  beforeEach(() => {
    document.cookie = "applypilot_csrf=csrf-value; Path=/";
  });

  it("renders profile fields and explains the verification boundary", async () => {
    const save = vi.fn(async () => undefined);
    const { container } = render(
      <ProfileEditor sections={sections} onSave={save} />,
    );
    expect(
      screen.getByText(/Saving profile structure does not verify/),
    ).toBeInTheDocument();
    await userEvent.type(
      screen.getByLabelText("Preferred name"),
      "Sample Candidate",
    );
    await userEvent.click(screen.getByRole("button", { name: "Save profile" }));
    expect(save).toHaveBeenCalled();
    expect((await axe(container)).violations).toHaveLength(0);
  });

  it("labels lifecycle state and immutable history with text", () => {
    render(
      <FactHistory
        versions={[
          version,
          {
            ...version,
            id: "old",
            version_number: 0,
            lifecycle_state: "revoked",
            current: false,
          },
        ]}
      />,
    );
    expect(screen.getByText("unverified")).toBeInTheDocument();
    expect(screen.getByText("revoked")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Immutable version history" }),
    ).toBeInTheDocument();
  });

  it("warns that editing creates a new unverified version", () => {
    render(
      <FactEditorDialog
        open
        existing={{
          identity_id: "identity",
          fact_type: "skill",
          semantic_key: "skill.synthetic",
          scope: "*",
          current_version: version,
          versions: [version],
        }}
        onCancel={vi.fn()}
        onConfirm={vi.fn()}
      />,
    );
    expect(
      screen.getByText(/creates a new unverified version/i),
    ).toBeInTheDocument();
  });

  it("requires deliberate verification and a revocation reason", async () => {
    const verify = vi.fn();
    const revoke = vi.fn();
    const user = userEvent.setup();
    const { rerender } = render(
      <VerificationDialog open onCancel={vi.fn()} onConfirm={verify} />,
    );
    await user.click(
      screen.getByRole("button", { name: "Verify exact version" }),
    );
    expect(verify).toHaveBeenCalledOnce();
    rerender(<RevocationDialog open onCancel={vi.fn()} onConfirm={revoke} />);
    expect(
      screen.getByRole("button", { name: "Revoke version" }),
    ).toBeDisabled();
    await user.type(screen.getByLabelText("Reason"), "Synthetic correction");
    await user.click(screen.getByRole("button", { name: "Revoke version" }));
    expect(revoke).toHaveBeenCalledWith("Synthetic correction");
  });

  it("includes the session-bound CSRF header on mutations", async () => {
    const fetchMock = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            identity_id: "id",
            fact_type: "skill",
            semantic_key: "skill.synthetic",
            scope: "*",
            current_version: version,
          }),
          { status: 201, headers: { "Content-Type": "application/json" } },
        ),
    );
    vi.stubGlobal("fetch", fetchMock);
    await createFact({
      fact_type: "skill",
      semantic_key: "skill.synthetic",
      value: "Synthetic",
    });
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/candidate-facts",
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            "X-ApplyPilot-CSRF": "csrf-value",
          }),
        }),
      ),
    );
  });
});
