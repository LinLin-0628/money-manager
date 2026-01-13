import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  withCredentials: true, // Required to send the refresh_token HttpOnly cookie
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

export const setupInterceptors = (
  accessToken: string | null,
  setAccessToken: (token: string | null) => void,
  logout: () => void,
) => {
  // Request Interceptor: Attach Access Token
  const reqInterceptor = api.interceptors.request.use(
    (config) => {
      // Only attach if we have a token and it hasn't been set manually
      if (accessToken && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${accessToken}`;
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

      // New Backend Structure Check:
      // error.response.data looks like: { "error": { "message": "...", "details": { "expired": true } } }
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
          // Call /api/auth/refresh which rotates tokens and sets new cookie
          // Returns AccessToken schema: { access_token: string, token_type: "bearer" }
          const response = await axios.post(
            `${api.defaults.baseURL}/api/auth/refresh`,
            {},
            { withCredentials: true },
          );

          const { access_token } = response.data;
          setAccessToken(access_token);
          processQueue(null, access_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError: any) {
          // If refresh fails (e.g., RefreshTokenExpired), backend sends logout: true
          processQueue(refreshError, null);
          logout();
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      // 2. Handle Explicit Logout Signal
      // Triggered by RefreshTokenExpired or RevokedToken in AuthService
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

export default api;
