import { csrfHeaders } from "@/lib/csrf-client";
import type {
  ConflictDetail,
  ConflictSummary,
  FactDetail,
  FactSummary,
  ProfileResponse,
  ProfileSections,
} from "./candidate-types";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { credentials: "same-origin", ...init });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as {
      detail?: string;
    };
    throw new Error(body.detail ?? "The request could not be completed.");
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

const mutationHeaders = () => ({
  "Content-Type": "application/json",
  ...csrfHeaders(),
});

export const readProfile = () => request<ProfileResponse>("/api/profile");
export const updateProfile = (sections: ProfileSections) =>
  request<ProfileResponse>("/api/profile", {
    method: "PUT",
    headers: mutationHeaders(),
    body: JSON.stringify(sections),
  });
export const listFacts = async () =>
  (await request<{ facts: FactSummary[] }>("/api/candidate-facts")).facts;
export const readFact = (id: string) =>
  request<FactDetail>(`/api/candidate-facts/${encodeURIComponent(id)}`);
export const createFact = (payload: object) =>
  request<FactSummary>("/api/candidate-facts", {
    method: "POST",
    headers: mutationHeaders(),
    body: JSON.stringify(payload),
  });
export const editFact = (identityId: string, payload: object) =>
  request<FactSummary>(
    `/api/candidate-facts/${encodeURIComponent(identityId)}/versions`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify(payload),
    },
  );
export const verifyFact = (id: string) =>
  request(`/api/candidate-facts/versions/${encodeURIComponent(id)}/verify`, {
    method: "POST",
    headers: csrfHeaders(),
  });
export const reconfirmFact = (id: string) =>
  request(`/api/candidate-facts/versions/${encodeURIComponent(id)}/reconfirm`, {
    method: "POST",
    headers: csrfHeaders(),
  });
export const revokeFact = (id: string, reason: string) =>
  request(`/api/candidate-facts/versions/${encodeURIComponent(id)}/revoke`, {
    method: "POST",
    headers: mutationHeaders(),
    body: JSON.stringify({ reason }),
  });
export const listConflicts = async () =>
  (
    await request<{ conflicts: ConflictSummary[] }>(
      "/api/candidate-fact-conflicts",
    )
  ).conflicts;
export const readConflict = (id: string) =>
  request<ConflictDetail>(
    `/api/candidate-fact-conflicts/${encodeURIComponent(id)}`,
  );
export const resolveConflict = (
  id: string,
  selectedVersionId: string,
  reason: string,
) =>
  request(`/api/candidate-fact-conflicts/${encodeURIComponent(id)}/resolve`, {
    method: "POST",
    headers: mutationHeaders(),
    body: JSON.stringify({ selected_version_id: selectedVersionId, reason }),
  });
