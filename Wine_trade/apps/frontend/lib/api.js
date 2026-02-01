import axios from "axios";

// Support both NEXT_PUBLIC_API_BASE and NEXT_PUBLIC_API_BASE_URL for compatibility
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE;

if (!API_BASE) {
  throw new Error(
    "NEXT_PUBLIC_API_BASE_URL or NEXT_PUBLIC_API_BASE is not defined. Refusing to start frontend. " +
    "Please set NEXT_PUBLIC_API_BASE_URL in your Render environment variables or NEXT_PUBLIC_API_BASE in .env.local file."
  );
}

// Log API base URL on module load (for debugging)
if (typeof window !== "undefined") {
  console.log("🌐 API BASE:", API_BASE);
}

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  timeout: 60000, // 60 seconds - increased for RAG queries that may need to download models
  headers: {
    "Content-Type": "application/json",
  },
});

// Token getter function - will be set by AuthContext
let tokenGetter = null;

export function setTokenGetter(getter) {
  tokenGetter = getter;
}

// Add request interceptor to automatically add JWT token in Authorization header
api.interceptors.request.use(
  async (config) => {
    // Only add Authorization if not already set (allows manual override)
    if (!config.headers['Authorization'] && typeof window !== 'undefined' && tokenGetter) {
      try {
        const token = await tokenGetter();
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
      } catch (error) {
        console.warn('Failed to get token for request:', error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Token refresh function - will be set by AuthContext
let tokenRefresher = null;

export function setTokenRefresher(refresher) {
  tokenRefresher = refresher;
}

// Add response interceptor for automatic token refresh on 401
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Try to refresh token
        if (tokenRefresher) {
          const newToken = await tokenRefresher();
          
          if (newToken) {
            processQueue(null, newToken);
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            isRefreshing = false;
            return api(originalRequest);
          }
        }
        
        // Refresh failed - clear auth and redirect
        processQueue(new Error('Token refresh failed'), null);
        isRefreshing = false;
        
        if (typeof window !== 'undefined' && window.location.pathname !== '/sign-in') {
          window.location.href = '/sign-in';
        }
        
        return Promise.reject(error);
      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;
        
        if (typeof window !== 'undefined' && window.location.pathname !== '/sign-in') {
          window.location.href = '/sign-in';
        }
        
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
