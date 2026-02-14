"use client";

import React from "react";
import {
  ArrowUpCircle,
  ArrowDownCircle,
  Pencil,
  Trash2,
  Calendar,
  Wallet,
  Tag
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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

interface TransactionCardProps {
  transaction: Transaction;
  onEdit: (transaction: Transaction) => void;
  onDelete: (transaction: Transaction) => void;
  isDeleting?: boolean;
}

export function TransactionCard({
  transaction,
  onEdit,
  onDelete,
  isDeleting = false,
}: TransactionCardProps) {
  const isIncome = transaction.type === "income";

  const formattedAmount = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(transaction.amount);

  const formattedDate = new Date(transaction.transaction_datetime).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="group relative flex items-center justify-between gap-4 overflow-hidden rounded-lg border bg-card p-4 transition-all hover:shadow-md">
      <div className="flex items-center gap-4">
        {/* Type Icon */}
        <div className={cn(
          "flex h-10 w-10 shrink-0 items-center justify-center rounded-full",
          isIncome ? "bg-emerald-500/10 text-emerald-500" : "bg-destructive/10 text-destructive"
        )}>
          {isIncome ? <ArrowUpCircle className="h-6 w-6" /> : <ArrowDownCircle className="h-6 w-6" />}
        </div>

        {/* Title and Category */}
        <div className="flex flex-col min-w-0">
          <span className="text-sm font-bold capitalize truncate">
            {transaction.title}
          </span>
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1 capitalize">
              <Tag className="h-3 w-3" />
              {transaction.category.name}
            </span>
            <span className="hidden sm:flex items-center gap-1 capitalize">
              <Wallet className="h-3 w-3" />
              {transaction.account.name}
            </span>
            <span className="hidden sm:flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              {formattedDate}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Amount */}
        <div className={cn(
          "text-right font-bold whitespace-nowrap",
          isIncome ? "text-emerald-500" : "text-destructive"
        )}>
          {isIncome ? "+" : "-"}{formattedAmount}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onEdit(transaction)}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-destructive hover:bg-destructive/10 hover:text-destructive"
            onClick={() => onDelete(transaction)}
            disabled={isDeleting}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
