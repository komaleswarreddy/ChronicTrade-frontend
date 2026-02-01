import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api, { setTokenGetter, setTokenRefresher } from '../lib/api'

const AuthContext = createContext(null)

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [accessToken, setAccessToken] = useState(null)
  const [loading, setLoading] = useState(true)

  // Check for existing session on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Try to get user info from API using refresh token
      checkAuthStatus()
    } else {
      setLoading(false)
    }
  }, [])

  const checkAuthStatus = async () => {
    try {
      // Try to refresh token to get current user
      const response = await fetch(`${API_BASE}/api/auth/refresh`, {
        method: 'POST',
        credentials: 'include', // Include cookies
      })

      if (response.ok) {
        const data = await response.json()
        setAccessToken(data.access_token)
        
        // Get user info
        const userResponse = await fetch(`${API_BASE}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${data.access_token}`,
          },
          credentials: 'include',
        })

        if (userResponse.ok) {
          const userData = await userResponse.json()
          setUser(userData)
        }
      }
    } catch (e) {
      console.warn('No existing session found:', e)
    } finally {
      setLoading(false)
    }
  }

  const register = async (email, password, fullName) => {
    try {
      const response = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email,
          password,
          full_name: fullName || null,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
      }

      const data = await response.json()
      setAccessToken(data.access_token)
      setUser(data.user)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email,
          password,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }

      const data = await response.json()
      setAccessToken(data.access_token)
      setUser(data.user)
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const refreshToken = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      const data = await response.json()
      setAccessToken(data.access_token)
      return data.access_token
    } catch (error) {
      console.error('Token refresh failed:', error)
      // Clear state on refresh failure
      setAccessToken(null)
      setUser(null)
      return null
    }
  }, [])

  const getToken = useCallback(async () => {
    // Return current token if available
    if (accessToken) {
      return accessToken
    }

    // Try to refresh token
    const newToken = await refreshToken()
    return newToken
  }, [accessToken, refreshToken])

  // Set token getter and refresher for api.js
  useEffect(() => {
    setTokenGetter(getToken)
    setTokenRefresher(refreshToken)
  }, [getToken, refreshToken])

  const logout = async () => {
    try {
      await fetch(`${API_BASE}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      setAccessToken(null)
    }
  }

  const getEmail = () => {
    return user?.email || null
  }

  const isAuthenticated = () => {
    return !!accessToken && !!user
  }

  const contextValue = {
    user,
    loading,
    accessToken,
    register,
    login,
    logout,
    getToken,
    getEmail,
    isAuthenticated,
    refreshToken,
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    // Return safe defaults during SSR or if context is not available
    if (typeof window === 'undefined') {
      return {
        user: null,
        loading: true,
        accessToken: null,
        register: async () => ({ success: false, error: 'Not available' }),
        login: async () => ({ success: false, error: 'Not available' }),
        logout: async () => {},
        getToken: async () => null,
        getEmail: () => null,
        isAuthenticated: () => false,
        refreshToken: async () => null,
      }
    }
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
