import { TriangleAlert } from "lucide-react";

export function ExtractionWarning({ message }: { message: string }) {
  return (
    <p className="extraction-warning" role="status">
      <TriangleAlert aria-hidden="true" size={17} /> {message}
    </p>
  );
}
