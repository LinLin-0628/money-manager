"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { AlertCircle, Loader2, X } from "lucide-react";
import { useRouter } from "next/navigation";

// Shadcn UI Components
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

// Custom API instance
import api from "@/lib/api";

export default function SignUpPage() {
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      name: "",
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: any) => {
    setShowError(false);
    try {
      /** * Sends the user registration data to the FastAPI backend.
       * The backend hashes the password and saves the user.
       */
      await api.post("/api/users/register", {
        name: data.name,
        email: data.email,
        password: data.password,
      });

      // On success, redirect to login page as requested
      router.push("/login");
    } catch (error: any) {
      /**
       * Handles registration errors.
       * Specifically catches the 'UserAlreadyExists' error raised by the service.
       */
      const msg =
        error.response?.data?.detail ||
        "An unexpected error occurred during registration.";
      setErrorMessage(msg);
      setShowError(true);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-background p-4 text-foreground">
      {/* Sign Up Card */}
      <Card className="w-full max-w-md border-border shadow-lg">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">
            Create an Account
          </CardTitle>
          <CardDescription>
            Enter your details below to create your account.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Name Field */}
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                {...register("name", { required: "Name is required" })}
              />
              {errors.name && (
                <p className="text-xs font-medium text-destructive">
                  {errors.name.message}
                </p>
              )}
            </div>

            {/* Email Field */}
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="name@example.com"
                {...register("email", { required: "Email is required" })}
              />
              {errors.email && (
                <p className="text-xs font-medium text-destructive">
                  {errors.email.message}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                {...register("password", {
                  required: "Password is required",
                  minLength: { value: 8, message: "Minimum 8 characters" },
                })}
              />
              {errors.password && (
                <p className="text-xs font-medium text-destructive">
                  {errors.password.message}
                </p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Register
            </Button>
          </form>
        </CardContent>

        <CardFooter className="flex justify-center border-t pt-4">
          <p className="text-sm text-muted-foreground">
            Already have an account?{" "}
            <Button
              variant="link"
              className="p-0 h-auto font-semibold"
              onClick={() => router.push("/login")}
            >
              Login
            </Button>
          </p>
        </CardFooter>
      </Card>

      {/* Error Alert */}
      {showError && (
        <div className="fixed bottom-6 right-6 w-full max-w-sm animate-in fade-in slide-in-from-right-5">
          <Alert variant="destructive" className="relative shadow-2xl">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{errorMessage}</AlertDescription>
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-2 h-6 w-6 hover:bg-destructive/20"
              onClick={() => setShowError(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </Alert>
        </div>
      )}
    </div>
  );
}
