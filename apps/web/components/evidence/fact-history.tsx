import type { FactVersion } from "@/features/candidate/candidate-types";
import { FactStateBadge } from "./fact-state-badge";

export function FactHistory({ versions }: { versions: FactVersion[] }) {
  return (
    <section className="fact-history">
      <h3>Immutable version history</h3>
      {versions.map((version) => (
        <article key={version.id}>
          <div>
            <strong>Version {version.version_number}</strong>
            {version.current && <span>Current</span>}
          </div>
          <FactStateBadge state={version.lifecycle_state} />
          <p>{JSON.stringify(version.value)}</p>
          <small>
            Source: {version.source_type} ·{" "}
            {new Date(version.created_at).toLocaleString()}
          </small>
        </article>
      ))}
    </section>
  );
}
