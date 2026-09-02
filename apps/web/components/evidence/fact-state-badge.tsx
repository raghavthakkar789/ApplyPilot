import type { FactState } from "@/features/candidate/candidate-types";

export function FactStateBadge({ state }: { state: FactState }) {
  return (
    <span className="fact-state" data-state={state}>
      {state}
    </span>
  );
}
