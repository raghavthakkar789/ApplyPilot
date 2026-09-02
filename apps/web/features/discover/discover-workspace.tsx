"use client";

import { Menu, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { JobDetailHeader } from "@/components/opportunities/job-detail-header";
import { OpportunityList } from "@/components/opportunities/opportunity-list";
import { OpportunityToolbar } from "@/components/opportunities/opportunity-toolbar";
import { EvidenceSection } from "@/components/matching/evidence-section";
import { FactorList } from "@/components/matching/factor-list";
import { MatchSummary } from "@/components/matching/match-summary";
import { opportunities as initialOpportunities } from "./discover-data";
import type { DiscoverFilters } from "./discover-types";
import { SessionExpiryWarning } from "@/components/auth/session-expiry-warning";

const emptyFilters: DiscoverFilters = {
  query: "",
  role: "",
  skill: "",
  location: "",
  source: "",
};

export function DiscoverWorkspace() {
  const [jobs, setJobs] = useState(initialOpportunities);
  const [selectedId, setSelectedId] = useState(initialOpportunities[0].id);
  const [filters, setFilters] = useState(emptyFilters);
  const [sort, setSort] = useState("ranking");
  const [mobileDetail, setMobileDetail] = useState(false);
  const [notice, setNotice] = useState("");

  const filtered = useMemo(() => {
    const query = filters.query.toLowerCase();
    const rows = jobs.filter(
      (job) =>
        (!query ||
          `${job.title} ${job.employer} ${job.skills.join(" ")}`
            .toLowerCase()
            .includes(query)) &&
        (!filters.role || job.roles.includes(filters.role)) &&
        (!filters.skill || job.skills.includes(filters.skill)) &&
        (!filters.location ||
          `${job.location} ${job.workplace}`.includes(filters.location)) &&
        (!filters.source || job.source === filters.source),
    );
    return [...rows].sort((a, b) =>
      sort === "newest"
        ? Date.parse(b.publishedAt) - Date.parse(a.publishedAt)
        : sort === "capability"
          ? (b.capabilityAlignment ?? -1) - (a.capabilityAlignment ?? -1)
          : b.rankingScore - a.rankingScore,
    );
  }, [jobs, filters, sort]);
  const selected =
    jobs.find((job) => job.id === selectedId) ?? filtered[0] ?? jobs[0];
  const toggleSave = (id: string) =>
    setJobs((current) =>
      current.map((job) =>
        job.id === id ? { ...job, saved: !job.saved } : job,
      ),
    );
  const select = (id: string) => {
    setSelectedId(id);
    setMobileDetail(true);
  };
  const activeCount = Object.values(filters).filter(Boolean).length;

  return (
    <AppShell>
      <SessionExpiryWarning />
      <main className="workspace">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">Discover workspace</p>
            <h1>Global opportunities</h1>
            <p>
              Review worldwide roles with source provenance and transparent
              match evidence.
            </p>
          </div>
          <div className="header-meta">
            <time dateTime="2026-09-02">2 September 2026</time>
            <button type="button" aria-label="Workspace options">
              <Menu aria-hidden="true" />
            </button>
          </div>
        </header>
        <OpportunityToolbar
          filters={filters}
          onChange={setFilters}
          sort={sort}
          onSort={setSort}
          activeCount={activeCount}
        />
        <div className="workspace-panes" data-mobile-detail={mobileDetail}>
          <section className="list-pane" aria-label="Opportunity results">
            <div className="pane-title">
              <span>
                <strong>{filtered.length} opportunities</strong>
                <small>Synthetic preview data</small>
              </span>
              {activeCount > 0 && (
                <button type="button" onClick={() => setFilters(emptyFilters)}>
                  Clear {activeCount} filters
                </button>
              )}
            </div>
            <OpportunityList
              opportunities={filtered}
              selectedId={selected.id}
              onSelect={select}
              onSave={toggleSave}
            />
          </section>
          <article
            className="detail-pane"
            aria-label="Selected opportunity detail"
          >
            <JobDetailHeader
              job={selected}
              onSave={() => toggleSave(selected.id)}
              onBack={() => setMobileDetail(false)}
            />
            <MatchSummary job={selected} />
            <div className="evidence-grid">
              <EvidenceSection
                title="Verified matches"
                count={selected.verifiedMatches.length}
              >
                <FactorList items={selected.verifiedMatches} tone="success" />
              </EvidenceSection>
              <EvidenceSection
                title="Partial matches"
                count={selected.partialMatches.length}
              >
                <FactorList items={selected.partialMatches} tone="warning" />
              </EvidenceSection>
              <EvidenceSection
                title="Missing evidence"
                count={selected.missingEvidence.length}
              >
                <FactorList items={selected.missingEvidence} />
              </EvidenceSection>
              <EvidenceSection
                title="Verified gaps"
                count={selected.verifiedGaps.length}
              >
                <FactorList items={selected.verifiedGaps} tone="danger" />
              </EvidenceSection>
              <EvidenceSection
                title="Uncertainties"
                count={selected.uncertainties.length}
              >
                <FactorList items={selected.uncertainties} tone="warning" />
              </EvidenceSection>
              <EvidenceSection
                title="Confirmed blockers"
                count={selected.confirmedBlockers.length}
              >
                <FactorList items={selected.confirmedBlockers} tone="danger" />
              </EvidenceSection>
              <EvidenceSection
                title="Owner actions"
                count={selected.ownerActions.length}
              >
                <FactorList items={selected.ownerActions} />
              </EvidenceSection>
              <EvidenceSection
                title="Possible relevance"
                count={selected.possibleRelevance.length}
              >
                <FactorList items={selected.possibleRelevance} />
              </EvidenceSection>
            </div>
            <section className="role-summary">
              <p className="eyebrow">Role information</p>
              <h3>Role summary</h3>
              <p>{selected.summary}</p>
              <dl>
                {selected.facts.map((fact) => (
                  <div key={fact.label}>
                    <dt>{fact.label}</dt>
                    <dd>{fact.value}</dd>
                  </div>
                ))}
              </dl>
            </section>
            <footer className="preparation-bar">
              <div>
                <ShieldCheck aria-hidden="true" />
                <span>
                  <strong>Ready to prepare?</strong>
                  <small>Preparation does not submit an application.</small>
                </span>
              </div>
              <button
                type="button"
                onClick={() =>
                  setNotice("Preparation does not submit an application.")
                }
              >
                Prepare application
              </button>
            </footer>
            {notice && (
              <p className="action-notice" role="status">
                {notice}
              </p>
            )}
          </article>
        </div>
      </main>
    </AppShell>
  );
}
