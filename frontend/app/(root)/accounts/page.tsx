"use client";

import React, { useEffect, useState, useRef } from "react";
import { Plus, Loader2, Wallet, AlertCircle, Search } from "lucide-react";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { AccountCard } from "@/components/accounts/AccountCard";
import { AccountDialog } from "@/components/accounts/AccountDialog";
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

interface Account {
  id: number;
  name: string;
  balance: number;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Dialog state
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [accountToDelete, setAccountToDelete] = useState<Account | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Prevent double-fetch in React Strict Mode
  const hasFetchedRef = useRef(false);

  const fetchAccounts = async () => {
    try {
      setIsLoading(true);
      setError(null);
      // Use relative path to hit the Next.js API proxy instead of backend directly
      // axios allows absolute URLs to override baseURL, but relative ones append to it.
      // Since 'api' instance has baseURL set to backend, we use standard axios or
      // pass a full URL to 'api' to hit our proxy.
      const response = await api.get("/api/accounts", { baseURL: "" });
      setAccounts(response.data);
    } catch (err: any) {
      console.error("Failed to fetch accounts:", err);
      setError("Failed to load accounts. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (hasFetchedRef.current) return;
    hasFetchedRef.current = true;
    fetchAccounts();
  }, []);

  const handleAddAccount = () => {
    setSelectedAccount(null);
    setIsDialogOpen(true);
  };

  const handleEditAccount = (account: Account) => {
    setSelectedAccount(account);
    setIsDialogOpen(true);
  };

  const handleDeleteClick = (account: Account) => {
    setAccountToDelete(account);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!accountToDelete) return;

    try {
      setIsSubmitting(true);
      await api.delete(`/api/accounts/${accountToDelete.id}`, { baseURL: "" });
      setAccounts((prev) => prev.filter((acc) => acc.id !== accountToDelete.id));
      setIsDeleteDialogOpen(false);
      setAccountToDelete(null);
    } catch (err: any) {
      console.error("Failed to delete account:", err);
      alert("Failed to delete account.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFormSubmit = async (data: any) => {
    try {
      setIsSubmitting(true);
      if (selectedAccount) {
        // Update - backend AccountUpdate only accepts name and description
        const { balance, ...updateData } = data;
        const response = await api.put(
          `/api/accounts/${selectedAccount.id}`,
          updateData,
          { baseURL: "" }
        );
        setAccounts((prev) =>
          prev.map((acc) => (acc.id === selectedAccount.id ? response.data : acc))
        );
      } else {
        // Create
        const response = await api.post("/api/accounts", data, { baseURL: "" });
        setAccounts((prev) => [...prev, response.data]);
      }
      setIsDialogOpen(false);
    } catch (err: any) {
      console.error("Failed to save account:", err);
      alert(err.response?.data?.error?.message || "Failed to save account.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredAccounts = accounts.filter((acc) =>
    acc.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="animate-in fade-in duration-500 space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Accounts</h1>
          <p className="text-muted-foreground">
            Manage your bank accounts, wallets, and other financial sources.
          </p>
        </div>
        <Button onClick={handleAddAccount} className="gap-2 self-start md:self-center">
          <Plus className="h-4 w-4" />
          Add Account
        </Button>
      </div>

      <div className="flex items-center gap-2 max-w-sm">
        <div className="relative w-full">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search accounts..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="mt-4 text-sm text-muted-foreground">Loading accounts...</p>
        </div>
      ) : error ? (
        <Card className="border-destructive">
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <CardTitle>Error</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
            <Button variant="outline" className="mt-4" onClick={fetchAccounts}>
              Try Again
            </Button>
          </CardContent>
        </Card>
      ) : filteredAccounts.length > 0 ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredAccounts.map((account) => (
            <AccountCard
              key={account.id}
              account={account}
              onEdit={handleEditAccount}
              onDelete={handleDeleteClick}
            />
          ))}
        </div>
      ) : (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
              <Wallet className="h-6 w-6 text-muted-foreground" />
            </div>
            <h3 className="mt-4 text-lg font-semibold">No accounts found</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {searchQuery
                ? `No accounts matching "${searchQuery}"`
                : "You haven't added any accounts yet. Get started by creating one."}
            </p>
            {!searchQuery && (
              <Button variant="outline" className="mt-4" onClick={handleAddAccount}>
                Add your first account
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      <AccountDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onSubmit={handleFormSubmit}
        account={selectedAccount}
        isLoading={isSubmitting}
      />

      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the account
              <span className="font-semibold text-foreground mx-1">
                "{accountToDelete?.name}"
              </span>
              and all associated data.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isSubmitting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={(e) => {
                e.preventDefault();
                handleConfirmDelete();
              }}
              disabled={isSubmitting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isSubmitting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : null}
              Delete Account
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
