'use client'

import { useState, useEffect } from 'react'
import api from '../lib/api'
import { useAuth } from '../contexts/AuthContext'

export default function CapitalSummaryPanel() {
  const [capital, setCapital] = useState(null)
  const [exposure, setExposure] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    if (isAuthenticated()) {
      fetchCapitalData()
    }
  }, [isAuthenticated])

  const fetchCapitalData = async () => {
    if (!isAuthenticated()) return
    
    setLoading(true)
    setError(null)
    
    try {
      // api.js interceptor will automatically add the JWT token
      const [capitalRes, exposureRes] = await Promise.all([
        api.get(`/api/portfolio/capital`),
        api.get(`/api/portfolio/exposure`)
      ])
      
      setCapital(capitalRes.data)
      setExposure(exposureRes.data)
    } catch (err) {
      console.error('Failed to fetch capital data:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to fetch capital data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Capital Summary</h3>
        <div className="text-red-600">{error}</div>
        <button
          onClick={fetchCapitalData}
          className="mt-4 px-4 py-2 bg-wine-500 text-white rounded hover:bg-wine-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Capital Summary</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {capital && (
          <div className="p-4 bg-gray-50 rounded">
            <div className="text-sm text-gray-600 mb-1">Total Capital</div>
            <div className="text-2xl font-bold text-gray-900">
              ₹{capital.total_capital?.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Available: ₹{capital.available_capital?.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
            </div>
          </div>
        )}
        
        {exposure && (
          <div className="p-4 bg-gray-50 rounded">
            <div className="text-sm text-gray-600 mb-1">Current Exposure</div>
            <div className="text-2xl font-bold text-gray-900">
              ₹{exposure.total_exposure?.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {capital?.total_capital ? (
                `${((exposure.total_exposure / capital.total_capital) * 100).toFixed(1)}% of capital`
              ) : 'N/A'}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
