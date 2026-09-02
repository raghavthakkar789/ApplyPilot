import { ProtectedRouteBoundary } from "@/components/auth/protected-route-boundary";
import { SourceSettings } from "@/features/sources/source-settings";

export default function SourcesPage() {
  return (
    <ProtectedRouteBoundary>
      <SourceSettings />
    </ProtectedRouteBoundary>
  );
}
