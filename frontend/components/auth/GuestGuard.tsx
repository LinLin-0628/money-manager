// components/auth/GuestGuard.tsx
"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Loader2 } from "lucide-react";

export default function GuestGuard({ children }: { children: React.ReactNode }) {
  const { accessToken, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If we finished checking the session and a token exists,
    // the user shouldn't be here. Send them to the dashboard.
    if (!isLoading && accessToken) {
      router.push("/dashboard");
    }
  }, [accessToken, isLoading, router]);

  // While checking the session, show a loader to prevent "flickering"
  // where the login form shows for a split second before redirecting.
  if (isLoading || accessToken) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return <>{children}</>;
}
