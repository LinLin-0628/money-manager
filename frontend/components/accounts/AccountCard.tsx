"use client";

import React from "react";
import { Wallet, Pencil, Trash2, Calendar } from "lucide-react";
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

interface Account {
  id: number;
  name: string;
  balance: number;
  description: string | null;
  created_at: string;
  updated_at: string;
}

interface AccountCardProps {
  account: Account;
  onEdit: (account: Account) => void;
  onDelete: (account: Account) => void;
  isDeleting?: boolean;
}

export function AccountCard({
  account,
  onEdit,
  onDelete,
  isDeleting = false,
}: AccountCardProps) {
  const formattedBalance = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(account.balance);

  const formattedDate = new Date(account.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <Card className="group relative overflow-hidden transition-all hover:shadow-md">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Wallet className="h-4 w-4" />
            </div>
            <CardTitle className="text-lg font-bold capitalize">
              {account.name}
            </CardTitle>
          </div>
          <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onEdit(account)}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-destructive hover:bg-destructive/10 hover:text-destructive"
              onClick={() => onDelete(account)}
              disabled={isDeleting}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
        {account.description && (
          <CardDescription className="line-clamp-1">
            {account.description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent className="pb-4">
        <div className="text-2xl font-bold text-primary">
          {formattedBalance}
        </div>
      </CardContent>
      <CardFooter className="flex items-center gap-2 border-t bg-muted/30 px-6 py-2 text-[10px] text-muted-foreground">
        <Calendar className="h-3 w-3" />
        <span>Created on {formattedDate}</span>
      </CardFooter>
    </Card>
  );
}
