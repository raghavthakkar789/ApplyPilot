import type { Opportunity } from "./discover-types";

export const opportunities: Opportunity[] = [
  {
    id: "job-001",
    title: "Senior Platform Engineer",
    employer: "Northstar Systems",
    location: "Bengaluru, India",
    workplace: "Hybrid",
    employmentType: "Full-time",
    source: "Greenhouse",
    sourceUrl: "https://example.com/jobs/job-001",
    publishedAt: "2026-09-02T08:30:00+05:30",
    group: "Today",
    roles: ["Platform Engineer", "Backend Engineer"],
    skills: ["Python", "PostgreSQL", "Docker"],
    capabilityAlignment: 82,
    preferenceCompatibility: 88,
    evidenceCoverage: 76,
    extractionConfidence: "high",
    eligibility: "compatible",
    rankingScore: 72.95,
    saved: false,
    facts: [
      { label: "Seniority", value: "Senior" },
      { label: "Work mode", value: "Hybrid · 2 days on-site" },
      { label: "Employment", value: "Full-time" },
      { label: "Language", value: "English" },
    ],
    summary:
      "Build reliable internal platforms and developer tooling for distributed product teams. The role emphasizes Python services, PostgreSQL, container operations, and pragmatic systems design.",
    verifiedMatches: [
      {
        id: "vm-1",
        label: "Python service development",
        detail: "Verified experience supports the required service work.",
        citation: "Responsibilities · paragraph 2",
      },
      {
        id: "vm-2",
        label: "PostgreSQL",
        detail:
          "Verified database experience matches the explicit requirement.",
        citation: "Requirements · bullet 3",
      },
    ],
    partialMatches: [
      {
        id: "pm-1",
        label: "Platform ownership",
        detail:
          "Verified evidence covers delivery, but not the full stated scale.",
        citation: "Responsibilities · paragraph 1",
      },
    ],
    missingEvidence: [
      {
        id: "me-1",
        label: "Container orchestration operations",
        detail:
          "No eligible verified fact currently evaluates this requirement.",
        citation: "Requirements · bullet 5",
      },
    ],
    verifiedGaps: [],
    uncertainties: [
      {
        id: "un-1",
        label: "On-call frequency",
        detail: "The posting does not state the expected rotation frequency.",
        citation: "Posting · not specified",
      },
    ],
    confirmedBlockers: [],
    ownerActions: [
      {
        id: "oa-1",
        label: "Confirm current location",
        detail: "Location confirmation is due before application preparation.",
        citation: "Candidate fact policy · 90 days",
      },
    ],
    possibleRelevance: [
      {
        id: "pr-1",
        label: "Infrastructure automation",
        detail:
          "An inferred signal may improve discovery recall but does not affect alignment.",
        citation: "Possible relevance · matching only",
      },
    ],
  },
  {
    id: "job-002",
    title: "Backend Engineer",
    employer: "Atlas Ledger",
    location: "Remote · India",
    workplace: "Remote",
    employmentType: "Full-time",
    source: "Lever",
    sourceUrl: "https://example.com/jobs/job-002",
    publishedAt: "2026-09-02T07:10:00+05:30",
    group: "Today",
    roles: ["Backend Engineer"],
    skills: ["TypeScript", "PostgreSQL", "APIs"],
    capabilityAlignment: 74,
    preferenceCompatibility: 94,
    evidenceCoverage: 68,
    extractionConfidence: "medium",
    eligibility: "unclear",
    rankingScore: 64.68,
    saved: true,
    facts: [
      { label: "Seniority", value: "Mid–Senior" },
      { label: "Work mode", value: "Remote in India" },
      { label: "Employment", value: "Full-time" },
      { label: "Compensation", value: "Unknown" },
    ],
    summary:
      "Design typed APIs and data services for a financial operations product. The posting is explicit about technical work but does not fully explain its employment-location restrictions.",
    verifiedMatches: [
      {
        id: "vm-3",
        label: "API design",
        detail: "Verified API delivery evidence matches the requirement.",
        citation: "Requirements · bullet 1",
      },
    ],
    partialMatches: [
      {
        id: "pm-2",
        label: "TypeScript depth",
        detail:
          "Verified evidence is relevant but narrower than the stated scope.",
        citation: "Requirements · bullet 2",
      },
    ],
    missingEvidence: [
      {
        id: "me-2",
        label: "Financial systems domain",
        detail:
          "No verified evidence evaluates the preferred domain requirement.",
        citation: "Preferred · bullet 1",
      },
    ],
    verifiedGaps: [],
    uncertainties: [
      {
        id: "un-2",
        label: "Remote eligibility",
        detail:
          "The phrase “Remote · India” does not specify residency or payroll constraints.",
        citation: "Location · header",
      },
    ],
    confirmedBlockers: [],
    ownerActions: [
      {
        id: "oa-2",
        label: "Review remote eligibility",
        detail:
          "Owner review is required because posting language is ambiguous.",
        citation: "Eligibility rule · unclear",
      },
    ],
    possibleRelevance: [],
  },
  {
    id: "job-003",
    title: "Developer Experience Engineer",
    employer: "Juniper Works",
    location: "Berlin, Germany",
    workplace: "On-site",
    employmentType: "Full-time",
    source: "Ashby",
    sourceUrl: "https://example.com/jobs/job-003",
    publishedAt: "2026-09-01T18:15:00+05:30",
    group: "Yesterday",
    roles: ["Platform Engineer", "Developer Experience"],
    skills: ["Python", "Docker", "CI/CD"],
    capabilityAlignment: 79,
    preferenceCompatibility: 52,
    evidenceCoverage: 71,
    extractionConfidence: "high",
    eligibility: "blocked",
    rankingScore: 64.08,
    saved: false,
    facts: [
      { label: "Seniority", value: "Senior" },
      { label: "Work mode", value: "On-site" },
      { label: "Employment", value: "Full-time" },
      { label: "Language", value: "English" },
    ],
    summary:
      "Improve build systems, local development, and continuous delivery for engineering teams. The role requires physical presence in Berlin from the start date.",
    verifiedMatches: [
      {
        id: "vm-4",
        label: "Developer tooling",
        detail: "Verified tooling work supports the core responsibility.",
        citation: "Responsibilities · bullet 1",
      },
    ],
    partialMatches: [],
    missingEvidence: [],
    verifiedGaps: [
      {
        id: "vg-1",
        label: "Mandatory work location",
        detail:
          "A current verified fact directly contradicts the mandatory on-site start requirement.",
        citation: "Requirements · mandatory location",
      },
    ],
    uncertainties: [],
    confirmedBlockers: [
      {
        id: "cb-1",
        label: "On-site in Berlin at start",
        detail:
          "The posting is explicit and current verified relocation availability contradicts it.",
        citation: "Requirements · bullet 6 + verified fact cf-042",
      },
    ],
    ownerActions: [
      {
        id: "oa-3",
        label: "Inspect blocker evidence",
        detail:
          "The job remains searchable; an override changes view preference only.",
        citation: "D-019 blocker rule",
      },
    ],
    possibleRelevance: [],
  },
  {
    id: "job-004",
    title: "Cloud Engineering Intern",
    employer: "Harbor Research",
    location: "Worldwide",
    workplace: "Remote",
    employmentType: "Internship",
    source: "Remotive",
    sourceUrl: "https://example.com/jobs/job-004",
    publishedAt: "2026-08-30T12:00:00+05:30",
    group: "Earlier this week",
    roles: ["Cloud Engineer"],
    skills: ["Linux", "Python"],
    capabilityAlignment: null,
    preferenceCompatibility: 80,
    evidenceCoverage: 34,
    extractionConfidence: "low",
    eligibility: "unclear",
    rankingScore: 0,
    saved: false,
    facts: [
      { label: "Seniority", value: "Internship" },
      { label: "Work mode", value: "Remote" },
      { label: "Employment", value: "Internship" },
      { label: "Working hours", value: "Unknown" },
    ],
    summary:
      "Support cloud research prototypes and documentation. The available posting contains limited requirements, so precise combined alignment is intentionally suppressed.",
    verifiedMatches: [],
    partialMatches: [],
    missingEvidence: [
      {
        id: "me-4",
        label: "Cloud platform exposure",
        detail:
          "The requirement cannot be evaluated from eligible verified facts.",
        citation: "Requirements · bullet 1",
      },
    ],
    verifiedGaps: [],
    uncertainties: [
      {
        id: "un-4",
        label: "Working hours",
        detail: "Timezone overlap is not specified.",
        citation: "Posting · not specified",
      },
    ],
    confirmedBlockers: [],
    ownerActions: [
      {
        id: "oa-4",
        label: "Add or verify evidence",
        detail:
          "More verified facts are needed before a precise combined alignment can be displayed.",
        citation: "Evidence coverage · 34%",
      },
    ],
    possibleRelevance: [
      {
        id: "pr-4",
        label: "Linux tooling",
        detail:
          "Possible relevance is inferred and excluded from verified capability alignment.",
        citation: "Possible relevance · matching only",
      },
    ],
  },
];
