import {
  CircleAlert,
  CircleCheck,
  CircleDashed,
  CircleDot,
} from "lucide-react";
import type { EvidenceItem } from "@/features/discover/discover-types";

export function FactorList({
  items,
  tone = "neutral",
  emptyText = "None identified in current evidence.",
}: {
  items: EvidenceItem[];
  tone?: "success" | "warning" | "danger" | "neutral";
  emptyText?: string;
}) {
  const Icon =
    tone === "success"
      ? CircleCheck
      : tone === "danger"
        ? CircleAlert
        : tone === "warning"
          ? CircleDot
          : CircleDashed;
  if (!items.length) return <p className="factor-empty">{emptyText}</p>;
  return (
    <ul className="factor-list">
      {items.map((item) => (
        <li key={item.id} data-tone={tone}>
          <Icon aria-hidden="true" size={17} />
          <div>
            <strong>{item.label}</strong>
            <p>{item.detail}</p>
            <small>{item.citation}</small>
          </div>
        </li>
      ))}
    </ul>
  );
}
