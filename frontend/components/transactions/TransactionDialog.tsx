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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  RadioGroup,
  RadioGroupItem
} from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";

interface Account {
  id: number;
  name: string;
}

interface Category {
  id: number;
  name: string;
  type: string;
}

interface Transaction {
  id: number;
  amount: number;
  type: string;
  title: string;
  description: string | null;
  transaction_datetime: string;
  account: { id: number; name: string };
  category: { id: number; name: string };
}

interface TransactionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  transaction?: Transaction | null;
  accounts: Account[];
  categories: Category[];
  isLoading?: boolean;
}

export function TransactionDialog({
  isOpen,
  onClose,
  onSubmit,
  transaction,
  accounts,
  categories,
  isLoading = false,
}: TransactionDialogProps) {
  const isEdit = !!transaction;

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm({
    defaultValues: {
      title: "",
      amount: 0,
      type: "expense",
      description: "",
      transaction_datetime: new Date().toISOString().slice(0, 16),
      account_id: "",
      category_id: "",
    },
  });

  const selectedType = watch("type");

  // Reset form when transaction changes or dialog opens/closes
  useEffect(() => {
    if (transaction) {
      reset({
        title: transaction.title,
        amount: transaction.amount,
        type: transaction.type,
        description: transaction.description || "",
        transaction_datetime: new Date(transaction.transaction_datetime).toISOString().slice(0, 16),
        account_id: transaction.account.id.toString(),
        category_id: transaction.category.id.toString(),
      });
    } else {
      reset({
        title: "",
        amount: 0,
        type: "expense",
        description: "",
        transaction_datetime: new Date().toISOString().slice(0, 16),
        account_id: accounts.length > 0 ? accounts[0].id.toString() : "",
        category_id: "",
      });
    }
  }, [transaction, reset, isOpen, accounts]);

  const handleFormSubmit = async (data: any) => {
    // Convert string IDs to numbers as expected by the backend
    const submissionData = {
      ...data,
      amount: parseFloat(data.amount),
      account_id: parseInt(data.account_id),
      category_id: parseInt(data.category_id),
    };
    await onSubmit(submissionData);
  };

  const filteredCategories = categories.filter(cat => cat.type === selectedType);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit Transaction" : "Add Transaction"}</DialogTitle>
          <DialogDescription>
            {isEdit
              ? "Update your transaction details below."
              : "Record a new income or expense."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4 py-4 max-h-[70vh] overflow-y-auto px-1">
          {/* Transaction Type */}
          <div className="space-y-2">
            <Label>Transaction Type</Label>
            <RadioGroup
              defaultValue={selectedType}
              onValueChange={(value) => {
                setValue("type", value);
                setValue("category_id", ""); // Reset category when type changes
              }}
              className="flex gap-4"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="expense" id="expense" />
                <Label htmlFor="expense" className="font-normal">Expense</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="income" id="income" />
                <Label htmlFor="income" className="font-normal">Income</Label>
              </div>
            </RadioGroup>
          </div>

          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              placeholder="e.g. Grocery Shopping"
              {...register("title", {
                required: "Title is required",
                maxLength: { value: 255, message: "Max 255 characters" },
              })}
            />
            {errors.title && (
              <p className="text-xs font-medium text-destructive">
                {errors.title.message}
              </p>
            )}
          </div>

          {/* Amount */}
          <div className="space-y-2">
            <Label htmlFor="amount">Amount</Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              placeholder="0.00"
              {...register("amount", {
                required: "Amount is required",
                min: { value: 0.01, message: "Amount must be greater than 0" },
              })}
            />
            {errors.amount && (
              <p className="text-xs font-medium text-destructive">
                {errors.amount.message}
              </p>
            )}
          </div>

          {/* Account */}
          <div className="space-y-2">
            <Label htmlFor="account">Account</Label>
            <Select
              value={watch("account_id")}
              onValueChange={(value) => setValue("account_id", value)}
            >
              <SelectTrigger id="account">
                <SelectValue placeholder="Select account" />
              </SelectTrigger>
              <SelectContent>
                {accounts.map((acc) => (
                  <SelectItem key={acc.id} value={acc.id.toString()}>
                    <span className="capitalize">{acc.name}</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.account_id && (
              <p className="text-xs font-medium text-destructive">
                Account is required
              </p>
            )}
          </div>

          {/* Category */}
          <div className="space-y-2">
            <Label htmlFor="category">Category</Label>
            <Select
              value={watch("category_id")}
              onValueChange={(value) => setValue("category_id", value)}
            >
              <SelectTrigger id="category">
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                {filteredCategories.length > 0 ? (
                  filteredCategories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id.toString()}>
                      <span className="capitalize">{cat.name}</span>
                    </SelectItem>
                  ))
                ) : (
                  <div className="p-2 text-xs text-muted-foreground text-center">
                    No {selectedType} categories found.
                  </div>
                )}
              </SelectContent>
            </Select>
            {errors.category_id && (
              <p className="text-xs font-medium text-destructive">
                Category is required
              </p>
            )}
          </div>

          {/* Date & Time */}
          <div className="space-y-2">
            <Label htmlFor="transaction_datetime">Date & Time</Label>
            <Input
              id="transaction_datetime"
              type="datetime-local"
              {...register("transaction_datetime", {
                required: "Date is required",
              })}
            />
            {errors.transaction_datetime && (
              <p className="text-xs font-medium text-destructive">
                {errors.transaction_datetime.message}
              </p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description (Optional)</Label>
            <Textarea
              id="description"
              placeholder="Add more details..."
              className="resize-none"
              {...register("description", {
                maxLength: { value: 500, message: "Max 500 characters" },
              })}
            />
            {errors.description && (
              <p className="text-xs font-medium text-destructive">
                {errors.description.message}
              </p>
            )}
          </div>

          <DialogFooter className="pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isEdit ? "Save Changes" : "Add Transaction"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
