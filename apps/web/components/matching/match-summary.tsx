import { BarChart3, FileSearch, Gauge, SlidersHorizontal } from "lucide-react";
import type { Opportunity } from "@/features/discover/discover-types";
import { AlignmentMetric } from "./alignment-metric";
import { EligibilityStatus } from "./eligibility-status";

export function MatchSummary({ job }: { job: Opportunity }) {
  if (job.matchEvaluated === false) {
    return (
      <section className="match-summary" aria-labelledby="match-summary-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Candidate match information</p>
            <h3 id="match-summary-title">Not evaluated</h3>
          </div>
        </div>
        <p>
          Matching is not calculated by the job catalog. Job facts and candidate
          evidence remain separate.
        </p>
      </section>
    );
  }
  const insufficient = job.evidenceCoverage < 40;
  return (
    <section className="match-summary" aria-labelledby="match-summary-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Transparent matching</p>
          <h3 id="match-summary-title">Alignment summary</h3>
        </div>
        <span>Rules v1 · Weights v1</span>
      </div>
      <div className="metric-grid">
        <AlignmentMetric
          label="Capability alignment"
          value={
            insufficient
              ? "Insufficient evidence"
              : `${job.capabilityAlignment}%`
          }
          detail={
            insufficient
              ? "Below 40% capability coverage"
              : "Evaluable verified requirements"
          }
          icon={<Gauge aria-hidden="true" />}
        />
        <AlignmentMetric
          label="Preference compatibility"
          value={`${job.preferenceCompatibility}%`}
          detail="Known preferences only"
          icon={<SlidersHorizontal aria-hidden="true" />}
        />
        <div className="metric">
          <span className="metric-label">
            <BarChart3 aria-hidden="true" />
            Eligibility
          </span>
          <EligibilityStatus status={job.eligibility} />
          <small>Separate from numerical alignment</small>
        </div>
        <AlignmentMetric
          label="Evidence coverage"
          value={`${job.evidenceCoverage}%`}
          detail="Weighted evaluable requirements"
          icon={<FileSearch aria-hidden="true" />}
        />
        <AlignmentMetric
          label="Extraction confidence"
          value={
            job.extractionConfidence[0].toUpperCase() +
            job.extractionConfidence.slice(1)
          }
          detail="Posting parsing confidence"
        />
      </div>
    </section>
  );
}
