// Generated-contract output from the FastAPI OpenAPI schema. Do not edit by hand.
export interface SessionView {
  id: string;
  created_at: string;
  last_activity_at: string;
  idle_expires_at: string;
  absolute_expires_at: string;
  client_label: string | null;
  current: boolean;
}

export interface ApiProblem {
  detail?: string;
}
