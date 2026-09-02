import type { ResumeRecord } from "@/features/resumes/resume-types";
import { ResumeRow } from "./resume-row";

export function ResumeList({
  resumes,
  selectedId,
  onSelect,
}: {
  resumes: ResumeRecord[];
  selectedId?: string;
  onSelect: (id: string) => void;
}) {
  if (!resumes.length)
    return (
      <div className="candidate-empty">
        <h2>No resumes stored</h2>
        <p>Upload a PDF, DOCX, or UTF-8 text file to create version 1.</p>
      </div>
    );
  return (
    <div className="resume-list" aria-label="Stored resumes">
      {resumes.map((resume) => (
        <ResumeRow
          key={resume.id}
          resume={resume}
          selected={selectedId === resume.id}
          onSelect={() => onSelect(resume.id)}
        />
      ))}
    </div>
  );
}
