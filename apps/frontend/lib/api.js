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
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add axios interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('Authentication error (401): Token may be expired or invalid')
    }
    return Promise.reject(error)
  }
);

export default api;
