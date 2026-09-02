import { ProtectedRouteBoundary } from "@/components/auth/protected-route-boundary";
import { CandidateWorkspace } from "@/features/candidate/candidate-workspace";

export default function EvidencePage() {
  return (
    <ProtectedRouteBoundary>
      <CandidateWorkspace view="evidence" />
    </ProtectedRouteBoundary>
  );
}
