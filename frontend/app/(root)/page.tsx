"use client";

import React, { useEffect, useState, useRef } from "react";
import {
  Loader2,
  TrendingUp,
  TrendingDown,
  Wallet,
  ArrowRight,
  Plus,
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
  const { accessToken, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [user, setUser] = useState<UserData | null>(null);
  const [fetchLoading, setFetchLoading] = useState(false);

  // Prevent double-fetch in React Strict Mode
  const hasFetchedRef = useRef(false);

  useEffect(() => {
    if (authLoading) return;
    if (!accessToken) {
      router.push("/login");
      return;
    }

    if (hasFetchedRef.current) return;

    const fetchUserData = async () => {
      hasFetchedRef.current = true;
      try {
        setFetchLoading(true);
        const response = await api.get("/api/users/me");
        setUser(response.data);
      } catch (err: any) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setFetchLoading(false);
      }
    };

    fetchUserData();
  }, [authLoading, accessToken, router]);

  if (authLoading || (fetchLoading && !user)) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="animate-in fade-in duration-500 space-y-8">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {user?.name || "User"}
          </h1>
          <p className="text-muted-foreground">
            Here's what's happening with your money today.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Add Transaction
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="Total Balance"
          value="$0.00"
          icon={<Wallet className="h-4 w-4 text-muted-foreground" />}
          description="Available across all accounts"
        />
        <StatCard
          title="Income"
          value="$0.00"
          icon={<TrendingUp className="h-4 w-4 text-emerald-500" />}
          description="+0% from last month"
        />
        <StatCard
          title="Expenses"
          value="$0.00"
          icon={<TrendingDown className="h-4 w-4 text-destructive" />}
          description="+0% from last month"
        />
      </div>

      {/* Recent Activity Placeholder */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent Transactions</CardTitle>
            <CardDescription>You have no recent transactions.</CardDescription>
          </div>
          <Button variant="ghost" size="sm" className="gap-1" onClick={() => router.push("/transactions")}>
            View all
            <ArrowRight className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="flex h-[200px] items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
            Transaction history will appear here.
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon,
  description,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
  description: string;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
