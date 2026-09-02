import type { FactSummary } from "@/features/candidate/candidate-types";
import { FactStateBadge } from "./fact-state-badge";

export function FactRow({
  fact,
  onSelect,
}: {
  fact: FactSummary;
  onSelect: () => void;
}) {
  return (
    <button className="fact-row" type="button" onClick={onSelect}>
      <span>
        <strong>{fact.semantic_key}</strong>
        <small>
          Scope: {fact.scope} · Version {fact.current_version.version_number}
        </small>
      </span>
      <FactStateBadge state={fact.current_version.lifecycle_state} />
    </button>
  );
}
