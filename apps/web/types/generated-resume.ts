// Generated-contract boundary derived from FastAPI's resume schemas.
export type ExtractionStatus = "pending" | "succeeded" | "failed";
export type ReviewStatus = "pending" | "accepted" | "rejected";

export interface ResumeVersion {
  id: string;
  version_number: number;
  filename: string;
  media_type: string;
  format: "pdf" | "docx" | "text";
  byte_length: number;
  sha256: string;
  parser: string;
  parser_version: string;
  extraction_status: ExtractionStatus;
  integrity_state: string;
  created_at: string;
  superseded_at: string | null;
  current: boolean;
}

export interface ResumeRecord {
  id: string;
  display_name: string;
  purpose: string | null;
  created_at: string;
  trashed_at: string | null;
  purge_after: string | null;
  current_version: ResumeVersion | null;
}

export interface ResumeDetail extends ResumeRecord {
  versions: ResumeVersion[];
}

export interface Extraction {
  status: ExtractionStatus;
  text: string | null;
  page_count: number | null;
  paragraph_count: number | null;
  segments: { citation: string; text: string }[];
  warnings: string[];
  extracted_at: string | null;
  failure_category: string | null;
}

export interface FactCandidate {
  id: string;
  resume_version_id: string;
  fact_type: string;
  semantic_key: string;
  proposed_value: unknown;
  evidence_citation: string;
  extraction_method: string;
  confidence: string | null;
  review_status: ReviewStatus;
  created_at: string;
  reviewed_at: string | null;
  resulting_fact_identity_id: string | null;
  resulting_fact_version_id: string | null;
}
