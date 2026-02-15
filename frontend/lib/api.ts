import axios from "axios";

const getBaseURL = () => {
  // If we're on the server, use the internal API_URL
  if (typeof window === "undefined") {
    return process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://backend:8000";
  }
  // If we're on the client, use the NEXT_PUBLIC_API_URL
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
};

const api = axios.create({
  baseURL: getBaseURL(),
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

// 🔥 SOLUTION: Store the token getter as a module-level variable
// This will be updated by AuthContext and always returns current token
let tokenGetter: () => string | null = () => null;

export const setTokenGetter = (getter: () => string | null) => {
  tokenGetter = getter;
};

export const setupInterceptors = (
  setAccessToken: (token: string | null) => void,
  logout: () => void,
) => {
  // Request Interceptor: Attach Access Token
  const reqInterceptor = api.interceptors.request.use(
    (config) => {
      // 🔥 FIX: Always get the CURRENT token from the getter
      const currentToken = tokenGetter();
      if (currentToken && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${currentToken}`;
      }
      return config;
    },
    (error) => Promise.reject(error),
  );

  // Response Interceptor: Handle Expiry and Refresh
  const resInterceptor = api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      const errorPayload = error.response?.data?.error;
      const details = errorPayload?.details;

      // 1. Handle Access Token Expiration
      if (details?.expired === true && !originalRequest._retry) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return api(originalRequest);
            })
            .catch((err) => Promise.reject(err));
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          const response = await axios.post(
            "/api/auth/refresh",
            {},
            { withCredentials: true }
          );

          const { access_token } = response.data;
          setAccessToken(access_token);
          processQueue(null, access_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError: any) {
          processQueue(refreshError, null);
          logout();
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      // 2. Handle Explicit Logout Signal
      if (details?.logout === true) {
        logout();
      }

      return Promise.reject(error);
    },
  );

  return () => {
    api.interceptors.request.eject(reqInterceptor);
    api.interceptors.response.eject(resInterceptor);
  };
};

/**
 * Helper to forward headers from Next.js API Routes to the backend.
 * This ensures that the proxy correctly passes the Authorization token
 * and the Refresh Token cookie.
 */
export async function getProxyConfig() {
  // Dynamic import to avoid issues in client-side bundles
  const { headers } = await import("next/headers");
  const headersList = await headers();

  const config: any = {
    headers: {},
  };

  const authHeader = headersList.get("authorization");
  if (authHeader) {
    config.headers.Authorization = authHeader;
  }

  const cookieHeader = headersList.get("cookie");
  if (cookieHeader) {
    config.headers.Cookie = cookieHeader;
  }

  return config;
}

export default api;
