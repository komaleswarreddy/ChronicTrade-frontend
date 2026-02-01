'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import DashboardLayout from '../../components/DashboardLayout'
import api from '../../lib/api'
import ArbitrageCard from '../../components/ArbitrageCard'

export default function MarketArbitrage() {
  const [arbitrage, setArbitrage] = useState([])
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
      const [arbitrageRes, watchlistRes] = await Promise.allSettled([
        api.get('/api/arbitrage?limit=20'),
        api.get('/api/watchlist')
      ])
      
      if (arbitrageRes.status === 'fulfilled') {
        setArbitrage(arbitrageRes.value.data || [])
      }
      
      if (watchlistRes.status === 'fulfilled') {
        setWatchlist(watchlistRes.value.data?.items || [])
      }
    } catch (err) {
      console.error('Failed to fetch arbitrage:', err)
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Arbitrage Opportunities</h1>
        <p className="text-gray-600">Discover price differences across regions</p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading opportunities...</p>
        </div>
      ) : arbitrage.length > 0 ? (
        <div className="space-y-4">
          {arbitrage.map((opp, idx) => (
            <ArbitrageCard 
              key={idx} 
              opportunity={{
                ...opp,
                onBuySuccess: fetchData
              }}
              onWatchlistToggle={handleWatchlistToggle}
              isInWatchlist={watchlist.some(w => w.asset_id === opp.asset_id)}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No arbitrage opportunities at this time
        </div>
      )}
    </DashboardLayout>
  )
}
