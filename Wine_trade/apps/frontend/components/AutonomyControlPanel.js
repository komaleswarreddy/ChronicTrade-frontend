'use client'

import { useState, useEffect } from 'react'
import api from '../lib/api'
import { useAuth } from '../contexts/AuthContext'

export default function AutonomyControlPanel() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [enabling, setEnabling] = useState(false)
  const [disabling, setDisabling] = useState(false)
  const [showEnableConfirm, setShowEnableConfirm] = useState(false)
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    if (isAuthenticated()) {
      fetchStatus()
    }
  }, [isAuthenticated])

  const fetchStatus = async () => {
    if (!isAuthenticated()) return
    
    setLoading(true)
    setError(null)
    
    try {
      // api.js interceptor will automatically add the JWT token
      const response = await api.get(`/api/autonomy/status`)
      
      setStatus(response.data)
    } catch (err) {
      console.error('Failed to fetch autonomy status:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to fetch status')
    } finally {
      setLoading(false)
    }
  }

  const handleEnable = async () => {
    if (!isAuthenticated() || !showEnableConfirm) return
    
    setEnabling(true)
    setError(null)
    
    try {
      // api.js interceptor will automatically add the JWT token
      const response = await api.post(`/api/autonomy/enable`, {
        policy_name: 'default_policy',
        max_daily_trades: 1,  // Hard limit
        confidence_threshold: 0.85,  // Hard limit
        risk_threshold: 0.30  // Hard limit
      })
      
      setShowEnableConfirm(false)
      await fetchStatus()
      alert('Autonomy enabled with strict limits:\n- Max 1 trade per day\n- Confidence >= 85%\n- Risk <= 30%')
    } catch (err) {
      console.error('Failed to enable autonomy:', err)
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to enable autonomy'
      
      // Handle kill switch error specifically
      if (err.response?.status === 403 && errorMessage.includes('kill switch')) {
        setError('Autonomy is disabled by kill switch. Please contact an administrator to enable autonomy.')
      } else {
        setError(errorMessage)
      }
    } finally {
      setEnabling(false)
    }
  }

  const handleDisable = async () => {
    if (!isAuthenticated()) return
    
    const confirmed = window.confirm(
      'Are you sure you want to DISABLE autonomy?\n\n' +
      'This will activate the kill switch and immediately halt all autonomous execution.'
    )
    
    if (!confirmed) return
    
    setDisabling(true)
    setError(null)
    
    try {
      // api.js interceptor will automatically add the JWT token
      const response = await api.post(`/api/autonomy/disable`)
      
      await fetchStatus()
      alert('Autonomy disabled. Kill switch activated.')
    } catch (err) {
      console.error('Failed to disable autonomy:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to disable autonomy')
    } finally {
      setDisabling(false)
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

  if (error && !status) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Autonomy Control</h3>
        <div className="text-red-600">{error}</div>
        <button
          onClick={fetchStatus}
          className="mt-4 px-4 py-2 bg-wine-500 text-white rounded hover:bg-wine-700"
        >
          Retry
        </button>
      </div>
    )
  }

  const isEnabled = status?.autonomy_enabled || false
  const killSwitchActive = status?.kill_switch_active || false

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Autonomy Control</h3>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          isEnabled && !killSwitchActive
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        }`}>
          {isEnabled && !killSwitchActive ? 'Enabled' : 'Disabled'}
        </div>
      </div>

      {killSwitchActive && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
          <p className="text-sm text-red-800">
            <strong>Kill Switch Active:</strong> Autonomy is disabled by kill switch.
          </p>
        </div>
      )}

      <div className="space-y-4">
        {!isEnabled || killSwitchActive ? (
          <div>
            {!showEnableConfirm ? (
              <button
                onClick={() => setShowEnableConfirm(true)}
                className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
              >
                Enable Autonomy
              </button>
            ) : (
              <div className="space-y-2">
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded text-sm">
                  <p className="font-medium text-yellow-800 mb-2">Strict Limits Will Apply:</p>
                  <ul className="list-disc list-inside text-yellow-700 space-y-1">
                    <li>Maximum 1 trade per day</li>
                    <li>Confidence threshold: 85% minimum</li>
                    <li>Risk threshold: 30% maximum</li>
                  </ul>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleEnable}
                    disabled={enabling}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors disabled:opacity-50"
                  >
                    {enabling ? 'Enabling...' : 'Confirm Enable'}
                  </button>
                  <button
                    onClick={() => setShowEnableConfirm(false)}
                    disabled={enabling}
                    className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <button
            onClick={handleDisable}
            disabled={disabling}
            className="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors disabled:opacity-50"
          >
            {disabling ? 'Disabling...' : 'Disable Autonomy'}
          </button>
        )}

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-800">
            {error}
          </div>
        )}

        {status && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Trades Today:</span>
                <span className="ml-2 font-medium">{status.total_trades_today || 0}</span>
              </div>
              <div>
                <span className="text-gray-600">Value Today:</span>
                <span className="ml-2 font-medium">${(status.total_value_today || 0).toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
