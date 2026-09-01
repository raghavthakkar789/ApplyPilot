import type { Opportunity } from "@/features/discover/discover-types";
import { OpportunityRow } from "./opportunity-row";
import { EmptyState } from "@/components/feedback/empty-state";

interface Props {
  opportunities: Opportunity[];
  selectedId: string;
  onSelect: (id: string) => void;
  onSave: (id: string) => void;
}

export function OpportunityList({
  opportunities,
  selectedId,
  onSelect,
  onSave,
}: Props) {
  if (!opportunities.length)
    return (
      <EmptyState
        title="No matching opportunities"
        detail="Adjust or clear filters to inspect more synthetic opportunities."
      />
    );
  const groups = ["Today", "Yesterday", "Earlier this week"] as const;
  return (
    <div
      className="opportunity-list"
      aria-label={`${opportunities.length} opportunities`}
    >
      {groups.map((group) => {
        const rows = opportunities.filter((job) => job.group === group);
        return rows.length ? (
          <section
            key={group}
            aria-labelledby={`group-${group.replaceAll(" ", "-")}`}
          >
            <h2 id={`group-${group.replaceAll(" ", "-")}`}>
              {group}
              <span>{rows.length}</span>
            </h2>
            {rows.map((job) => (
              <OpportunityRow
                key={job.id}
                opportunity={job}
                selected={job.id === selectedId}
                rank={opportunities.indexOf(job) + 1}
                onSelect={() => onSelect(job.id)}
                onSave={() => onSave(job.id)}
              />
            ))}
          </section>
        ) : null;
      })}
    </div>
  );
}
