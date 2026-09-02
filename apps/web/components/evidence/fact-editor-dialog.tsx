import { useState } from "react";

import type { FactDetail } from "@/features/candidate/candidate-types";

export interface FactDraft {
  fact_type: string;
  semantic_key: string;
  scope: string;
  value: string;
  source_type: string;
  sensitivity: string;
  reconfirmation_policy: string;
  reason?: string;
}

const empty: FactDraft = {
  fact_type: "skill",
  semantic_key: "",
  scope: "*",
  value: "",
  source_type: "owner_entry",
  sensitivity: "standard",
  reconfirmation_policy: "stable",
};

export function FactEditorDialog({
  open,
  existing,
  onCancel,
  onConfirm,
}: {
  open: boolean;
  existing?: FactDetail | null;
  onCancel: () => void;
  onConfirm: (draft: FactDraft) => void;
}) {
  const [draft, setDraft] = useState<FactDraft>(() =>
    existing
      ? {
          fact_type: existing.fact_type,
          semantic_key: existing.semantic_key,
          scope: existing.scope,
          value: String(existing.current_version.value ?? ""),
          source_type: "owner_entry",
          sensitivity: existing.current_version.sensitivity,
          reconfirmation_policy: existing.current_version.reconfirmation_policy,
          reason: "",
        }
      : empty,
  );
  if (!open) return null;
  const update = (key: keyof FactDraft, value: string) =>
    setDraft((current) => ({ ...current, [key]: value }));
  return (
    <div className="dialog-backdrop" role="presentation">
      <form
        role="dialog"
        aria-modal="true"
        aria-labelledby="fact-editor-title"
        className="candidate-dialog"
        onSubmit={(event) => {
          event.preventDefault();
          onConfirm(draft);
        }}
      >
        <h2 id="fact-editor-title">
          {existing ? "Create a new version" : "Add candidate fact"}
        </h2>
        <p>
          {existing
            ? "The historical value remains immutable. This edit creates a new unverified version."
            : "Typed information begins unverified and needs a separate explicit confirmation."}
        </p>
        <label>
          Fact type
          <input
            required
            value={draft.fact_type}
            onChange={(event) => update("fact_type", event.target.value)}
          />
        </label>
        <label>
          Semantic key
          <input
            required
            disabled={Boolean(existing)}
            value={draft.semantic_key}
            onChange={(event) => update("semantic_key", event.target.value)}
          />
        </label>
        <label>
          Scope
          <input
            required
            value={draft.scope}
            onChange={(event) => update("scope", event.target.value)}
          />
        </label>
        <label>
          Value
          <textarea
            required
            value={draft.value}
            onChange={(event) => update("value", event.target.value)}
          />
        </label>
        <label>
          Reconfirmation
          <select
            value={draft.reconfirmation_policy}
            onChange={(event) =>
              update("reconfirmation_policy", event.target.value)
            }
          >
            <option value="stable">Stable completed history</option>
            <option value="days_90">Every 90 days</option>
            <option value="days_30">Every 30 days</option>
            <option value="per_application">Every exact application</option>
          </select>
        </label>
        {existing && (
          <label>
            Reason for new version
            <textarea
              required
              value={draft.reason}
              onChange={(event) => update("reason", event.target.value)}
            />
          </label>
        )}
        <div>
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
          <button className="primary-action" type="submit">
            {existing ? "Create unverified version" : "Add unverified fact"}
          </button>
        </div>
      </form>
    </div>
  );
}
