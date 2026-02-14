"use client";

import React from "react";
import { Tag, Pencil, Trash2, Calendar, TrendingUp, TrendingDown } from "lucide-react";
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

interface Category {
  id: number;
  name: string;
  type: "income" | "expense";
  created_at: string;
  updated_at: string;
}

interface CategoryCardProps {
  category: Category;
  onEdit: (category: Category) => void;
  onDelete: (category: Category) => void;
  isDeleting?: boolean;
}

export function CategoryCard({
  category,
  onEdit,
  onDelete,
  isDeleting = false,
}: CategoryCardProps) {
  const isIncome = category.type === "income";

  const formattedDate = new Date(category.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <Card className="group relative overflow-hidden transition-all hover:shadow-md">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-full",
                isIncome ? "bg-emerald-500/10 text-emerald-500" : "bg-destructive/10 text-destructive"
              )}
            >
              {isIncome ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
            </div>
            <CardTitle className="text-lg font-bold capitalize">
              {category.name}
            </CardTitle>
          </div>
          <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onEdit(category)}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-destructive hover:bg-destructive/10 hover:text-destructive"
              onClick={() => onDelete(category)}
              disabled={isDeleting}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pb-4">
        <div
          className={cn(
            "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
            isIncome
              ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
              : "border-destructive/20 bg-destructive/10 text-destructive"
          )}
        >
          {isIncome ? "Income" : "Expense"}
        </div>
      </CardContent>
      <CardFooter className="flex items-center gap-2 border-t bg-muted/30 px-6 py-2 text-[10px] text-muted-foreground">
        <Calendar className="h-3 w-3" />
        <span>Created on {formattedDate}</span>
      </CardFooter>
    </Card>
  );
}
