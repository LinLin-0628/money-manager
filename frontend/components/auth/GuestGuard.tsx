"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Loader2 } from "lucide-react";

interface GuestGuardProps {
  children: React.ReactNode;
}

/**
 * GuestGuard prevents authenticated users from accessing auth pages (login/signup).
 * If a user is already logged in, they get redirected to the dashboard.
 */
export default function GuestGuard({ children }: GuestGuardProps) {
  const { accessToken, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If auth check is finished and user HAS a token, redirect to dashboard
    if (!isLoading && accessToken) {
      router.push("/");
    }
  }, [accessToken, isLoading, router]);

  // Show loader while checking auth status
  if (isLoading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-background">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="mt-4 text-sm font-medium text-muted-foreground">
          Loading...
        </p>
      </div>
    );
  }

  // If user is authenticated, show loader during redirect
  if (accessToken) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-background">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="mt-4 text-sm font-medium text-muted-foreground">
          Redirecting to dashboard...
        </p>
      </div>
    );
  }

  // User is not authenticated - show the auth page (login/signup)
  return <>{children}</>;
}
