"use client";

import React, { useEffect } from "react";
import { useForm } from "react-hook-form";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2 } from "lucide-react";

interface Category {
  id: number;
  name: string;
  type: string;
}

interface Budget {
  id: number;
  month: string;
  amount: number;
  category: { id: number; name: string };
}

interface BudgetFormData {
  month: string;
  amount: number;
  category_id: string;
}

interface BudgetDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { amount: number }) => Promise<void>;
  budget?: Budget | null;
  categories: Category[];
  isLoading?: boolean;
}

export function BudgetDialog({
  isOpen,
  onClose,
  onSubmit,
  budget,
  categories,
  isLoading = false,
}: BudgetDialogProps) {
  const isEdit = !!budget;
  const expenseCategories = categories.filter(c => c.type === "expense");

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<BudgetFormData>({
    defaultValues: {
      month: new Date().toISOString().slice(0, 7), // YYYY-MM
      amount: 0,
      category_id: "",
    },
  });

  const selectedCategoryId = watch("category_id");

  useEffect(() => {
    if (budget) {
      reset({
        month: budget.month.slice(0, 7),
        amount: Number(budget.amount),
        category_id: budget.category.id.toString(),
      });
    } else {
      reset({
        month: new Date().toISOString().slice(0, 7),
        amount: 0,
        category_id: "",
      });
    }
  }, [budget, reset, isOpen]);

  const handleFormSubmit = async (data: BudgetFormData) => {
    if (isEdit) {
        await onSubmit({ amount: Number(data.amount) });
    } else {
        const submissionData = {
          month: `${data.month}-01`,
          amount: Number(data.amount),
          category_id: parseInt(data.category_id),
        };
        await onSubmit(submissionData);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit Budget" : "Add Budget"}</DialogTitle>
          <DialogDescription>
            {isEdit
              ? "Update your budget amount."
              : "Set a monthly spending limit for a category."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="month">Month</Label>
            <Input
              id="month"
              type="month"
              disabled={isEdit}
              {...register("month", {
                required: "Month is required",
              })}
            />
            {errors.month && (
              <p className="text-xs font-medium text-destructive">
                {errors.month.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="category_id">Category</Label>
            <Select
              disabled={isEdit}
              value={selectedCategoryId}
              onValueChange={(value) => setValue("category_id", value)}
            >
              <SelectTrigger id="category_id">
                <SelectValue placeholder="Select a category" />
              </SelectTrigger>
              <SelectContent>
                {expenseCategories.map((category) => (
                  <SelectItem key={category.id} value={category.id.toString()} className="capitalize">
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.category_id && (
              <p className="text-xs font-medium text-destructive">
                {errors.category_id.message}
              </p>
            )}
            {expenseCategories.length === 0 && (
                <p className="text-xs text-amber-500">No expense categories found. Create one first.</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="amount">Budget Amount</Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              placeholder="0.00"
              {...register("amount", {
                required: "Budget amount is required",
                min: { value: 0.01, message: "Amount must be greater than 0" },
              })}
            />
            {errors.amount && (
              <p className="text-xs font-medium text-destructive">
                {errors.amount.message}
              </p>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading || (!isEdit && expenseCategories.length === 0)}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isEdit ? "Save Changes" : "Create Budget"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
