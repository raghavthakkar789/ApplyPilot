"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthenticationShell } from "@/components/auth/authentication-shell";
import { SetupForm } from "@/components/auth/setup-form";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { useAuth } from "@/features/auth/auth-provider";

export default function SetupPage() {
  const { state } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (state === "authenticated") router.replace("/");
    if (state === "anonymous") router.replace("/login");
  }, [state, router]);
  if (state !== "setup-required") return <LoadingSkeleton />;
  return (
    <AuthenticationShell
      title="Create the local owner"
      description="This one-time setup protects the private ApplyPilot workspace. Account creation is permanently disabled after completion."
    >
      <SetupForm />
    </AuthenticationShell>
  );
}
