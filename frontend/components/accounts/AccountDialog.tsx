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
import { Loader2 } from "lucide-react";

interface Account {
  id: number;
  name: string;
  balance: number;
  description: string | null;
}

interface AccountDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  account?: Account | null;
  isLoading?: boolean;
}

export function AccountDialog({
  isOpen,
  onClose,
  onSubmit,
  account,
  isLoading = false,
}: AccountDialogProps) {
  const isEdit = !!account;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      name: "",
      balance: 0,
      description: "",
    },
  });

  // Reset form when account changes or dialog opens/closes
  useEffect(() => {
    if (account) {
      reset({
        name: account.name,
        balance: account.balance,
        description: account.description || "",
      });
    } else {
      reset({
        name: "",
        balance: 0,
        description: "",
      });
    }
  }, [account, reset, isOpen]);

  const handleFormSubmit = async (data: any) => {
    await onSubmit(data);
    if (!isLoading) {
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit Account" : "Add Account"}</DialogTitle>
          <DialogDescription>
            {isEdit
              ? "Update your account details below."
              : "Create a new account to track your finances."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="name">Account Name</Label>
            <Input
              id="name"
              placeholder="e.g. Main Savings"
              {...register("name", {
                required: "Account name is required",
                maxLength: { value: 100, message: "Max 100 characters" },
              })}
            />
            {errors.name && (
              <p className="text-xs font-medium text-destructive">
                {errors.name.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="balance">Initial Balance</Label>
            <Input
              id="balance"
              type="number"
              step="0.01"
              disabled={isEdit}
              placeholder="0.00"
              {...register("balance", {
                required: "Initial balance is required",
                min: { value: 0, message: "Balance cannot be negative" },
              })}
            />
            {errors.balance && (
              <p className="text-xs font-medium text-destructive">
                {errors.balance.message}
              </p>
            )}
            {isEdit && (
              <p className="text-[10px] text-muted-foreground">
                Balance cannot be changed here. Use transactions to adjust balance.
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (Optional)</Label>
            <Input
              id="description"
              placeholder="e.g. Used for monthly bills"
              {...register("description", {
                maxLength: { value: 255, message: "Max 255 characters" },
              })}
            />
            {errors.description && (
              <p className="text-xs font-medium text-destructive">
                {errors.description.message}
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
            <Button type="submit" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isEdit ? "Save Changes" : "Create Account"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
