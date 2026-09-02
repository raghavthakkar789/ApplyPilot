import type { FactSummary } from "@/features/candidate/candidate-types";
import { FactRow } from "./fact-row";

export function FactList({
  facts,
  onSelect,
}: {
  facts: FactSummary[];
  onSelect: (id: string) => void;
}) {
  if (!facts.length)
    return (
      <p className="candidate-empty">
        No candidate facts yet. New entries begin unverified.
      </p>
    );
  return (
    <div className="fact-list">
      {facts.map((fact) => (
        <FactRow
          key={fact.identity_id}
          fact={fact}
          onSelect={() => onSelect(fact.identity_id)}
        />
      ))}
    </div>
  );
}
