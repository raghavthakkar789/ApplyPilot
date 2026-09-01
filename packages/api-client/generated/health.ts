// Generated-contract baseline from the FastAPI OpenAPI schema.
// This package becomes mechanically regenerated once API schema export is wired.
export interface HealthResponse {
  status: "ok" | "ready";
}

export interface ErrorDetail {
  code: string;
  message: string;
  request_id: string | null;
}

export interface ErrorResponse {
  error: ErrorDetail;
}
