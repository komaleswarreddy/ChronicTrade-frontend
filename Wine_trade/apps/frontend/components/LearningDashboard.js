'use client'

import { useState, useEffect } from 'react'
import api from '../lib/api'
import { useAuth } from '../contexts/AuthContext'
import LearningInsightsPanel from './LearningInsightsPanel'
import MLModelsPanel from './MLModelsPanel'

export default function LearningDashboard() {
  const { isAuthenticated } = useAuth()
  const [activeTab, setActiveTab] = useState('insights')

  if (!isAuthenticated()) {
    return null
  }

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">Learning Dashboard</h3>
        <p className="text-xs text-blue-800">
          <strong>Observational only</strong> — These metrics do not modify AI behavior. 
          They provide insights into model performance, calibration, and strategy effectiveness.
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('insights')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'insights'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Learning Insights
          </button>
          <button
            onClick={() => setActiveTab('models')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'models'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            ML Models
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'insights' && <LearningInsightsPanel />}
        {activeTab === 'models' && <MLModelsPanel />}
      </div>
    </div>
  )
}
