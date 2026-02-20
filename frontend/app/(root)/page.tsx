"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
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
import { TransactionCard } from "@/components/transactions/TransactionCard";
import { TransactionDialog } from "@/components/transactions/TransactionDialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { cn } from "@/lib/utils";

interface UserData {
  id: string;
  email: string;
  name: string;
}

interface Transaction {
  id: number;
  amount: number;
  type: "income" | "expense";
  title: string;
  description: string | null;
  transaction_datetime: string;
  account: { id: number; name: string };
  category: { id: number; name: string };
}

interface Account {
  id: number;
  name: string;
  balance: number;
  description: string | null;
}

interface Category {
  id: number;
  name: string;
  type: string;
}

export default function DashboardPage() {
  const { accessToken, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [user, setUser] = useState<UserData | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [fetchLoading, setFetchLoading] = useState(false);

  // Dialog states
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [transactionToDelete, setTransactionToDelete] = useState<Transaction | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Prevent double-fetch in React Strict Mode
  const hasFetchedRef = useRef(false);

  const fetchData = useCallback(async () => {
    try {
      setFetchLoading(true);
      const [userRes, accountsRes, transRes, catsRes] = await Promise.all([
        api.get("/api/users/me", { baseURL: "" }),
        api.get("/api/accounts", { baseURL: "" }),
        api.get("/api/transactions", { baseURL: "" }),
        api.get("/api/categories", { baseURL: "" })
      ]);
      setUser(userRes.data);
      setAccounts(accountsRes.data);
      setTransactions(transRes.data);
      setCategories(catsRes.data);
    } catch (err: any) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setFetchLoading(false);
    }
  }, []);

  useEffect(() => {
    if (authLoading) return;
    if (!accessToken) {
      router.push("/login");
      return;
    }

    if (hasFetchedRef.current) return;
    hasFetchedRef.current = true;

    fetchData();
  }, [authLoading, accessToken, router, fetchData]);

  // Calculations
  const totalBalance = accounts.reduce((acc, account) => acc + Number(account.balance), 0);

  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();

  const currentMonthTransactions = transactions.filter(t => {
    const d = new Date(t.transaction_datetime);
    return d.getMonth() === currentMonth && d.getFullYear() === currentYear;
  });

  const monthlyIncome = currentMonthTransactions
    .filter(t => t.type === "income")
    .reduce((acc, t) => acc + Number(t.amount), 0);

  const monthlyExpenses = currentMonthTransactions
    .filter(t => t.type === "expense")
    .reduce((acc, t) => acc + Number(t.amount), 0);

  // Handler functions
  const handleAddTransaction = () => {
    setSelectedTransaction(null);
    setIsDialogOpen(true);
  };

  const handleEditTransaction = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setIsDialogOpen(true);
  };

  const handleDeleteClick = (transaction: Transaction) => {
    setTransactionToDelete(transaction);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!transactionToDelete) return;

    try {
      setIsSubmitting(true);
      await api.delete(`/api/transactions/${transactionToDelete.id}`, { baseURL: "" });
      setTransactions((prev) => prev.filter((t) => t.id !== transactionToDelete.id));
      setIsDeleteDialogOpen(false);
      setTransactionToDelete(null);
      // Refresh accounts to update balance
      const accountsRes = await api.get("/api/accounts", { baseURL: "" });
      setAccounts(accountsRes.data);
    } catch (err: any) {
      console.error("Failed to delete transaction:", err);
      alert("Failed to delete transaction.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFormSubmit = async (data: any) => {
    try {
      setIsSubmitting(true);
      if (selectedTransaction) {
        const response = await api.put(
          `/api/transactions/${selectedTransaction.id}`,
          data,
          { baseURL: "" }
        );
        setTransactions((prev) =>
          prev.map((t) => (t.id === selectedTransaction.id ? response.data : t))
        );
      } else {
        const response = await api.post("/api/transactions", data, { baseURL: "" });
        setTransactions((prev) => [response.data, ...prev]);
      }
      setIsDialogOpen(false);
      // Refresh accounts to update balances
      const accountsRes = await api.get("/api/accounts", { baseURL: "" });
      setAccounts(accountsRes.data);
    } catch (err: any) {
      console.error("Failed to save transaction:", err);
      alert(err.response?.data?.error?.message || "Failed to save transaction.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (authLoading || (fetchLoading && !user)) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="mt-4 text-sm text-muted-foreground">Loading your dashboard...</p>
      </div>
    );
  }

  const recentTransactions = transactions.slice(0, 5);

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
          <Button onClick={handleAddTransaction} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Transaction
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="Total Balance"
          value={`$${totalBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon={<Wallet className="h-4 w-4 text-muted-foreground" />}
          description="Available across all accounts"
        />
        <StatCard
          title="Income"
          value={`$${monthlyIncome.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon={<TrendingUp className="h-4 w-4 text-emerald-500" />}
          description="Total for this month"
        />
        <StatCard
          title="Expenses"
          value={`$${monthlyExpenses.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon={<TrendingDown className="h-4 w-4 text-destructive" />}
          description="Total for this month"
        />
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent Transactions</CardTitle>
            <CardDescription>
              {recentTransactions.length > 0
                ? `Showing your last ${recentTransactions.length} transactions.`
                : "You have no recent transactions."}
            </CardDescription>
          </div>
          <Button variant="ghost" size="sm" className="gap-1" onClick={() => router.push("/transactions")}>
            View all
            <ArrowRight className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentTransactions.length > 0 ? (
              <div className="flex flex-col gap-2">
                {recentTransactions.map((transaction) => (
                  <TransactionCard
                    key={transaction.id}
                    transaction={transaction}
                    onEdit={handleEditTransaction}
                    onDelete={handleDeleteClick}
                  />
                ))}
              </div>
            ) : (
              <div className="flex h-[200px] items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
                Transaction history will appear here.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Transaction Add/Edit Dialog */}
      <TransactionDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onSubmit={handleFormSubmit}
        transaction={selectedTransaction}
        accounts={accounts}
        categories={categories}
        isLoading={isSubmitting}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the transaction
              <span className="font-semibold text-foreground mx-1">
                "{transactionToDelete?.title}"
              </span>
              of
              <span className={cn(
                "font-bold mx-1",
                transactionToDelete?.type === "income" ? "text-emerald-500" : "text-destructive"
              )}>
                ${transactionToDelete?.amount}
              </span>
              from your records.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isSubmitting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={(e) => {
                e.preventDefault();
                handleConfirmDelete();
              }}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete Transaction"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
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
