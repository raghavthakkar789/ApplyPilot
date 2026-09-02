import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { CandidateReviewDialog } from "@/components/resumes/candidate-review-dialog";
import { ExtractionWarning } from "@/components/resumes/extraction-warning";
import { FactCandidateList } from "@/components/resumes/fact-candidate-list";
import { ResumeDeleteDialog } from "@/components/resumes/resume-delete-dialog";
import { ResumeUploadDialog } from "@/components/resumes/resume-upload-dialog";
import { ResumeVersionHistory } from "@/components/resumes/resume-version-history";
import { uploadResume } from "@/features/resumes/resume-api";
import type {
  FactCandidate,
  ResumeRecord,
  ResumeVersion,
} from "@/features/resumes/resume-types";

const version: ResumeVersion = {
  id: "synthetic-version",
  version_number: 1,
  filename: "synthetic.txt",
  media_type: "text/plain",
  format: "text",
  byte_length: 42,
  sha256: "a".repeat(64),
  parser: "TextParser",
  parser_version: "stdlib-utf8-1",
  extraction_status: "succeeded",
  integrity_state: "verified",
  created_at: "2026-09-02T00:00:00Z",
  superseded_at: null,
  current: true,
};
const resume: ResumeRecord = {
  id: "synthetic-resume",
  display_name: "Synthetic resume",
  purpose: "Testing",
  created_at: "2026-09-02T00:00:00Z",
  trashed_at: null,
  purge_after: null,
  current_version: version,
};
const candidate: FactCandidate = {
  id: "synthetic-candidate",
  resume_version_id: version.id,
  fact_type: "skill",
  semantic_key: "skill.synthetic",
  proposed_value: "Synthetic skill",
  evidence_citation: "line 1",
  extraction_method: "deterministic_label_v1",
  confidence: "high",
  review_status: "pending",
  created_at: "2026-09-02T00:00:00Z",
  reviewed_at: null,
  resulting_fact_identity_id: null,
  resulting_fact_version_id: null,
};

describe("resume ingestion UI", () => {
  beforeEach(() => {
    document.cookie = "applypilot_csrf=csrf-value; Path=/";
    HTMLDialogElement.prototype.showModal = vi.fn(function (
      this: HTMLDialogElement,
    ) {
      this.setAttribute("open", "");
    });
    HTMLDialogElement.prototype.close = vi.fn(function (
      this: HTMLDialogElement,
    ) {
      this.removeAttribute("open");
    });
  });

  it("shows supported formats, size boundary, and separate verification", async () => {
    const upload = vi.fn(async () => undefined);
    const { container } = render(
      <ResumeUploadDialog open onCancel={vi.fn()} onUpload={upload} />,
    );
    expect(
      screen.getByText(/PDF, DOCX, or UTF-8 TXT, up to 10 MiB/),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/never overwrites or verifies/),
    ).toBeInTheDocument();
    expect(screen.queryByText(/accept and verify/i)).not.toBeInTheDocument();
    expect((await axe(container)).violations).toHaveLength(0);
  });

  it("rejects an oversized file before calling the API", async () => {
    const upload = vi.fn(async () => undefined);
    render(<ResumeUploadDialog open onCancel={vi.fn()} onUpload={upload} />);
    await userEvent.type(screen.getByLabelText("Display name"), "Synthetic");
    const large = new File(
      [new Uint8Array(10 * 1024 * 1024 + 1)],
      "large.txt",
      {
        type: "text/plain",
      },
    );
    await userEvent.upload(screen.getByLabelText("Resume file"), large);
    await userEvent.click(
      screen.getByRole("button", { name: "Upload securely" }),
    );
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "exceeds 10 MiB",
    );
    expect(upload).not.toHaveBeenCalled();
  });

  it("shows immutable history, extraction warning, and text lifecycle labels", () => {
    render(
      <>
        <ResumeVersionHistory versions={[version]} />
        <ExtractionWarning message="Page 1 contains no extractable text; OCR was not run." />
        <FactCandidateList candidates={[candidate]} onReview={vi.fn()} />
      </>,
    );
    expect(screen.getByText("Immutable version history")).toBeInTheDocument();
    expect(screen.getByText("Extraction complete")).toBeInTheDocument();
    expect(screen.getByText("Unverified candidate")).toBeInTheDocument();
    expect(screen.getByText(/OCR was not run/)).toBeInTheDocument();
  });

  it("keeps Accept candidate separate from explicit verification", () => {
    render(
      <CandidateReviewDialog
        candidate={candidate}
        onCancel={vi.fn()}
        onAccept={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(
      screen.getByRole("button", { name: "Accept candidate" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /verify/i }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText(/separate explicit Verify action/),
    ).toBeInTheDocument();
  });

  it("shows recoverable trash and permanent deletion scopes", () => {
    const { rerender } = render(
      <ResumeDeleteDialog
        resume={resume}
        permanent={false}
        onCancel={vi.fn()}
        onConfirm={vi.fn()}
      />,
    );
    expect(
      screen.getByText(/recoverable trash for 30 days/),
    ).toBeInTheDocument();
    rerender(
      <ResumeDeleteDialog
        resume={resume}
        permanent
        onCancel={vi.fn()}
        onConfirm={vi.fn()}
      />,
    );
    expect(screen.getByText(/This cannot be undone/)).toBeInTheDocument();
  });

  it("sends multipart mutations with CSRF and never uses Web Storage", async () => {
    const fetchMock = vi.fn(
      async () =>
        new Response(JSON.stringify(resume), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const storageSpy = vi.spyOn(Storage.prototype, "setItem");
    await uploadResume(
      new File(["safe"], "safe.txt", { type: "text/plain" }),
      "Safe",
    );
    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/resumes",
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            "X-ApplyPilot-CSRF": "csrf-value",
          }),
        }),
      ),
    );
    expect(storageSpy).not.toHaveBeenCalled();
  });
});
