import { AlertCircle } from "lucide-react";
export function ErrorState() {
  return (
    <div className="feedback-state" role="alert">
      <AlertCircle aria-hidden="true" />
      <h2>Opportunities unavailable</h2>
      <p>
        The local workspace could not load. Existing data has not been changed.
      </p>
    </div>
  );
}
