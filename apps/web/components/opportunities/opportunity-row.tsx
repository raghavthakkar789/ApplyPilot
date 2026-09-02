import { Bookmark } from "lucide-react";
import type { Opportunity } from "@/features/discover/discover-types";
import { EligibilityStatus } from "@/components/matching/eligibility-status";

interface Props {
  opportunity: Opportunity;
  selected: boolean;
  rank: number;
  onSelect: () => void;
  onSave: () => void;
}

export function OpportunityRow({
  opportunity,
  selected,
  rank,
  onSelect,
  onSave,
}: Props) {
  const insufficient = opportunity.evidenceCoverage < 40;
  return (
    <article
      className="opportunity-row"
      data-selected={selected}
      aria-label={`${opportunity.title} at ${opportunity.employer}`}
    >
      <button
        className="row-select"
        type="button"
        aria-label={`${opportunity.title} at ${opportunity.employer}`}
        aria-pressed={selected}
        onClick={onSelect}
      >
        <span className="rank" aria-label={`Rank ${rank}`}>
          {String(rank).padStart(2, "0")}
        </span>
        <span className="row-copy">
          <strong>{opportunity.title}</strong>
          <span>{opportunity.employer}</span>
          <small>
            {opportunity.location} · {opportunity.workplace}
          </small>
          <span className="row-metrics">
            {opportunity.matchEvaluated === false ? <b>Not evaluated</b> : null}
            {opportunity.matchEvaluated !== false && (
              <>
                {insufficient ? (
                  <b>Insufficient evidence</b>
                ) : (
                  <b>{opportunity.capabilityAlignment}% capability</b>
                )}
                <span>{opportunity.evidenceCoverage}% evidence</span>
                <EligibilityStatus status={opportunity.eligibility} compact />
              </>
            )}
          </span>
        </span>
      </button>
      <button
        className="save-button"
        type="button"
        aria-label={
          opportunity.saved
            ? `Unsave ${opportunity.title}`
            : `Save ${opportunity.title}`
        }
        aria-pressed={opportunity.saved}
        onClick={onSave}
      >
        <Bookmark
          aria-hidden="true"
          fill={opportunity.saved ? "currentColor" : "none"}
          size={18}
        />
      </button>
    </article>
  );
}
