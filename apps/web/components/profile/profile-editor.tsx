"use client";

import { useState } from "react";
import type { ProfileSections } from "@/features/candidate/candidate-types";
import { ProfileField } from "./profile-field";
import { ProfileSection } from "./profile-section";

export function ProfileEditor({
  sections,
  onSave,
}: {
  sections: ProfileSections;
  onSave: (sections: ProfileSections) => Promise<void>;
}) {
  const [draft, setDraft] = useState(sections);
  const [saving, setSaving] = useState(false);
  const field = (
    section: "identity" | "contact" | "current_location",
    key: string,
  ) => String(draft[section][key] ?? "");
  const update = (
    section: "identity" | "contact" | "current_location",
    key: string,
    value: string,
  ) =>
    setDraft((current) => ({
      ...current,
      [section]: { ...current[section], [key]: value },
    }));
  return (
    <form
      className="profile-editor"
      onSubmit={(event) => {
        event.preventDefault();
        setSaving(true);
        void onSave(draft).finally(() => setSaving(false));
      }}
    >
      <ProfileSection
        title="Application identity"
        description="Information you deliberately use on applications."
      >
        <ProfileField
          label="Preferred name"
          value={field("identity", "preferred_name")}
          onChange={(v) => update("identity", "preferred_name", v)}
        />
        <ProfileField
          label="Current role"
          value={field("identity", "current_role")}
          onChange={(v) => update("identity", "current_role", v)}
        />
      </ProfileSection>
      <ProfileSection
        title="Contact and location"
        description="Current details require confirmation every 90 days."
      >
        <ProfileField
          label="Email"
          value={field("contact", "email")}
          onChange={(v) => update("contact", "email", v)}
        />
        <ProfileField
          label="City and country"
          value={field("current_location", "label")}
          onChange={(v) => update("current_location", "label", v)}
        />
      </ProfileSection>
      <p className="form-note">
        Saving profile structure does not verify candidate facts. Verification
        is a separate owner action in Evidence.
      </p>
      <button className="primary-action" disabled={saving} type="submit">
        {saving ? "Saving…" : "Save profile"}
      </button>
    </form>
  );
}
