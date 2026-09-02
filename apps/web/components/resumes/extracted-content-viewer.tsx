import type { Extraction } from "@/features/resumes/resume-types";
import { ExtractionWarning } from "./extraction-warning";

export function ExtractedContentViewer({
  extraction,
}: {
  extraction: Extraction | null;
}) {
  return (
    <section
      className="resume-card"
      aria-labelledby="extracted-content-heading"
    >
      <h3 id="extracted-content-heading">Deterministic text extraction</h3>
      {!extraction ? (
        <p role="status">Loading extracted content…</p>
      ) : (
        <>
          {extraction.warnings.map((warning) => (
            <ExtractionWarning key={warning} message={warning} />
          ))}
          {extraction.segments.length ? (
            <div className="extracted-text" tabIndex={0}>
              {extraction.segments.map((segment) => (
                <section
                  key={`${segment.citation}-${segment.text.slice(0, 20)}`}
                >
                  <strong>{segment.citation}</strong>
                  <pre>{segment.text}</pre>
                </section>
              ))}
            </div>
          ) : (
            <p>No extractable text was found. OCR was not run.</p>
          )}
        </>
      )}
    </section>
  );
}
