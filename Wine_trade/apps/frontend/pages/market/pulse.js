'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import DashboardLayout from '../../components/DashboardLayout'
import api from '../../lib/api'
import MarketPulseCard from '../../components/MarketPulseCard'

export default function MarketPulse() {
  const [marketPulse, setMarketPulse] = useState({})
  const [loading, setLoading] = useState(true)
  const { user, loading: authLoading, isAuthenticated } = useAuth()

  const fetchData = async () => {
    if (authLoading || !user || !isAuthenticated()) {
      setLoading(false)
      return
    }
    
    try {
      setLoading(true)
      const pulseRes = await api.get('/api/market/pulse')
      setMarketPulse(pulseRes.data || {})
    } catch (err) {
      console.error('Failed to fetch market pulse:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!authLoading && user && isAuthenticated()) {
      fetchData()
    }
  }, [authLoading, user, isAuthenticated])

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Market Pulse</h1>
        <p className="text-gray-600">Real-time market trends by region</p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading market data...</p>
        </div>
      ) : Object.keys(marketPulse).length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
          {Object.entries(marketPulse).map(([region, change]) => (
            <MarketPulseCard key={region} region={region} change={change} />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No market pulse data available
        </div>
      )}
    </DashboardLayout>
  )
}
