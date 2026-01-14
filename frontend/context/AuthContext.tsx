"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
} from "react";
import { useRouter } from "next/navigation";
import api, { setupInterceptors, setTokenGetter } from "@/lib/api";

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

  // 🔥 FIX: Use ref to store current token, always accessible to interceptor
  const tokenRef = useRef<string | null>(null);

  // 🔥 FIX: Update both state and ref when token changes
  const updateAccessToken = (token: string | null) => {
    tokenRef.current = token;
    setAccessToken(token);
  };

  const isInitialized = useRef(false);

  const logout = () => {
    updateAccessToken(null);
    router.push("/login");
  };

  // 🔥 FIX: Set up the token getter ONCE before anything else
  useEffect(() => {
    // Provide the interceptor with a function that ALWAYS returns current token
    setTokenGetter(() => tokenRef.current);
  }, []);

  // 1. SILENT REFRESH (Restores session on hard refresh)
  useEffect(() => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    const restoreSession = async () => {
      try {
        const { data } = await api.post("/api/auth/refresh");
        updateAccessToken(data.access_token);
        console.log("Auth: Session restored via refresh token.");
      } catch (error) {
        console.warn("Auth: No active session found.");
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  // 2. INTERCEPTOR SETUP (Only needs to run once now!)
  useEffect(() => {
    const cleanup = setupInterceptors(updateAccessToken, logout);
    return () => cleanup();
  }, []); // 🔥 Empty deps - interceptor uses tokenRef which is always current

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        setAccessToken: updateAccessToken,
        logout,
        isLoading,
      }}
    >
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
