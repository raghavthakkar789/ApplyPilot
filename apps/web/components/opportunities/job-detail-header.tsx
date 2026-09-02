import { ArrowLeft, Bookmark, ExternalLink } from "lucide-react";
import type { Opportunity } from "@/features/discover/discover-types";

export function JobDetailHeader({
  job,
  onSave,
  onBack,
}: {
  job: Opportunity;
  onSave: () => void;
  onBack: () => void;
}) {
  return (
    <header className="detail-header">
      <button className="back-button" type="button" onClick={onBack}>
        <ArrowLeft aria-hidden="true" size={18} />
        Back to opportunities
      </button>
      <div className="detail-actions">
        <button type="button" onClick={onSave} aria-pressed={job.saved}>
          <Bookmark
            aria-hidden="true"
            fill={job.saved ? "currentColor" : "none"}
            size={18}
          />
          {job.saved ? "Saved" : "Save for later"}
        </button>
        {job.sourceUrl === "#" ? (
          <span>
            {job.attribution ??
              "Manually entered — source not automatically verified"}
          </span>
        ) : (
          <a href={job.sourceUrl} target="_blank" rel="noreferrer">
            {job.attribution ?? `Source: ${job.source}`}
            <ExternalLink aria-hidden="true" size={15} />
          </a>
        )}
      </div>
      <p className="eyebrow">
        {job.employer} · {job.source}
      </p>
      <h2>{job.title}</h2>
      <p>
        {job.location} · {job.workplace} · {job.employmentType}
      </p>
      <time dateTime={job.publishedAt}>Retrieved 2 September 2026</time>
    </header>
  );
}
