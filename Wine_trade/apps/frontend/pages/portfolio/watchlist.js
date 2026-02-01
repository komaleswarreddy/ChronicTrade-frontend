'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import DashboardLayout from '../../components/DashboardLayout'
import api from '../../lib/api'
import WatchlistCard from '../../components/WatchlistCard'

export default function PortfolioWatchlist() {
  const [watchlist, setWatchlist] = useState([])
  const [loading, setLoading] = useState(true)
  const { user, loading: authLoading, isAuthenticated } = useAuth()

  const fetchWatchlist = async () => {
    if (authLoading || !user || !isAuthenticated()) {
      setLoading(false)
      return
    }
    
    try {
      setLoading(true)
      const watchlistRes = await api.get('/api/watchlist')
      setWatchlist(watchlistRes.data?.items || [])
    } catch (err) {
      console.error('Failed to fetch watchlist:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!authLoading && user && isAuthenticated()) {
      fetchWatchlist()
    }
  }, [authLoading, user, isAuthenticated])

  const handleWatchlistRemove = async (assetId) => {
    try {
      await api.post('/api/watchlist/remove', { asset_id: assetId })
      await fetchWatchlist()
    } catch (err) {
      console.error('Failed to remove from watchlist:', err)
      alert('Failed to remove from watchlist. Please try again.')
    }
  }

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Watchlist</h1>
        <p className="text-gray-600">Track assets you're interested in</p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading watchlist...</p>
        </div>
      ) : (
        <WatchlistCard 
          watchlist={watchlist} 
          onRemove={handleWatchlistRemove}
        />
      )}
    </DashboardLayout>
  )
}
