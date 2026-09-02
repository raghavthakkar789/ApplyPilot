import type { ResumeVersion } from "@/features/resumes/resume-types";
import { ExtractionStatus } from "./extraction-status";

export function ResumeVersionHistory({
  versions,
}: {
  versions: ResumeVersion[];
}) {
  return (
    <section className="resume-card" aria-labelledby="version-history-heading">
      <h3 id="version-history-heading">Immutable version history</h3>
      <ol className="version-history">
        {versions.map((version) => (
          <li key={version.id}>
            <span>
              <strong>Version {version.version_number}</strong>
              <small>
                {version.filename} · {(version.byte_length / 1024).toFixed(1)}{" "}
                KiB
              </small>
            </span>
            <ExtractionStatus status={version.extraction_status} />
            <details>
              <summary>Integrity details</summary>
              <code>SHA-256 {version.sha256}</code>
              <p>
                {version.parser} {version.parser_version} ·{" "}
                {version.integrity_state}
              </p>
            </details>
          </li>
        ))}
      </ol>
    </section>
  );
}
