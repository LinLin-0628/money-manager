"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
} from "react";
import { useRouter } from "next/navigation";
import api, { setupInterceptors } from "@/lib/api";

interface AuthContextType {
  accessToken: string | null;
  setAccessToken: (token: string | null) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Use a ref to ensure the initialization only runs once (prevents strict mode double-triggers)
  const isInitialized = useRef(false);

  const logout = () => {
    setAccessToken(null);
    // Note: You may want to call api.post("/api/auth/logout") here
    // to clear the cookie on the server as well.
    router.push("/login");
  };

  // 1. SILENT REFRESH (Restores session on hard refresh)
  useEffect(() => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    const restoreSession = async () => {
      try {
        /**
         * Your backend auth.py: @router.post("/refresh")
         * returns AccessToken(access_token=...)
         */
        const { data } = await api.post("/api/auth/refresh");
        setAccessToken(data.access_token);
        console.log("Auth: Session restored via refresh token.");
      } catch (error) {
        // We don't logout() here because the user might just be a guest
        console.warn("Auth: No active session found.");
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  // 2. INTERCEPTOR SYNC
  // We use the setupInterceptors from your lib/axios.ts to handle
  // the complex queueing and nested error objects from exception_handler.py
  useEffect(() => {
    const cleanup = setupInterceptors(accessToken, setAccessToken, logout);
    return () => cleanup();
  }, [accessToken]);

  return (
    <AuthContext.Provider
      value={{ accessToken, setAccessToken, logout, isLoading }}
    >
      {/* Critical: We don't render children until the silent refresh check is done.
          This prevents "flickering" where a user sees the login page for 100ms
          before being redirected to the dashboard.
      */}
      {!isLoading ? (
        children
      ) : (
        <div className="flex min-h-screen flex-col items-center justify-center bg-background">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="mt-4 text-sm font-medium text-muted-foreground">
            Verifying your session...
          </p>
        </div>
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};
