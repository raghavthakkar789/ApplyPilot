"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthenticationShell } from "@/components/auth/authentication-shell";
import { LoginForm } from "@/components/auth/login-form";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { useAuth } from "@/features/auth/auth-provider";

export default function LoginPage() {
  const { state } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (state === "authenticated") router.replace("/");
    if (state === "setup-required") router.replace("/setup");
  }, [state, router]);
  if (state !== "anonymous") return <LoadingSkeleton />;
  return (
    <AuthenticationShell
      title="Welcome back"
      description="Sign in to continue to the private job discovery workspace."
    >
      <LoginForm />
    </AuthenticationShell>
  );
}
