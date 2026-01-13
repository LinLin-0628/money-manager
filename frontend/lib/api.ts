// lib/axios.ts
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  withCredentials: true, // Crucial for sending/receiving refresh token cookies
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
  setAccessToken: any,
  logout: any,
) => {
  // Request Interceptor: Attach Access Token
  const reqInterceptor = api.interceptors.request.use(
    (config) => {
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

      // Backend returns refresh: true when access token is invalid
      if (
        error.response?.data?.details?.expired === true &&
        !originalRequest._retry
      ) {
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
          // AuthService.refresh_tokens will set a new refresh cookie and return access_token
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
          // If refresh fails or backend signals logout: true
          processQueue(refreshError, null);
          logout();
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      // Explicit logout signal from backend
      if (error.response?.data?.logout === true) {
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
