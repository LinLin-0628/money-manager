"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import { Plus, Loader2, ArrowRightLeft, AlertCircle, Search, Filter } from "lucide-react";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

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
}

interface Category {
  id: number;
  name: string;
  type: string;
}

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");

  // Dialog state
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [transactionToDelete, setTransactionToDelete] = useState<Transaction | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Prevent double-fetch in React Strict Mode
  const hasFetchedRef = useRef(false);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [transRes, accRes, catRes] = await Promise.all([
        api.get("/api/transactions", { baseURL: "" }),
        api.get("/api/accounts", { baseURL: "" }),
        api.get("/api/categories", { baseURL: "" })
      ]);

      setTransactions(transRes.data);
      setAccounts(accRes.data);
      setCategories(catRes.data);
    } catch (err: any) {
      console.error("Failed to fetch data:", err);
      setError("Failed to load data. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (hasFetchedRef.current) return;
    hasFetchedRef.current = true;
    fetchData();
  }, [fetchData]);

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
    } catch (err: any) {
      console.error("Failed to save transaction:", err);
      alert(err.response?.data?.error?.message || "Failed to save transaction.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredTransactions = transactions.filter((t) => {
    const matchesSearch = t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (t.description?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);
    const matchesType = typeFilter === "all" || t.type === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div className="animate-in fade-in duration-500 space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Transactions</h1>
          <p className="text-muted-foreground">
            Monitor and manage your financial activities.
          </p>
        </div>
        <Button onClick={handleAddTransaction} className="gap-2 self-start md:self-center">
          <Plus className="h-4 w-4" />
          Add Transaction
        </Button>
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        <div className="relative w-full max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search transactions..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="All Types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="income">Income</SelectItem>
              <SelectItem value="expense">Expense</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="mt-4 text-sm text-muted-foreground">Loading transactions...</p>
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
            <Button variant="outline" className="mt-4" onClick={fetchData}>
              Try Again
            </Button>
          </CardContent>
        </Card>
      ) : filteredTransactions.length > 0 ? (
        <div className="flex flex-col gap-2">
          {filteredTransactions.map((transaction) => (
            <TransactionCard
              key={transaction.id}
              transaction={transaction}
              onEdit={handleEditTransaction}
              onDelete={handleDeleteClick}
            />
          ))}
        </div>
      ) : (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
              <ArrowRightLeft className="h-6 w-6 text-muted-foreground" />
            </div>
            <h3 className="mt-4 text-lg font-semibold">No transactions found</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {searchQuery || typeFilter !== "all"
                ? "Try adjusting your filters to find what you're looking for."
                : "Get started by adding your first income or expense."}
            </p>
            {!searchQuery && typeFilter === "all" && (
              <Button onClick={handleAddTransaction} variant="outline" className="mt-6">
                Add Transaction
              </Button>
            )}
          </CardContent>
        </Card>
      )}

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
