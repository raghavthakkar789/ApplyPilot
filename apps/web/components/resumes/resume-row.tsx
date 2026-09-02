import { FileText, Trash2 } from "lucide-react";
import type { ResumeRecord } from "@/features/resumes/resume-types";
import { ExtractionStatus } from "./extraction-status";

export function ResumeRow({
  resume,
  selected,
  onSelect,
}: {
  resume: ResumeRecord;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      className="resume-row"
      aria-pressed={selected}
      onClick={onSelect}
    >
      {resume.trashed_at ? (
        <Trash2 aria-hidden="true" />
      ) : (
        <FileText aria-hidden="true" />
      )}
      <span>
        <strong>{resume.display_name}</strong>
        <small>
          {resume.trashed_at
            ? "In trash"
            : `Version ${resume.current_version?.version_number ?? 0}`}
        </small>
      </span>
      {resume.current_version && (
        <ExtractionStatus status={resume.current_version.extraction_status} />
      )}
    </button>
  );
}
