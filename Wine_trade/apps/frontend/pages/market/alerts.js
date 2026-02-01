'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import DashboardLayout from '../../components/DashboardLayout'
import api from '../../lib/api'
import AlertCard from '../../components/AlertCard'

export default function MarketAlerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshingAlerts, setRefreshingAlerts] = useState(false)
  const { user, loading: authLoading, isAuthenticated } = useAuth()

  const fetchAlerts = async () => {
    if (authLoading || !user || !isAuthenticated()) return
    
    try {
      setLoading(true)
      const response = await api.get('/api/alerts?limit=50')
      const alertsData = response.data || []
      setAlerts(alertsData)
    } catch (err) {
      console.warn('Failed to fetch alerts:', err.response?.status || err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!authLoading && user && isAuthenticated()) {
      fetchAlerts()
    }
  }, [authLoading, user, isAuthenticated])

  return (
    <DashboardLayout>
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Recent Alerts</h1>
            <p className="text-gray-600">Stay informed about market changes</p>
          </div>
          <button
            onClick={async () => {
              setRefreshingAlerts(true)
              await fetchAlerts()
              setRefreshingAlerts(false)
            }}
            disabled={refreshingAlerts}
            className="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50 flex items-center gap-1"
          >
            <svg 
              className={`w-4 h-4 ${refreshingAlerts ? 'animate-spin' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {refreshingAlerts ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading alerts...</p>
        </div>
      ) : alerts.length > 0 ? (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <AlertCard 
              key={alert.id} 
              alert={alert} 
              onMarkRead={(alertId) => {
                setAlerts(alerts.map(a => a.id === alertId ? {...a, read: true} : a))
              }}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No alerts at this time
        </div>
      )}
    </DashboardLayout>
  )
}
