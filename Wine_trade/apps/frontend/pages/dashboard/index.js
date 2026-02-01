'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import DashboardLayout from '../../components/DashboardLayout'
import api from '../../lib/api'
import PortfolioCard from '../../components/PortfolioCard'
import PortfolioTrendChart from '../../components/PortfolioTrendChart'
import MarketPulseCard from '../../components/MarketPulseCard'

export default function DashboardOverview() {
  const [portfolioSummary, setPortfolioSummary] = useState(null)
  const [marketPulse, setMarketPulse] = useState({})
  const [trendData, setTrendData] = useState([])
  const [loading, setLoading] = useState(true)
  const [apiError, setApiError] = useState(null)
  const { user, loading: authLoading, isAuthenticated } = useAuth()

  const fetchDashboardData = async () => {
    if (authLoading || !user || !isAuthenticated()) {
      setLoading(false)
      return
    }
    
    try {
      setLoading(true)
      setApiError(null)
      
      const results = await Promise.allSettled([
        api.get('/api/portfolio/summary'),
        api.get('/api/market/pulse'),
        api.get(`/api/portfolio/trend?days=30&_t=${new Date().getTime()}`)
      ])
      
      const [summaryRes, pulseRes, trendRes] = results
      
      if (summaryRes.status === 'fulfilled') {
        setPortfolioSummary(summaryRes.value.data)
      } else {
        console.warn('Failed to fetch portfolio summary:', summaryRes.reason?.response?.status || summaryRes.reason?.message)
        setPortfolioSummary(null)
      }
      
      if (pulseRes.status === 'fulfilled') {
        setMarketPulse(pulseRes.value.data || {})
      } else {
        console.warn('Failed to fetch market pulse:', pulseRes.reason?.response?.status || pulseRes.reason?.message)
        setMarketPulse({})
      }
      
      if (trendRes.status === 'fulfilled') {
        const trendDataArray = trendRes.value.data || []
        setTrendData(trendDataArray)
      }
    } catch (err) {
      console.error('Critical error fetching dashboard data:', err)
      if (err.response?.status === 401) {
        setApiError('Authentication failed. Please sign out and sign in again.')
      } else if (!err.response) {
        setApiError('Cannot connect to backend. Make sure the backend is running on http://localhost:4000')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!authLoading && user && isAuthenticated()) {
      fetchDashboardData()
    }
  }, [authLoading, user, isAuthenticated])

  // Auto-refresh portfolio data every 30 seconds
  useEffect(() => {
    if (authLoading || !user || !isAuthenticated()) return
    
    const interval = setInterval(async () => {
      try {
        const timestamp = new Date().getTime()
        const [summaryRes, trendRes] = await Promise.allSettled([
          api.get('/api/portfolio/summary'),
          api.get(`/api/portfolio/trend?days=30&_t=${timestamp}`)
        ])
        
        if (summaryRes.status === 'fulfilled') {
          setPortfolioSummary(summaryRes.value.data)
        }
        if (trendRes.status === 'fulfilled') {
          const trendDataArray = trendRes.value.data || []
          setTrendData(trendDataArray)
        }
      } catch (err) {
        console.warn('Auto-refresh failed:', err)
      }
    }, 30000)
    
    return () => clearInterval(interval)
  }, [authLoading, user, isAuthenticated])

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome{user?.email ? `, ${user.email.split('@')[0]}` : ''}
        </h1>
        <p className="text-gray-600">Your wine trading intelligence dashboard</p>
      </div>

      {apiError && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg">
          <p className="font-semibold">Connection Error</p>
          <p className="text-sm mt-1">{apiError}</p>
          <p className="text-sm mt-2">Make sure the backend is running: <code className="bg-red-100 px-2 py-1 rounded">cd apps/backend && python start.py</code></p>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading dashboard data...</p>
        </div>
      ) : (
        <>
          {/* Portfolio Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <PortfolioCard 
              title="Total Portfolio Value" 
              value={portfolioSummary ? `₹${portfolioSummary.total_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '₹0.00'}
              change={portfolioSummary?.today_change}
              changePercent={portfolioSummary?.change_percent}
              subtitle={`${portfolioSummary?.bottles || 0} bottles across ${portfolioSummary?.regions?.split(',').length || 0} regions`}
            />
            <PortfolioCard 
              title="Today's Change" 
              value={portfolioSummary ? `₹${Math.abs(portfolioSummary.today_change).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '₹0.00'}
              change={portfolioSummary?.today_change}
              changePercent={portfolioSummary?.change_percent}
              subtitle="24 hour performance"
            />
            <PortfolioCard 
              title="Average ROI" 
              value={portfolioSummary ? `${portfolioSummary.avg_roi.toFixed(2)}%` : '0.00%'}
              subtitle="Across all holdings"
            />
          </div>

          {/* Portfolio Trend Chart */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Portfolio Trend (30 Days)</h3>
              <button
                onClick={async () => {
                  try {
                    const timestamp = new Date().getTime()
                    const random = Math.random()
                    const trendRes = await api.get(`/api/portfolio/trend?days=30&_t=${timestamp}&_r=${random}`)
                    const trendDataArray = trendRes.data || []
                    setTrendData(trendDataArray)
                  } catch (err) {
                    console.error('Failed to refresh trend:', err.response?.data || err.message)
                    alert('Failed to refresh trend data. Please try again.')
                  }
                }}
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                title="Refresh trend data"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
            </div>
            {trendData.length > 0 ? (
              <PortfolioTrendChart data={trendData} />
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p className="text-sm mb-2">No historical data available yet.</p>
                <p className="text-xs">Portfolio snapshots will appear here after transactions.</p>
              </div>
            )}
          </div>

          {/* Market Pulse */}
          {Object.keys(marketPulse).length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Pulse by Region</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
                {Object.entries(marketPulse).map(([region, change]) => (
                  <MarketPulseCard key={region} region={region} change={change} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </DashboardLayout>
  )
}
