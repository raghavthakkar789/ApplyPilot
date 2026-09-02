import { ProtectedRouteBoundary } from "@/components/auth/protected-route-boundary";
import { ResumeWorkspace } from "@/features/resumes/resume-workspace";

export default function ResumesPage() {
  return (
    <ProtectedRouteBoundary>
      <ResumeWorkspace />
    </ProtectedRouteBoundary>
  );
}
