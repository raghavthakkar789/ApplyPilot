"use client";

import {
  ArrowLeft,
  Download,
  Plus,
  RotateCcw,
  Trash2,
  Upload,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { CandidateReviewDialog } from "@/components/resumes/candidate-review-dialog";
import { ExtractedContentViewer } from "@/components/resumes/extracted-content-viewer";
import { FactCandidateList } from "@/components/resumes/fact-candidate-list";
import { ResumeDeleteDialog } from "@/components/resumes/resume-delete-dialog";
import { ResumeList } from "@/components/resumes/resume-list";
import { ResumeUploadDialog } from "@/components/resumes/resume-upload-dialog";
import { ResumeVersionHistory } from "@/components/resumes/resume-version-history";
import * as api from "./resume-api";
import type {
  Extraction,
  FactCandidate,
  ResumeDetail,
  ResumeRecord,
} from "./resume-types";

export function ResumeWorkspace() {
  const [resumes, setResumes] = useState<ResumeRecord[]>([]);
  const [selected, setSelected] = useState<ResumeDetail | null>(null);
  const [extraction, setExtraction] = useState<Extraction | null>(null);
  const [candidates, setCandidates] = useState<FactCandidate[]>([]);
  const [upload, setUpload] = useState<"new" | "version" | null>(null);
  const [review, setReview] = useState<FactCandidate | null>(null);
  const [deleting, setDeleting] = useState<"trash" | "permanent" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const load = useCallback(async () => setResumes(await api.listResumes()), []);
  const select = useCallback(async (id: string) => {
    const detail = await api.readResume(id);
    setSelected(detail);
    const current = detail.current_version;
    if (current) {
      const [nextExtraction, nextCandidates] = await Promise.all([
        api.readExtraction(current.id),
        api.listCandidates(current.id),
      ]);
      setExtraction(nextExtraction);
      setCandidates(nextCandidates);
    }
  }, []);
  useEffect(() => {
    const pending = window.setTimeout(() => {
      void load().catch((reason: Error) => setError(reason.message));
    }, 0);
    return () => window.clearTimeout(pending);
  }, [load]);
  const refresh = async () => {
    await load();
    if (selected) await select(selected.id);
  };
  return (
    <AppShell>
      <main className="candidate-workspace resume-workspace">
        <header className="candidate-header resume-header">
          <div>
            <p className="eyebrow">Evidence library</p>
            <h1>Resumes</h1>
            <p>
              Private originals, immutable versions, deterministic extraction,
              and deliberate review.
            </p>
          </div>
          <button className="primary-action" onClick={() => setUpload("new")}>
            <Plus aria-hidden="true" /> Add resume
          </button>
        </header>
        {error && (
          <div role="alert" className="candidate-error">
            {error}
          </div>
        )}
        <div className="resume-layout" data-detail-open={Boolean(selected)}>
          <section className="resume-list-pane" aria-label="Resume library">
            <ResumeList
              resumes={resumes}
              selectedId={selected?.id}
              onSelect={(id) =>
                void select(id).catch((reason: Error) =>
                  setError(reason.message),
                )
              }
            />
          </section>
          <section className="resume-detail-pane">
            {selected ? (
              <>
                <button
                  type="button"
                  className="resume-mobile-back"
                  onClick={() => setSelected(null)}
                >
                  <ArrowLeft aria-hidden="true" /> Back to resumes
                </button>
                <header className="resume-detail-header">
                  <div>
                    <p className="eyebrow">
                      {selected.trashed_at
                        ? "Recoverable trash"
                        : "Protected document"}
                    </p>
                    <h2>{selected.display_name}</h2>
                    <p>{selected.purpose || "No purpose label"}</p>
                  </div>
                  <div className="evidence-actions">
                    {!selected.trashed_at && (
                      <>
                        <a
                          className="button-link"
                          href={`/api/resumes/versions/${selected.current_version?.id}/download`}
                        >
                          <Download aria-hidden="true" /> Download
                        </a>
                        <button onClick={() => setUpload("version")}>
                          <Upload aria-hidden="true" /> New version
                        </button>
                        <button
                          className="danger-action"
                          onClick={() => setDeleting("trash")}
                        >
                          <Trash2 aria-hidden="true" /> Trash
                        </button>
                      </>
                    )}
                    {selected.trashed_at && (
                      <>
                        <button
                          onClick={() =>
                            void api.restoreResume(selected.id).then(refresh)
                          }
                        >
                          <RotateCcw aria-hidden="true" /> Restore
                        </button>
                        <button
                          className="danger-action"
                          onClick={() => setDeleting("permanent")}
                        >
                          <Trash2 aria-hidden="true" /> Delete permanently
                        </button>
                      </>
                    )}
                  </div>
                </header>
                <ResumeVersionHistory versions={selected.versions} />
                <ExtractedContentViewer extraction={extraction} />
                <FactCandidateList
                  candidates={candidates}
                  onReview={setReview}
                />
              </>
            ) : (
              <div className="candidate-empty">
                <h2>Select a resume</h2>
                <p>
                  Inspect its immutable versions, extraction warnings, evidence
                  citations, and review candidates.
                </p>
              </div>
            )}
          </section>
        </div>
        <ResumeUploadDialog
          open={upload !== null}
          existingName={
            upload === "version" ? selected?.display_name : undefined
          }
          onCancel={() => setUpload(null)}
          onUpload={async (file, name, purpose) => {
            try {
              await api.uploadResume(
                file,
                name,
                purpose,
                upload === "version" ? selected?.id : undefined,
              );
              setUpload(null);
              await refresh();
            } catch (reason) {
              setError((reason as Error).message);
            }
          }}
        />
        <CandidateReviewDialog
          candidate={review}
          onCancel={() => setReview(null)}
          onAccept={() => {
            if (review)
              void api.acceptCandidate(review.id).then(async () => {
                setReview(null);
                await refresh();
              });
          }}
          onReject={() => {
            if (review)
              void api.rejectCandidate(review.id).then(async () => {
                setReview(null);
                await refresh();
              });
          }}
        />
        <ResumeDeleteDialog
          resume={deleting ? selected : null}
          permanent={deleting === "permanent"}
          onCancel={() => setDeleting(null)}
          onConfirm={() => {
            if (!selected) return;
            const operation =
              deleting === "permanent"
                ? api.permanentlyDeleteResume(selected.id)
                : api.trashResume(selected.id);
            void operation.then(async () => {
              setDeleting(null);
              if (deleting === "permanent") setSelected(null);
              await refresh();
            });
          }}
        />
      </main>
    </AppShell>
  );
}
