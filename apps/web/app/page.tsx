import { DiscoverWorkspace } from "@/features/discover/discover-workspace";
import { ProtectedRouteBoundary } from "@/components/auth/protected-route-boundary";

export default function HomePage() {
  return (
    <ProtectedRouteBoundary>
      <DiscoverWorkspace />
    </ProtectedRouteBoundary>
  );
}
