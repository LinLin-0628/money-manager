"use client";

import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

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

  // Use a ref to prevent double-initialization in React Strict Mode
  const isMounted = useRef(false);

  const logout = () => {
    setAccessToken(null);
    router.push('/login');
  };

  // 1. SESSION RESTORATION (The "Silent Refresh")
  useEffect(() => {
    if (isMounted.current) return;
    isMounted.current = true;

    const restoreSession = async () => {
      try {
        // IMPORTANT: Ensure your axios instance has { withCredentials: true }
        // This is what forces the browser to send the HttpOnly refresh_token cookie
        const { data } = await api.post('/api/auth/refresh', {}, { withCredentials: true });

        if (data.access_token) {
          setAccessToken(data.access_token);
          console.log("Session restored successfully");
        }
      } catch (error) {
        console.warn("No valid refresh token found or session expired.");
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  // 2. INTERCEPTORS
  useEffect(() => {
    // Request Interceptor: Attach current token to outgoing requests
    const reqInterceptor = api.interceptors.request.use((config) => {
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
      // Ensure all requests from this instance send cookies
      config.withCredentials = true;
      return config;
    });

    // Response Interceptor: Handle 401s and "expired: true"
    const resInterceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Backend signal: { details: { expired: true } }
        const isExpired = error.response?.data?.details?.expired === true;

        if (isExpired && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            const { data } = await api.post('/api/auth/refresh', {}, { withCredentials: true });
            const newAccessToken = data.access_token;

            setAccessToken(newAccessToken);
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

            return api(originalRequest);
          } catch (refreshError) {
            logout();
            return Promise.reject(refreshError);
          }
        }

        // Backend signal: { logout: true }
        if (error.response?.data?.logout === true) {
          logout();
        }

        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.request.eject(reqInterceptor);
      api.interceptors.response.eject(resInterceptor);
    };
  }, [accessToken]);

  return (
    <AuthContext.Provider value={{ accessToken, setAccessToken, logout, isLoading }}>
      {!isLoading ? (
        children
      ) : (
        <div className="flex min-h-screen items-center justify-center bg-background">
          <div className="flex flex-col items-center gap-2">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            <p className="text-sm text-muted-foreground">Checking session...</p>
          </div>
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
