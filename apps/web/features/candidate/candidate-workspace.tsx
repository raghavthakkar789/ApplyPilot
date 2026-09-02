"use client";

import { Plus } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { FactHistory } from "@/components/evidence/fact-history";
import {
  FactEditorDialog,
  type FactDraft,
} from "@/components/evidence/fact-editor-dialog";
import { ConflictResolutionDialog } from "@/components/evidence/conflict-resolution-dialog";
import { FactList } from "@/components/evidence/fact-list";
import { ReconfirmationDialog } from "@/components/evidence/reconfirmation-dialog";
import { RevocationDialog } from "@/components/evidence/revocation-dialog";
import { VerificationDialog } from "@/components/evidence/verification-dialog";
import { AppShell } from "@/components/layout/app-shell";
import { ProfileEditor } from "@/components/profile/profile-editor";
import * as api from "./candidate-api";
import type {
  FactDetail,
  FactSummary,
  ConflictDetail,
  ConflictSummary,
  ProfileResponse,
} from "./candidate-types";

export function CandidateWorkspace({ view }: { view: "profile" | "evidence" }) {
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [facts, setFacts] = useState<FactSummary[]>([]);
  const [selected, setSelected] = useState<FactDetail | null>(null);
  const [conflicts, setConflicts] = useState<ConflictSummary[]>([]);
  const [selectedConflict, setSelectedConflict] =
    useState<ConflictDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dialog, setDialog] = useState<
    "create" | "edit" | "verify" | "reconfirm" | "revoke" | "conflict" | null
  >(null);
  const loadFacts = useCallback(async () => {
    const [nextFacts, nextConflicts] = await Promise.all([
      api.listFacts(),
      api.listConflicts(),
    ]);
    setFacts(nextFacts);
    setConflicts(nextConflicts);
  }, []);
  useEffect(() => {
    const pending = window.setTimeout(() => {
      const load =
        view === "profile" ? api.readProfile().then(setProfile) : loadFacts();
      void load.catch((reason: Error) => setError(reason.message));
    }, 0);
    return () => window.clearTimeout(pending);
  }, [view, loadFacts]);
  const refreshSelected = async () => {
    await loadFacts();
    if (selected) setSelected(await api.readFact(selected.identity_id));
  };
  return (
    <AppShell>
      <main className="candidate-workspace">
        <header className="candidate-header">
          <p className="eyebrow">Candidate record</p>
          <h1>{view === "profile" ? "Profile" : "Evidence"}</h1>
          <p>
            {view === "profile"
              ? "Organize application information without implying verification."
              : "Inspect provenance and deliberately confirm exact fact versions."}
          </p>
        </header>
        {error && (
          <div role="alert" className="candidate-error">
            {error}
          </div>
        )}
        {view === "profile" && profile && (
          <ProfileEditor
            sections={profile.sections}
            onSave={async (sections) =>
              setProfile(await api.updateProfile(sections))
            }
          />
        )}
        {view === "evidence" && (
          <div className="evidence-layout">
            <section className="evidence-list-pane">
              <div className="evidence-toolbar">
                <h2>Candidate facts</h2>
                <button
                  type="button"
                  aria-label="Add candidate fact"
                  onClick={() => setDialog("create")}
                >
                  <Plus aria-hidden="true" /> Add fact
                </button>
              </div>
              <FactList
                facts={facts}
                onSelect={(id) =>
                  void api
                    .readFact(id)
                    .then(setSelected)
                    .catch((reason: Error) => setError(reason.message))
                }
              />
              {conflicts.length > 0 && (
                <section
                  className="conflict-list"
                  aria-labelledby="conflicts-heading"
                >
                  <h2 id="conflicts-heading">
                    Conflicts requiring owner action
                  </h2>
                  {conflicts.map((conflict) => (
                    <button
                      key={conflict.id}
                      type="button"
                      onClick={() => {
                        void api.readConflict(conflict.id).then((detail) => {
                          setSelectedConflict(detail);
                          setDialog("conflict");
                        });
                      }}
                    >
                      <strong>{conflict.semantic_key}</strong>
                      <span>Inspect competing values</span>
                    </button>
                  ))}
                </section>
              )}
            </section>
            <section className="evidence-detail-pane">
              {selected ? (
                <>
                  <header>
                    <p className="eyebrow">{selected.fact_type}</p>
                    <h2>{selected.semantic_key}</h2>
                    <p>Scope: {selected.scope}</p>
                    <div className="evidence-actions">
                      <button onClick={() => setDialog("edit")}>
                        Edit as new version
                      </button>
                      {selected.current_version.lifecycle_state ===
                        "unverified" && (
                        <button
                          className="primary-action"
                          onClick={() => setDialog("verify")}
                        >
                          Verify
                        </button>
                      )}
                      {(["verified", "stale"] as string[]).includes(
                        selected.current_version.lifecycle_state,
                      ) && (
                        <button onClick={() => setDialog("reconfirm")}>
                          Reconfirm
                        </button>
                      )}
                      {selected.current_version.lifecycle_state !==
                        "revoked" && (
                        <button
                          className="danger-action"
                          onClick={() => setDialog("revoke")}
                        >
                          Revoke
                        </button>
                      )}
                    </div>
                  </header>
                  <p className="provenance">
                    Source: {selected.current_version.source_type}
                    {selected.current_version.evidence_citation
                      ? ` · ${selected.current_version.evidence_citation}`
                      : ""}
                  </p>
                  {selected.current_version.confirmation_due_at && (
                    <p className="due-date">
                      Confirmation due{" "}
                      {new Date(
                        selected.current_version.confirmation_due_at,
                      ).toLocaleDateString()}
                    </p>
                  )}
                  <FactHistory versions={selected.versions} />
                </>
              ) : (
                <div className="candidate-empty">
                  <h2>Select a fact</h2>
                  <p>
                    Review its exact value, state, provenance, confirmation
                    timing, and immutable history.
                  </p>
                </div>
              )}
            </section>
          </div>
        )}
        <VerificationDialog
          open={dialog === "verify"}
          onCancel={() => setDialog(null)}
          onConfirm={() => {
            if (selected)
              void api
                .verifyFact(selected.current_version.id)
                .then(refreshSelected);
            setDialog(null);
          }}
        />
        <FactEditorDialog
          key={`${dialog}-${selected?.identity_id ?? "new"}`}
          open={dialog === "create" || dialog === "edit"}
          existing={dialog === "edit" ? selected : null}
          onCancel={() => setDialog(null)}
          onConfirm={(draft: FactDraft) => {
            const operation =
              selected && dialog === "edit"
                ? api.editFact(selected.identity_id, draft)
                : api.createFact(draft);
            void operation
              .then(async (fact) => {
                await loadFacts();
                setSelected(await api.readFact(fact.identity_id));
              })
              .catch((reason: Error) => setError(reason.message));
            setDialog(null);
          }}
        />
        <ReconfirmationDialog
          open={dialog === "reconfirm"}
          onCancel={() => setDialog(null)}
          onConfirm={() => {
            if (selected)
              void api
                .reconfirmFact(selected.current_version.id)
                .then(refreshSelected);
            setDialog(null);
          }}
        />
        <RevocationDialog
          open={dialog === "revoke"}
          onCancel={() => setDialog(null)}
          onConfirm={(reason) => {
            if (selected)
              void api
                .revokeFact(selected.current_version.id, reason)
                .then(refreshSelected);
            setDialog(null);
          }}
        />
        <ConflictResolutionDialog
          conflict={dialog === "conflict" ? selectedConflict : null}
          onCancel={() => setDialog(null)}
          onConfirm={(version, reason) => {
            if (selectedConflict) {
              void api
                .resolveConflict(selectedConflict.id, version, reason)
                .then(loadFacts)
                .catch((failure: Error) => setError(failure.message));
            }
            setDialog(null);
          }}
        />
      </main>
    </AppShell>
  );
}
