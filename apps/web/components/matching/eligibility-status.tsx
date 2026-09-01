import { AlertTriangle, CheckCircle2, HelpCircle } from "lucide-react";
import type { Eligibility } from "@/features/discover/discover-types";

const labels = {
  compatible: "Compatible",
  unclear: "Unclear",
  blocked: "Blocked",
} as const;

export function EligibilityStatus({
  status,
  compact = false,
}: {
  status: Eligibility;
  compact?: boolean;
}) {
  const Icon =
    status === "compatible"
      ? CheckCircle2
      : status === "blocked"
        ? AlertTriangle
        : HelpCircle;
  return (
    <span className="eligibility" data-status={status} data-compact={compact}>
      <Icon aria-hidden="true" size={compact ? 14 : 18} />
      {labels[status]}
    </span>
  );
}
