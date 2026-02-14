"use client";

import React, { useEffect, useState, useRef } from "react";
import {
  Loader2,
  User,
  Mail,
  ShieldCheck,
  LogOut,
  AlertCircle,
} from "lucide-react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

interface UserData {
  id: string;
  email: string;
  name: string;
}

export default function DashboardPage() {
  const { logout, accessToken, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [user, setUser] = useState<UserData | null>(null);
  const [fetchLoading, setFetchLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Prevent double-fetch in React Strict Mode
  const hasFetchedRef = useRef(false);

  useEffect(() => {
    // Wait for auth initialization to complete
    if (authLoading) return;

    // Redirect to login if no token
    if (!accessToken) {
      router.push("/login");
      return;
    }

    // Prevent duplicate API calls
    if (hasFetchedRef.current) return;

    const fetchUserData = async () => {
      hasFetchedRef.current = true;

      try {
        setFetchLoading(true);
        setError(null);
        const response = await api.get("/api/users/me");
        setUser(response.data);
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.error?.message || "Failed to load profile.";
        setError(errorMessage);
        console.error("Dashboard fetch error:", err);
      } finally {
        setFetchLoading(false);
      }
    };

    fetchUserData();
  }, [authLoading, accessToken, router]);

  // Show loader during auth initialization
  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="text-sm font-medium text-muted-foreground">
            Initializing session...
          </p>
        </div>
      </div>
    );
  }

  // Show loader while fetching user data
  if (fetchLoading && !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="text-sm font-medium text-muted-foreground">
            Loading your profile...
          </p>
        </div>
      </div>
    );
  }

  // Show error state if fetch failed
  if (error && !user) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4 bg-background">
        <Card className="w-full max-w-md border-destructive shadow-lg">
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <CardTitle>Unable to Load Profile</CardTitle>
            </div>
            <CardDescription className="text-destructive/80">
              {error}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex gap-2">
            <Button
              onClick={() => {
                hasFetchedRef.current = false;
                window.location.reload();
              }}
              className="flex-1"
            >
              Retry
            </Button>
            <Button onClick={logout} variant="outline" className="flex-1">
              Logout
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Fallback loader (shouldn't reach here normally)
  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  // Main dashboard content
  return (
    <div className="min-h-screen bg-background p-8 animate-in fade-in duration-500">
      <div className="mx-auto max-w-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <Button
            variant="outline"
            onClick={logout}
            className="gap-2 border-destructive text-destructive hover:bg-destructive hover:text-destructive-foreground transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </div>

        {/* User Profile Card */}
        <Card className="shadow-md overflow-hidden">
          <CardHeader className="border-b bg-muted/30">
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-primary" />
              <CardTitle>User Profile</CardTitle>
            </div>
            <CardDescription>Your account information</CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <DetailRow
                icon={<ShieldCheck />}
                label="User ID"
                value={user.id}
                mono
              />
              <DetailRow icon={<User />} label="Full Name" value={user.name} />
              <DetailRow
                icon={<Mail />}
                label="Email Address"
                value={user.email}
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function DetailRow({
  icon,
  label,
  value,
  mono = false,
}: {
  icon: React.ReactElement<{ className?: string }>;
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b last:border-0">
      <div className="flex items-center gap-3 text-muted-foreground">
        {React.cloneElement(icon, { className: "h-5 w-5" } as any)}
        <span className="font-medium text-foreground">{label}</span>
      </div>
      <span
        className={
          mono
            ? "text-xs font-mono bg-muted px-2 py-1 rounded border"
            : "font-medium"
        }
      >
        {value}
      </span>
    </div>
  );
}
