import Link from 'next/link'
import { useAuth } from '../contexts/AuthContext'
import { useRouter } from 'next/router'
import { useState, useEffect } from 'react'

export default function NavBar(){
  const { user, logout, isAuthenticated } = useAuth()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
  }, [])
  
  const handleLogout = () => {
    logout()
    router.push('/sign-in')
  }
  
  // Prevent hydration mismatch
  if (!mounted) {
    return (
      <header className="bg-white shadow-md">
        <div className="max-w-6xl mx-auto p-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-wine-700 font-bold text-xl hover:text-wine-500">Wine Invest</Link>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-20 h-8 bg-gray-200 animate-pulse rounded"></div>
          </div>
        </div>
      </header>
    )
  }
  
  return (
    <header className="bg-white shadow-md">
      <div className="max-w-6xl mx-auto p-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard" className="text-wine-700 font-bold text-xl hover:text-wine-500">Wine Invest</Link>
        </div>

        <div className="flex items-center gap-3">
          {!isAuthenticated() ? (
            <>
              <Link href="/sign-in">
                <button className="px-4 py-2 bg-wine-500 text-white rounded hover:bg-wine-700 transition-colors">
                  Sign In
                </button>
              </Link>
            </>
          ) : (
            <div className="flex items-center gap-3">
              <div className="text-sm text-gray-600 hidden sm:block font-lato">
                {user?.email || 'User'}
              </div>
              <button 
                onClick={handleLogout}
                className="px-4 py-2 bg-[#800020] text-white rounded-lg hover:bg-[#7b1730] transition-all duration-200 font-lato font-medium shadow-sm hover:shadow-md"
              >
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

