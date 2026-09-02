"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { useAuth } from "@/features/auth/auth-provider";

export function ProtectedRouteBoundary({
  children,
}: {
  children: React.ReactNode;
}) {
  const { state } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (state === "setup-required") router.replace("/setup");
    if (state === "anonymous") router.replace("/login");
  }, [state, router]);
  if (state !== "authenticated") return <LoadingSkeleton />;
  return children;
}
