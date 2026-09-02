// Generated-contract output from the FastAPI OpenAPI schema. Do not edit by hand.
export type FactState =
  "unverified" | "verified" | "stale" | "conflicted" | "revoked";
export interface ProfileSections {
  identity: Record<string, unknown>;
  contact: Record<string, unknown>;
  current_location: Record<string, unknown>;
  professional_summary: Record<string, unknown>;
  desired_roles: Record<string, unknown>[];
  skills: Record<string, unknown>[];
  employment_history: Record<string, unknown>[];
  education: Record<string, unknown>[];
  projects: Record<string, unknown>[];
  certifications: Record<string, unknown>[];
  languages: Record<string, unknown>[];
  portfolio_links: Record<string, unknown>[];
  work_preferences: Record<string, unknown>;
  availability: Record<string, unknown>;
  compensation: Record<string, unknown>;
  relocation: Record<string, unknown>;
  work_authorization: Record<string, unknown>;
}
export interface ProfileResponse {
  sections: ProfileSections;
  created_at: string | null;
  updated_at: string | null;
}
export interface FactVersion {
  id: string;
  version_number: number;
  value: unknown;
  lifecycle_state: FactState;
  source_type: string;
  source_reference: string | null;
  source_version: string | null;
  evidence_citation: string | null;
  created_at: string;
  owner_confirmed_at: string | null;
  reconfirmation_policy: string;
  confirmation_due_at: string | null;
  sensitivity: string;
  current: boolean;
}
export interface FactSummary {
  identity_id: string;
  fact_type: string;
  semantic_key: string;
  scope: string;
  current_version: FactVersion;
}
export interface FactDetail extends FactSummary {
  versions: FactVersion[];
}
export interface ConflictSummary {
  id: string;
  semantic_key: string;
  status: string;
  detected_at: string;
}
export interface ConflictDetail extends ConflictSummary {
  members: FactVersion[];
}
