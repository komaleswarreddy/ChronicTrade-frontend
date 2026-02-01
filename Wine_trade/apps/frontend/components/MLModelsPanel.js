'use client'

import { useState, useEffect, useRef } from 'react'
import api from '../lib/api'
import { useAuth } from '../contexts/AuthContext'

export default function MLModelsPanel() {
  const { isAuthenticated } = useAuth()
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filterType, setFilterType] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [selectedModel, setSelectedModel] = useState(null)
  const [predictions, setPredictions] = useState([])
  const [loadingPredictions, setLoadingPredictions] = useState(false)
  const dropdownRef = useRef(null)

  const filterOptions = [
    { value: '', label: 'All Types' },
    { value: 'price_prediction', label: 'Price Prediction' },
    { value: 'risk_scoring', label: 'Risk Scoring' }
  ]

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  // Fetch models when filter changes or component mounts
  useEffect(() => {
    if (isAuthenticated()) {
      fetchModels()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterType])

  const fetchModels = async () => {
    if (!isAuthenticated()) {
      console.warn('[ML Models] Not authenticated, skipping fetch')
      return
    }

    console.log('[ML Models] ============================================================')
    console.log('[ML Models] Starting fetch models')
    console.log('[ML Models] Filter Type:', filterType || 'All Types')

    setLoading(true)
    setError(null)

    const startTime = Date.now()
    try {
      const url = filterType ? `/api/ml/models?model_type=${filterType}` : '/api/ml/models'
      console.log('[ML Models] Request URL:', url)
      console.log('[ML Models] Sending GET request...')

      const response = await api.get(url)
      const requestTime = Date.now() - startTime

      console.log('[ML Models] Response received in', requestTime, 'ms')
      console.log('[ML Models] Response status:', response.status)
      console.log('[ML Models] Full response data:', JSON.stringify(response.data, null, 2))

      if (response.data) {
        const modelsArray = Array.isArray(response.data) ? response.data : []
        console.log('[ML Models] Models count:', modelsArray.length)
        
        if (modelsArray.length > 0) {
          console.log('[ML Models] Models:')
          modelsArray.forEach((model, i) => {
            console.log(`  Model ${i + 1}:`)
            console.log(`    - ID: ${model.model_id}`)
            console.log(`    - Type: ${model.model_type}`)
            console.log(`    - Name: ${model.model_name}`)
            console.log(`    - Version: ${model.version}`)
            console.log(`    - Active: ${model.is_active}`)
          })
        } else {
          console.warn('[ML Models] WARNING: No models in response!')
        }

        setModels(modelsArray)
      } else {
        console.error('[ML Models] ERROR: Response data is null or undefined!')
        setModels([])
      }

      console.log('[ML Models] ============================================================')
    } catch (err) {
      const errorTime = Date.now() - startTime
      console.error('[ML Models] ============================================================')
      console.error('[ML Models] Fetch FAILED after', errorTime, 'ms')
      console.error('[ML Models] Error object:', err)
      console.error('[ML Models] Error type:', err.constructor.name)
      console.error('[ML Models] Error message:', err.message)
      
      if (err.response) {
        console.error('[ML Models] Response error details:')
        console.error('  - Status:', err.response.status)
        console.error('  - Status Text:', err.response.statusText)
        console.error('  - Data:', JSON.stringify(err.response.data, null, 2))
      } else if (err.request) {
        console.error('[ML Models] Request error (no response):')
        console.error('  - This usually means the server is not reachable')
      }
      
      console.error('[ML Models] Full error stack:', err.stack)
      console.error('[ML Models] ============================================================')

      let errorMessage = 'Failed to fetch ML models'
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.response?.status) {
        errorMessage = `Server error (${err.response.status}): ${err.response.statusText || err.message}`
      } else if (err.request) {
        errorMessage = 'Cannot connect to server. Please check if the backend is running.'
      } else {
        errorMessage = err.message || 'Unknown error occurred'
      }

      setError(errorMessage)
      setModels([])
    } finally {
      setLoading(false)
      console.log('[ML Models] Loading state set to false')
    }
  }

  const handleFilterChange = (value) => {
    console.log('[ML Models] Filter changed to:', value || 'All Types')
    setFilterType(value)
    setDropdownOpen(false)
  }

  const handleModelClick = async (model) => {
    console.log('[ML Models] Opening model details for:', model.model_id)
    setSelectedModel(model)
    setPredictions([])
    setLoadingPredictions(true)
    
    try {
      const response = await api.get(`/api/ml/models/${model.model_id}/predictions`)
      console.log('[ML Models] Predictions response:', response.data)
      setPredictions(response.data.predictions || [])
    } catch (err) {
      console.error('[ML Models] Failed to fetch predictions:', err)
      // Don't show error - just show empty predictions
      setPredictions([])
    } finally {
      setLoadingPredictions(false)
    }
  }

  const closeModal = () => {
    setSelectedModel(null)
    setPredictions([])
  }

  const getModelTypeColor = (type) => {
    switch (type) {
      case 'price_prediction':
        return {
          bg: 'bg-gradient-to-br from-blue-50 to-blue-100',
          border: 'border-blue-200',
          text: 'text-blue-700',
          badge: 'bg-blue-500 text-white',
          icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
        }
      case 'risk_scoring':
        return {
          bg: 'bg-gradient-to-br from-red-50 to-red-100',
          border: 'border-red-200',
          text: 'text-red-700',
          badge: 'bg-red-500 text-white',
          icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
        }
      default:
        return {
          bg: 'bg-gradient-to-br from-gray-50 to-gray-100',
          border: 'border-gray-200',
          text: 'text-gray-700',
          badge: 'bg-gray-500 text-white',
          icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
        }
    }
  }

  const getModelTypeLabel = (type) => {
    switch (type) {
      case 'price_prediction':
        return 'Price Prediction'
      case 'risk_scoring':
        return 'Risk Scoring'
      default:
        return type
    }
  }

  const selectedOption = filterOptions.find(opt => opt.value === filterType) || filterOptions[0]

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">ML Models</h3>
            <p className="text-xs text-gray-500 mt-0.5">View trained machine learning models</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Modern Custom Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 min-w-[180px] justify-between"
            >
              <span className="text-sm font-medium text-gray-700">{selectedOption.label}</span>
              <svg 
                className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-xl border border-gray-200 z-50 overflow-hidden">
                {filterOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleFilterChange(option.value)}
                    className={`w-full text-left px-4 py-3 text-sm transition-colors ${
                      filterType === option.value
                        ? 'bg-blue-50 text-blue-700 font-semibold'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{option.label}</span>
                      {filterType === option.value && (
                        <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={fetchModels}
            disabled={loading}
            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white text-sm font-medium rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
          >
            <svg 
              className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="p-8 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
          <div className="flex items-center justify-center space-x-4">
            <div className="relative">
              <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Loading models...</p>
              <p className="text-xs text-gray-500 mt-1">Fetching ML models from database</p>
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="p-6 bg-red-50 border border-red-300 rounded-xl">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">Failed to Load Models</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
                <button
                  onClick={fetchModels}
                  className="mt-3 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && models.length === 0 && (
        <div className="p-8 bg-gradient-to-br from-yellow-50 to-amber-50 rounded-xl border border-yellow-200">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <svg className="w-16 h-16 text-yellow-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">No ML Models Found</h3>
              <p className="text-sm text-yellow-700 mb-1">
                {filterType 
                  ? `No ${getModelTypeLabel(filterType)} models found.`
                  : 'No models have been trained yet.'
                }
              </p>
              <p className="text-xs text-yellow-600 mt-2">
                Models will appear here after training.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Models List */}
      {!loading && !error && models.length > 0 && (
        <div className="space-y-4">
          <div className="mb-4 p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm font-semibold text-green-800">
                  Found {models.length} {models.length === 1 ? 'model' : 'models'}
                </span>
              </div>
            </div>
          </div>

          {models.map((model) => {
            const colors = getModelTypeColor(model.model_type)
            return (
              <div
                key={model.model_id}
                onClick={() => handleModelClick(model)}
                className={`${colors.bg} ${colors.border} border-2 rounded-xl p-5 shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.01] cursor-pointer`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3 flex-1">
                    <div className={`${colors.badge} p-2 rounded-lg`}>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={colors.icon} />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-bold text-gray-900">{model.model_name || 'Unnamed Model'}</h4>
                        {model.is_active && (
                          <span className="px-2 py-0.5 bg-green-500 text-white text-xs font-semibold rounded-full">
                            Active
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">
                        {getModelTypeLabel(model.model_type)} • Version {model.version}
                      </p>
                    </div>
                  </div>
                </div>

                {model.training_metrics && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="text-xs font-semibold text-gray-700 mb-3">Training Metrics</div>
                    <div className="grid grid-cols-2 gap-3">
                      {model.training_metrics.val_r2 !== undefined && (
                        <div className="bg-white/60 backdrop-blur-sm p-2 rounded-lg">
                          <div className="text-xs text-gray-500">Validation R²</div>
                          <div className="text-sm font-bold text-gray-900">
                            {(model.training_metrics.val_r2 * 100).toFixed(1)}%
                          </div>
                        </div>
                      )}
                      {model.training_metrics.val_mae !== undefined && (
                        <div className="bg-white/60 backdrop-blur-sm p-2 rounded-lg">
                          <div className="text-xs text-gray-500">Validation MAE</div>
                          <div className="text-sm font-bold text-gray-900">
                            {model.training_metrics.val_mae.toFixed(3)}
                          </div>
                        </div>
                      )}
                      {model.training_metrics.train_size && (
                        <div className="bg-white/60 backdrop-blur-sm p-2 rounded-lg">
                          <div className="text-xs text-gray-500">Train Size</div>
                          <div className="text-sm font-bold text-gray-900">
                            {model.training_metrics.train_size.toLocaleString()}
                          </div>
                        </div>
                      )}
                      {model.training_metrics.val_size && (
                        <div className="bg-white/60 backdrop-blur-sm p-2 rounded-lg">
                          <div className="text-xs text-gray-500">Val Size</div>
                          <div className="text-sm font-bold text-gray-900">
                            {model.training_metrics.val_size.toLocaleString()}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="mt-4 pt-3 border-t border-gray-200">
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Model ID: {model.model_id}</span>
                    <span>Created: {new Date(model.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Model Details Modal */}
      {selectedModel && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={closeModal}
        >
          <div 
            className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">{selectedModel.model_name}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {getModelTypeLabel(selectedModel.model_type)} • Version {selectedModel.version}
                  </p>
                </div>
                <button
                  onClick={closeModal}
                  className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {/* Model Info */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">Model Information</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Model ID:</span>
                    <span className="ml-2 font-mono text-gray-900 text-xs">{selectedModel.model_id}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Status:</span>
                    <span className={`ml-2 px-2 py-1 rounded-full text-xs font-semibold ${selectedModel.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {selectedModel.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Created:</span>
                    <span className="ml-2 text-gray-900">{new Date(selectedModel.created_at).toLocaleString()}</span>
                  </div>
                  {selectedModel.training_metrics && (
                    <div>
                      <span className="text-gray-500">Validation R²:</span>
                      <span className="ml-2 font-semibold text-gray-900">
                        {(selectedModel.training_metrics.val_r2 * 100).toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Predictions Section */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-4">Recent Predictions</h4>
                
                {loadingPredictions ? (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-200 border-t-blue-600"></div>
                    <p className="mt-2 text-sm text-gray-500">Loading predictions...</p>
                  </div>
                ) : predictions.length === 0 ? (
                  <div className="text-center py-8 bg-yellow-50 rounded-lg border border-yellow-200">
                    <svg className="w-12 h-12 text-yellow-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm text-gray-600">No predictions found for this model yet.</p>
                    <p className="text-xs text-gray-500 mt-1">Predictions will appear here after the model is used.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {predictions.map((pred, idx) => (
                      <div key={idx} className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-500 rounded-lg">
                              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                              </svg>
                            </div>
                            <div>
                              <div className="font-bold text-gray-900">
                                {selectedModel.model_type === 'price_prediction' 
                                  ? `₹${pred.prediction_value?.toFixed(2) || 'N/A'}`
                                  : `${(pred.prediction_value * 100)?.toFixed(1) || 'N/A'}%`
                                }
                              </div>
                              <div className="text-xs text-gray-500">
                                {new Date(pred.created_at).toLocaleString()}
                              </div>
                            </div>
                          </div>
                          {pred.confidence_score !== null && pred.confidence_score !== undefined && (
                            <div className="text-right">
                              <div className="text-xs text-gray-500">Confidence</div>
                              <div className="text-sm font-semibold text-blue-600">
                                {(pred.confidence_score * 100).toFixed(1)}%
                              </div>
                            </div>
                          )}
                        </div>
                        {pred.input_features && Object.keys(pred.input_features).length > 0 ? (
                          <div className="mt-3 pt-3 border-t border-blue-200">
                            <div className="text-xs text-gray-500 mb-1 font-semibold">Input Features:</div>
                            <div className="text-xs font-mono bg-white p-2 rounded border border-blue-100 max-h-32 overflow-y-auto">
                              <pre className="whitespace-pre-wrap break-words text-gray-900">
                                {JSON.stringify(pred.input_features, null, 2)}
                              </pre>
                            </div>
                          </div>
                        ) : (
                          <div className="mt-3 pt-3 border-t border-blue-200">
                            <div className="text-xs text-gray-400 italic">Input features not available</div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
