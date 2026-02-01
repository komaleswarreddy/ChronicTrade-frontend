// Auth utilities for email-based authentication

export function getAuthToken() {
  // Return email as "token" for Authorization header
  if (typeof window === 'undefined') return null
  return localStorage.getItem('user_email')
}

export function isAuthenticated() {
  if (typeof window === 'undefined') return false
  return !!localStorage.getItem('user_email')
}

export function getAuthHeaders() {
  const email = getAuthToken()
  if (!email) {
    return {}
  }
  return {
    'Authorization': `Bearer ${email}`,
    'Content-Type': 'application/json'
  }
}
