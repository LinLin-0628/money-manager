"use client";

import React, { useEffect, useState } from "react";
import { Loader2, User, Mail, ShieldCheck, LogOut, AlertCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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

  useEffect(() => {
    // 1. 🔥 THE GATEKEEPER: If AuthContext is still initializing, DO NOTHING.
    // This stops the "Request 1" that causes the 401 error on hard refresh.
    if (authLoading) return;

    // 2. If we finished loading and there's no token, go to login.
    if (!accessToken) {
      router.push("/login");
      return;
    }

    // 3. Only fetch if we have a token and don't have a user yet.
    const fetchUserData = async () => {
      try {
        setFetchLoading(true);
        setError(null);
        const response = await api.get("/api/users/me");
        setUser(response.data);
      } catch (err: any) {
        // This will now only trigger if the token is truly invalid/expired
        setError(err.response?.data?.error?.message || "Failed to load profile.");
      } finally {
        setFetchLoading(false);
      }
    };

    fetchUserData();
  }, [authLoading, accessToken, router]); // Dependency on authLoading is key

  /**
   * RENDERING LOGIC
   * We show the loader if:
   * - Auth is still initializing (authLoading)
   * - OR we are currently fetching data (fetchLoading)
   */
  if (authLoading || (fetchLoading && !user)) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="text-sm font-medium text-muted-foreground">Synchronizing session...</p>
        </div>
      </div>
    );
  }

  // Only show error if we are NOT loading and HAVE NO user.
  if (error && !user) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-md border-destructive shadow-lg">
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <CardTitle>Session Error</CardTitle>
            </div>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => window.location.reload()} className="w-full">
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-background p-8 animate-in fade-in duration-500">
      <div className="mx-auto max-w-2xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <Button variant="outline" onClick={logout} className="gap-2 border-destructive text-destructive hover:bg-destructive hover:text-destructive-foreground transition-colors">
            <LogOut className="h-4 w-4" /> Logout
          </Button>
        </div>

        <Card className="shadow-md overflow-hidden">
          <CardHeader className="border-b bg-muted/30">
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-primary" />
              <CardTitle>User Profile</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <DetailRow icon={<ShieldCheck />} label="User ID" value={user.id} mono />
              <DetailRow icon={<User />} label="Full Name" value={user.name} />
              <DetailRow icon={<Mail />} label="Email Address" value={user.email} />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function DetailRow({ icon, label, value, mono = false }: any) {
  return (
    <div className="flex items-center justify-between py-2 border-b last:border-0">
      <div className="flex items-center gap-3 text-muted-foreground">
        {React.cloneElement(icon, { className: "h-5 w-5" })}
        <span className="font-medium text-foreground">{label}</span>
      </div>
      <span className={mono ? "text-xs font-mono bg-muted px-2 py-1 rounded border" : "font-medium"}>
        {value}
      </span>
    </div>
  );
}
