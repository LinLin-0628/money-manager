"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Loader2 } from "lucide-react";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { accessToken, isLoading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If auth check is finished and no token exists, send to login
    if (!authLoading && !accessToken) {
      router.push("/login");
    }
  }, [accessToken, authLoading, router]);

  /**
   * Keep the user on the loading screen if:
   * 1. Auth is still initializing (Silent Refresh is in progress)
   * 2. No token is present (Prevents page content flash during redirect)
   */
  if (authLoading || !accessToken) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-background">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="mt-4 text-sm font-medium text-muted-foreground animate-pulse">
          Verifying session...
        </p>
      </div>
    );
  }

  // Once authenticated, render the dashboard page
  return <>{children}</>;
}
