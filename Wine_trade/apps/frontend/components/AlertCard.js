'use client'

import { useState } from 'react'
import api from '../lib/api'
import { useAuth } from '../contexts/AuthContext'

export default function AlertCard({ alert, onMarkRead }) {
  const [showExplanation, setShowExplanation] = useState(false)
  const [isMarkingRead, setIsMarkingRead] = useState(false)
  const [isRead, setIsRead] = useState(alert.read || false)
  const { isAuthenticated } = useAuth()

  const severityColors = {
    critical: 'bg-red-100 border-red-300 text-red-800',
    high: 'bg-orange-100 border-orange-300 text-orange-800',
    medium: 'bg-yellow-100 border-yellow-300 text-yellow-800',
    low: 'bg-blue-100 border-blue-300 text-blue-800'
  }
  
  const colorClass = severityColors[alert.severity] || severityColors.medium

  const handleMarkRead = async () => {
    if (isMarkingRead || !isAuthenticated()) return
    
    setIsMarkingRead(true)
    const wasRead = isRead
    
    // Optimistic update
    setIsRead(true)
    
    try {
      // api.js interceptor will automatically add the JWT token
      await api.patch(`/api/alerts/${alert.id}/read?read=true`, {})
      
      if (onMarkRead) {
        onMarkRead(alert.id)
      }
    } catch (err) {
      // Rollback on error
      setIsRead(wasRead)
      
      // Don't show error for 401 - just log it
      if (err.response?.status === 401) {
        console.warn('Authentication failed when marking alert as read')
      } else {
        console.error('Failed to mark alert as read:', err)
      }
    } finally {
      setIsMarkingRead(false)
    }
  }
  
  return (
    <div className={`${colorClass} p-4 rounded-lg border-2 shadow-sm hover:shadow-md transition-shadow ${!isRead ? 'ring-2 ring-opacity-50' : ''}`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wide">
              {alert.severity}
            </span>
            <span className="text-xs opacity-75">•</span>
            <span className="text-xs opacity-75">{alert.type}</span>
          </div>
          <p className="text-sm font-medium">{alert.message}</p>
        </div>
        <div className="flex items-center gap-2">
          {!isRead && (
            <div className="w-2 h-2 bg-current rounded-full opacity-75 animate-pulse"></div>
          )}
          {!isRead && isAuthenticated() && (
            <button
              onClick={handleMarkRead}
              disabled={isMarkingRead}
              className="text-xs px-2 py-1 bg-white bg-opacity-50 rounded hover:bg-opacity-75 transition-colors disabled:opacity-50"
            >
              Mark read
            </button>
          )}
        </div>
      </div>
      
      {alert.explanation && (
        <div className="mt-2">
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="text-xs text-current opacity-75 hover:opacity-100 underline"
          >
            {showExplanation ? 'Hide' : 'Why am I seeing this?'}
          </button>
          {showExplanation && (
            <p className="text-xs mt-2 opacity-90 italic">
              {alert.explanation}
            </p>
          )}
        </div>
      )}
      
      {alert.value != null && (
        <div className="text-xs mt-2 opacity-90">
          Value: ₹{typeof alert.value === 'number' ? alert.value.toFixed(2) : alert.value}
          {alert.threshold != null && ` (Threshold: ₹${typeof alert.threshold === 'number' ? alert.threshold.toFixed(2) : alert.threshold})`}
        </div>
      )}
    </div>
  )
}

