"use client";

import React from "react";
import {
  Pencil,
  Trash2,
  Calendar,
  AlertCircle,
  Wallet
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

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

interface BudgetCardProps {
  budget: Budget;
  onEdit: (budget: Budget) => void;
  onDelete: (budget: Budget) => void;
  isDeleting?: boolean;
}

export function BudgetCard({
  budget,
  onEdit,
  onDelete,
  isDeleting = false,
}: BudgetCardProps) {
  const percentUsed = Math.min(budget.percent_used * 100, 100);
  const isWarning = budget.percent_used >= 0.8 && budget.percent_used <= 1;
  const isOver = budget.is_overspent;

  const monthDate = new Date(budget.month);
  // Re-adjusting if timezone causes the first of the month to shift back to previous month
  const adjustedDate = new Date(monthDate.getUTCFullYear(), monthDate.getUTCMonth(), 1);
  const formattedMonth = adjustedDate.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  });

  return (
    <Card className="group relative overflow-hidden transition-all hover:shadow-md">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-full",
                isOver ? "bg-destructive/10 text-destructive" : "bg-primary/10 text-primary"
              )}
            >
              <Wallet className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-lg font-bold capitalize">
                {budget.category.name}
              </CardTitle>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Calendar className="h-3 w-3" />
                <span>{formattedMonth}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onEdit(budget)}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-destructive hover:bg-destructive/10 hover:text-destructive"
              onClick={() => onDelete(budget)}
              disabled={isDeleting}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 pt-2">
        <div className="flex items-end justify-between">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Spent</p>
            <p className="text-lg font-semibold">
              ${Number(budget.actual_spent).toFixed(2)}
            </p>
          </div>
          <div className="text-right space-y-1">
            <p className="text-xs text-muted-foreground">Budget</p>
            <p className="text-sm font-medium text-muted-foreground">
              ${Number(budget.amount).toFixed(2)}
            </p>
          </div>
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className={cn(
                "font-medium",
                isOver ? "text-destructive" : isWarning ? "text-amber-500" : "text-primary"
            )}>
                {(budget.percent_used * 100).toFixed(1)}% used
            </span>
            <span className="text-muted-foreground">
                {isOver ? (
                    <span className="flex items-center gap-1 text-destructive font-medium">
                        <AlertCircle className="h-3 w-3" />
                        OVER BY ${(budget.actual_spent - budget.amount).toFixed(2)}
                    </span>
                ) : (
                    `$${Number(budget.remaining).toFixed(2)} remaining`
                )}
            </span>
          </div>
          <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
            <div
              className={cn(
                "h-full transition-all duration-500",
                isOver ? "bg-destructive" : isWarning ? "bg-amber-500" : "bg-primary"
              )}
              style={{ width: `${percentUsed}%` }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
