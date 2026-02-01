'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import DashboardLayout from '../../components/DashboardLayout'
import api from '../../lib/api'
import HoldingsTable from '../../components/HoldingsTable'

export default function PortfolioHoldings() {
  const [holdings, setHoldings] = useState([])
  const [watchlist, setWatchlist] = useState([])
  const [loading, setLoading] = useState(true)
  const { user, loading: authLoading, isAuthenticated } = useAuth()

  const fetchData = async () => {
    if (authLoading || !user || !isAuthenticated()) {
      setLoading(false)
      return
    }
    
    try {
      setLoading(true)
      const [holdingsRes, watchlistRes] = await Promise.allSettled([
        api.get('/api/holdings/active'),
        api.get('/api/watchlist')
      ])
      
      if (holdingsRes.status === 'fulfilled') {
        setHoldings(holdingsRes.value.data || [])
      }
      
      if (watchlistRes.status === 'fulfilled') {
        setWatchlist(watchlistRes.value.data?.items || [])
      }
    } catch (err) {
      console.error('Failed to fetch holdings:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!authLoading && user && isAuthenticated()) {
      fetchData()
    }
  }, [authLoading, user, isAuthenticated])

  const handleWatchlistToggle = async (assetId) => {
    try {
      const checkRes = await api.get(`/api/watchlist/check/${assetId}`)
      const isCurrentlyInWatchlist = checkRes.data?.in_watchlist || false
      
      if (isCurrentlyInWatchlist) {
        await api.post('/api/watchlist/remove', { asset_id: assetId })
      } else {
        await api.post('/api/watchlist/add', { asset_id: assetId })
      }
      
      const watchlistRes = await api.get('/api/watchlist')
      setWatchlist(watchlistRes.data?.items || [])
    } catch (err) {
      console.error('Failed to toggle watchlist:', err)
    }
  }

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Holdings</h1>
        <p className="text-gray-600">Manage your current wine portfolio</p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading holdings...</p>
        </div>
      ) : (
        <HoldingsTable 
          holdings={holdings} 
          onWatchlistToggle={handleWatchlistToggle} 
          watchlist={watchlist}
          onHoldingsUpdate={fetchData}
        />
      )}
    </DashboardLayout>
  )
}
