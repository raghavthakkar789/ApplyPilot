import { csrfHeaders } from "@/lib/csrf-client";
import type {
  Extraction,
  FactCandidate,
  ResumeDetail,
  ResumeRecord,
} from "./resume-types";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { credentials: "same-origin", ...init });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as {
      detail?: string;
      error?: { message?: string };
    };
    throw new Error(
      body.detail ??
        body.error?.message ??
        "The request could not be completed.",
    );
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const listResumes = async () =>
  (await request<{ resumes: ResumeRecord[] }>("/api/resumes")).resumes;
export const readResume = (id: string) =>
  request<ResumeDetail>(`/api/resumes/${encodeURIComponent(id)}`);
export const readExtraction = (versionId: string) =>
  request<Extraction>(
    `/api/resumes/versions/${encodeURIComponent(versionId)}/extraction`,
  );
export const listCandidates = async (versionId: string) =>
  (
    await request<{ candidates: FactCandidate[] }>(
      `/api/resume-versions/${encodeURIComponent(versionId)}/fact-candidates`,
    )
  ).candidates;
export async function uploadResume(
  file: File,
  displayName: string,
  purpose?: string,
  resumeId?: string,
) {
  const form = new FormData();
  form.set("file", file);
  if (!resumeId) {
    form.set("display_name", displayName);
    if (purpose) form.set("purpose", purpose);
  }
  const url = resumeId
    ? `/api/resumes/${encodeURIComponent(resumeId)}/versions`
    : "/api/resumes";
  return request<ResumeRecord>(url, {
    method: "POST",
    headers: csrfHeaders(),
    body: form,
  });
}
export const acceptCandidate = (id: string) =>
  request(`/api/resume-fact-candidates/${encodeURIComponent(id)}/accept`, {
    method: "POST",
    headers: csrfHeaders(),
  });
export const rejectCandidate = (id: string) =>
  request(`/api/resume-fact-candidates/${encodeURIComponent(id)}/reject`, {
    method: "POST",
    headers: csrfHeaders(),
  });
export const trashResume = (id: string) =>
  request(`/api/resumes/${encodeURIComponent(id)}/trash`, {
    method: "POST",
    headers: csrfHeaders(),
  });
export const restoreResume = (id: string) =>
  request(`/api/resumes/${encodeURIComponent(id)}/restore`, {
    method: "POST",
    headers: csrfHeaders(),
  });
export const permanentlyDeleteResume = (id: string) =>
  request(`/api/resumes/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: csrfHeaders(),
  });
