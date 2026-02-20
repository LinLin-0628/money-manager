"use client";

import React, { useEffect, useState, useRef } from "react";
import { Plus, Loader2, Wallet, AlertCircle, Search, Calendar } from "lucide-react";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { BudgetCard } from "@/components/budgets/BudgetCard";
import { BudgetDialog } from "@/components/budgets/BudgetDialog";
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

interface Category {
  id: number;
  name: string;
  type: string;
}

interface Budget {
  id: number;
  month: string;
  amount: number;
  actual_spent: number;
  remaining: number;
  percent_used: number;
  is_overspent: boolean;
  category: {
    id: number;
    name: string;
    type: string;
  };
}

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Dialog state
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedBudget, setSelectedBudget] = useState<Budget | null>(null);
  const [budgetToDelete, setBudgetToDelete] = useState<Budget | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Prevent double-fetch in React Strict Mode
  const hasFetchedRef = useRef(false);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [budgetsRes, categoriesRes] = await Promise.all([
        api.get("/api/budgets", { baseURL: "" }),
        api.get("/api/categories", { baseURL: "" })
      ]);

      setBudgets(budgetsRes.data);
      setCategories(categoriesRes.data);
    } catch (err: unknown) {
      console.error("Failed to fetch budgets data:", err);
      setError("Failed to load budgets. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (hasFetchedRef.current) return;
    hasFetchedRef.current = true;
    fetchData();
  }, []);

  const handleAddBudget = () => {
    setSelectedBudget(null);
    setIsDialogOpen(true);
  };

  const handleEditBudget = (budget: Budget) => {
    setSelectedBudget(budget);
    setIsDialogOpen(true);
  };

  const handleDeleteClick = (budget: Budget) => {
    setBudgetToDelete(budget);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!budgetToDelete) return;

    try {
      setIsSubmitting(true);
      await api.delete(`/api/budgets/${budgetToDelete.id}`, { baseURL: "" });
      setBudgets((prev) => prev.filter((b) => b.id !== budgetToDelete.id));
      setIsDeleteDialogOpen(false);
      setBudgetToDelete(null);
    } catch (err: unknown) {
      console.error("Failed to delete budget:", err);
      alert("Failed to delete budget.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFormSubmit = async (data: Partial<{
    month: string;
    amount: number;
    category_id: number;
  }>) => {
    try {
      setIsSubmitting(true);
      if (selectedBudget) {
        // Update
        const response = await api.put(
          `/api/budgets/${selectedBudget.id}`,
          data,
          { baseURL: "" }
        );
        // Backend returns the updated budget with actuals
        setBudgets((prev) =>
          prev.map((b) => (b.id === selectedBudget.id ? response.data : b))
        );
      } else {
        // Create
        const response = await api.post("/api/budgets", data, { baseURL: "" });
        // The create endpoint returns the budget without actuals populated sometimes,
        // but our service layer seems to handle it on the actual backend.
        // Let's just refresh to be safe or append if backend returns full object.
        setBudgets((prev) => [...prev, response.data]);

        // Refresh to get actual spent calculations if not returned
        fetchData();
      }
      setIsDialogOpen(false);
    } catch (err: unknown) {
      const error = err as any;
      console.error("Failed to save budget:", error);
      const errorMessage = error.response?.data?.error?.message || error.response?.data?.detail?.[0]?.msg || "Failed to save budget.";
      alert(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredBudgets = budgets.filter((b) =>
    b.category.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="animate-in fade-in duration-500 space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Budgets</h1>
          <p className="text-muted-foreground">
            Set monthly spending limits for your expense categories.
          </p>
        </div>
        <Button onClick={handleAddBudget} className="gap-2 self-start md:self-center">
          <Plus className="h-4 w-4" />
          Add Budget
        </Button>
      </div>

      <div className="flex items-center gap-2 max-w-sm">
        <div className="relative w-full">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search category budgets..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="mt-4 text-sm text-muted-foreground">Loading budgets...</p>
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
      ) : filteredBudgets.length > 0 ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredBudgets.map((budget) => (
            <BudgetCard
              key={budget.id}
              budget={budget}
              onEdit={handleEditBudget}
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
            <h3 className="mt-4 text-lg font-semibold">No budgets found</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {searchQuery ? "No budgets match your search." : "You haven't set any budgets yet."}
            </p>
            {!searchQuery && (
              <Button onClick={handleAddBudget} variant="outline" className="mt-4">
                Set Your First Budget
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      <BudgetDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onSubmit={handleFormSubmit}
        budget={selectedBudget}
        categories={categories}
        isLoading={isSubmitting}
      />

      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the budget for{" "}
              <span className="font-semibold text-foreground">
                {budgetToDelete?.category.name}
              </span>{" "}
              in {budgetToDelete && new Date(budgetToDelete.month).toLocaleDateString("en-US", { month: "long", year: "numeric" })}.
              This action cannot be undone.
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
              {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : "Delete Budget"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
