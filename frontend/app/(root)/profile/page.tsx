"use client";

import React, { useEffect, useState, useRef } from "react";
import {
  Loader2,
  User,
  Mail,
  ShieldCheck,
  LogOut,
  AlertCircle,
  Settings,
  Bell,
  Lock,
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

export default function ProfilePage() {
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
        console.error("Profile fetch error:", err);
      } finally {
        setFetchLoading(false);
      }
    };

    fetchUserData();
  }, [authLoading, accessToken, router]);

  // Show loader during auth initialization
  if (authLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="mt-4 text-sm font-medium text-muted-foreground">
          Verifying session...
        </p>
      </div>
    );
  }

  // Show loader while fetching user data
  if (fetchLoading && !user) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="mt-4 text-sm font-medium text-muted-foreground">
          Loading profile details...
        </p>
      </div>
    );
  }

  // Show error state if fetch failed
  if (error && !user) {
    return (
      <div className="flex items-center justify-center p-4">
        <Card className="w-full max-w-md border-destructive shadow-lg">
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <CardTitle>Error Loading Profile</CardTitle>
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

  if (!user) return null;

  return (
    <div className="animate-in fade-in duration-500 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Account Profile</h1>
        <p className="text-muted-foreground">Manage your account settings and preferences.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* User Information */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-primary" />
              <CardTitle>Personal Information</CardTitle>
            </div>
            <CardDescription>Your basic account details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
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
          </CardContent>
        </Card>

        {/* Account Settings / Placeholders */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-primary" />
              <CardTitle>Quick Settings</CardTitle>
            </div>
            <CardDescription>Manage your app experience</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" className="w-full justify-start gap-2" disabled>
              <Lock className="h-4 w-4" />
              Change Password
            </Button>
            <Button variant="outline" className="w-full justify-start gap-2" disabled>
              <Bell className="h-4 w-4" />
              Notifications
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-2 text-destructive hover:bg-destructive/10"
              onClick={logout}
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </Button>
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
    <div className="flex items-center justify-between py-3 border-b last:border-0">
      <div className="flex items-center gap-3 text-muted-foreground">
        {React.cloneElement(icon, { className: "h-4 w-4" } as any)}
        <span className="text-sm font-medium text-foreground">{label}</span>
      </div>
      <span
        className={
          mono
            ? "text-xs font-mono bg-muted px-2 py-1 rounded border"
            : "text-sm font-medium"
        }
      >
        {value}
      </span>
    </div>
  );
}
