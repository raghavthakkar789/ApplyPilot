import type { FactCandidate } from "@/features/resumes/resume-types";
import { FactCandidateRow } from "./fact-candidate-row";

export function FactCandidateList({
  candidates,
  onReview,
}: {
  candidates: FactCandidate[];
  onReview: (candidate: FactCandidate) => void;
}) {
  return (
    <section className="resume-card" aria-labelledby="candidate-list-heading">
      <h3 id="candidate-list-heading">Fact candidates</h3>
      <p>
        Parsing creates review candidates only. Accepting one creates an
        unverified fact; verification remains a separate action in Evidence.
      </p>
      {candidates.length ? (
        candidates.map((candidate) => (
          <FactCandidateRow
            key={candidate.id}
            candidate={candidate}
            onReview={() => onReview(candidate)}
          />
        ))
      ) : (
        <p>
          No deterministic fact candidates were identified. Select from the
          extracted text manually.
        </p>
      )}
    </section>
  );
}
