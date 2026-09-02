export type Eligibility = "compatible" | "unclear" | "blocked";
export type Confidence = "high" | "medium" | "low";
export type Source = "Greenhouse" | "Lever" | "Ashby" | "Remotive" | "Manual";

export interface EvidenceItem {
  id: string;
  label: string;
  detail: string;
  citation: string;
}

export interface Opportunity {
  id: string;
  title: string;
  employer: string;
  location: string;
  workplace: "Remote" | "Hybrid" | "On-site";
  employmentType: "Full-time" | "Contract" | "Internship";
  source: Source;
  sourceUrl: string;
  publishedAt: string;
  group: "Today" | "Yesterday" | "Earlier this week";
  roles: string[];
  skills: string[];
  capabilityAlignment: number | null;
  preferenceCompatibility: number;
  evidenceCoverage: number;
  extractionConfidence: Confidence;
  eligibility: Eligibility;
  rankingScore: number;
  saved: boolean;
  facts: { label: string; value: string }[];
  summary: string;
  verifiedMatches: EvidenceItem[];
  partialMatches: EvidenceItem[];
  missingEvidence: EvidenceItem[];
  verifiedGaps: EvidenceItem[];
  uncertainties: EvidenceItem[];
  confirmedBlockers: EvidenceItem[];
  ownerActions: EvidenceItem[];
  possibleRelevance: EvidenceItem[];
  matchEvaluated?: boolean;
  freshnessState?: string;
  attribution?: string;
}

export interface DiscoverFilters {
  query: string;
  role: string;
  skill: string;
  location: string;
  source: string;
  workMode: string;
  employmentType: string;
  freshness: string;
}
