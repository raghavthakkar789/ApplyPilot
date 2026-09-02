import { ProtectedRouteBoundary } from "@/components/auth/protected-route-boundary";
import { CandidateWorkspace } from "@/features/candidate/candidate-workspace";

export default function ProfilePage() {
  return (
    <ProtectedRouteBoundary>
      <CandidateWorkspace view="profile" />
    </ProtectedRouteBoundary>
  );
}
