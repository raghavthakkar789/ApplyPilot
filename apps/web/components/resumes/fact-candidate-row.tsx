import type { FactCandidate } from "@/features/resumes/resume-types";

export function FactCandidateRow({
  candidate,
  onReview,
}: {
  candidate: FactCandidate;
  onReview: () => void;
}) {
  return (
    <article className="fact-candidate-row">
      <div>
        <span className="fact-state state-unverified">
          Unverified candidate
        </span>
        <h4>{candidate.semantic_key}</h4>
        <p>{String(candidate.proposed_value)}</p>
        <small>Evidence: {candidate.evidence_citation}</small>
      </div>
      {candidate.review_status === "pending" ? (
        <button type="button" onClick={onReview}>
          Review candidate
        </button>
      ) : (
        <span className="resume-status">{candidate.review_status}</span>
      )}
    </article>
  );
}
