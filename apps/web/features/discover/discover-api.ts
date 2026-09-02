import { csrfHeaders } from "@/lib/csrf-client";
import type { Opportunity } from "./discover-types";

interface ApiJob {
  id: string;
  title: string;
  employer: string;
  description: string;
  location: string | null;
  work_mode: string | null;
  employment_type: string | null;
  freshness_state: string;
  saved: boolean;
  created_at: string;
  sources: {
    provider: string;
    source_url: string;
    attribution: string;
    retrieved_at: string;
  }[];
}

const emptyEvidence: never[] = [];

function opportunity(job: ApiJob): Opportunity {
  const source = job.sources[0];
  const provider = source?.provider ?? "manual";
  const sourceName =
    provider === "manual"
      ? "Manual"
      : `${provider[0].toUpperCase()}${provider.slice(1)}`;
  return {
    id: job.id,
    title: job.title,
    employer: job.employer,
    location: job.location ?? "Location unknown",
    workplace:
      job.work_mode === "remote"
        ? "Remote"
        : job.work_mode === "hybrid"
          ? "Hybrid"
          : "On-site",
    employmentType:
      job.employment_type === "contract"
        ? "Contract"
        : job.employment_type === "internship"
          ? "Internship"
          : "Full-time",
    source: sourceName as Opportunity["source"],
    sourceUrl:
      source?.source_url === "manual-entry" ? "#" : (source?.source_url ?? "#"),
    publishedAt: source?.retrieved_at ?? job.created_at,
    group: "Today",
    roles: [],
    skills: [],
    capabilityAlignment: null,
    preferenceCompatibility: 0,
    evidenceCoverage: 0,
    extractionConfidence: "low",
    eligibility: "unclear",
    rankingScore: 0,
    saved: job.saved,
    facts: [
      { label: "Freshness", value: job.freshness_state.replaceAll("_", " ") },
    ],
    summary: job.description || "No description was supplied by this source.",
    verifiedMatches: emptyEvidence,
    partialMatches: emptyEvidence,
    missingEvidence: emptyEvidence,
    verifiedGaps: emptyEvidence,
    uncertainties: emptyEvidence,
    confirmedBlockers: emptyEvidence,
    ownerActions: emptyEvidence,
    possibleRelevance: emptyEvidence,
    matchEvaluated: false,
    freshnessState: job.freshness_state,
    attribution: source?.attribution,
  };
}

export interface CatalogResult {
  jobs: Opportunity[];
  partialFailures: string[];
}

export async function loadJobs(): Promise<CatalogResult> {
  const response = await fetch("/api/jobs", { credentials: "same-origin" });
  if (!response.ok) throw new Error("Jobs could not be loaded.");
  const payload = (await response.json()) as {
    jobs: ApiJob[];
    partial_failures: string[];
  };
  return {
    jobs: payload.jobs.map(opportunity),
    partialFailures: payload.partial_failures,
  };
}

export async function setJobSaved(id: string, saved: boolean): Promise<void> {
  const response = await fetch(`/api/jobs/${id}/save`, {
    method: saved ? "POST" : "DELETE",
    credentials: "same-origin",
    headers: csrfHeaders(),
  });
  if (!response.ok) throw new Error("Save state could not be updated.");
}
