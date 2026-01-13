"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { AlertCircle, Loader2, X } from "lucide-react";
import { useRouter } from "next/navigation";

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
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

export default function LoginPage() {
  const [showError, setShowError] = useState(false); // Default to false
  const [errorMessage, setErrorMessage] = useState("");
  const { setAccessToken } = useAuth();
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: any) => {
    setShowError(false);

    try {
      // OAuth2PasswordBearer expects form-data usually, but
      // FastAPI's login can be handled via JSON or Form depending on your router.
      // Based on deps.py, it points to api/auth/login.

      const formData = new FormData();
      formData.append("username", data.email); // OAuth2 uses 'username' field
      formData.append("password", data.password);

      const response = await api.post("/api/auth/login", formData);

      // Store the access token in our Context State
      setAccessToken(response.data.access_token);

      // Redirect to dashboard or home after successful login
      router.push("/dashboard");
    } catch (error: any) {
      console.error("Login failed:", error);
      setErrorMessage(
        error.response?.data?.detail ||
          "Invalid credentials. Please check your email and password.",
      );
      setShowError(true);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-background p-4 text-foreground">
      {/* Login Card */}
      <Card className="w-full max-w-md border-border shadow-lg">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Login</CardTitle>
          <CardDescription>
            Enter your email and password to access your account.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <Button variant="link" size="sm" className="px-0 font-normal">
                  Forgot password?
                </Button>
              </div>
              <Input
                id="password"
                type="password"
                {...register("password", { required: "Password is required" })}
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
              Sign In
            </Button>
          </form>
        </CardContent>

        <CardFooter className="flex justify-center border-t pt-4">
          <p className="text-sm text-muted-foreground">
            Don't have an account?{" "}
            <Button variant="link" className="p-0 h-auto font-semibold">
              Sign up
            </Button>
          </p>
        </CardFooter>
      </Card>

      {/* Default Shadcn Alert - Fixed Bottom Right */}
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
