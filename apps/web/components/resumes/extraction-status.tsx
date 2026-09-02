import { CheckCircle2, Clock3, TriangleAlert } from "lucide-react";
import type { ExtractionStatus as Status } from "@/features/resumes/resume-types";

export function ExtractionStatus({ status }: { status: Status }) {
  const Icon =
    status === "succeeded"
      ? CheckCircle2
      : status === "failed"
        ? TriangleAlert
        : Clock3;
  return (
    <span className={`resume-status status-${status}`}>
      <Icon aria-hidden="true" size={16} />
      {status === "succeeded"
        ? "Extraction complete"
        : status === "failed"
          ? "Extraction failed"
          : "Extraction pending"}
    </span>
  );
}
