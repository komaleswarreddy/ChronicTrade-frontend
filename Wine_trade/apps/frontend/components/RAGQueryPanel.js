'use client'

import { useState } from 'react'
import api from '../lib/api'
import { useAuth } from '../contexts/AuthContext'
import CitationDisplay from './CitationDisplay'

export default function RAGQueryPanel() {
  const { isAuthenticated } = useAuth()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sourceTypes, setSourceTypes] = useState([])
  const [topK, setTopK] = useState(5)
  const [topKInput, setTopKInput] = useState('5')

  const handleQuery = async () => {
    if (!query.trim() || !isAuthenticated()) {
      console.warn('[RAG Frontend] Query blocked:', {
        hasQuery: !!query.trim(),
        isAuthenticated: isAuthenticated()
      })
      return
    }

    console.log('[RAG Frontend] ============================================================')
    console.log('[RAG Frontend] Starting RAG query')
    console.log('[RAG Frontend] Query:', query.trim())
    console.log('[RAG Frontend] Source Types:', sourceTypes.length > 0 ? sourceTypes : null)
    console.log('[RAG Frontend] Top K:', topK)
    console.log('[RAG Frontend] Min Confidence: 0.5')

    setLoading(true)
    setError(null)
    setResults(null)

    const requestPayload = {
      query: query.trim(),
      source_types: sourceTypes.length > 0 ? sourceTypes : null,
      top_k: topK,
      min_confidence: 0.5
    }

    console.log('[RAG Frontend] Request payload:', JSON.stringify(requestPayload, null, 2))
    console.log('[RAG Frontend] Sending POST to /api/rag/query...')

    const startTime = Date.now()
    try {
      const response = await api.post('/api/rag/query', requestPayload)
      const requestTime = Date.now() - startTime

      console.log('[RAG Frontend] Response received in', requestTime, 'ms')
      console.log('[RAG Frontend] Response status:', response.status)
      console.log('[RAG Frontend] Response headers:', response.headers)
      console.log('[RAG Frontend] Full response data:', JSON.stringify(response.data, null, 2))

      if (response.data) {
        console.log('[RAG Frontend] Response structure:')
        console.log('  - Query:', response.data.query)
        console.log('  - Total Results:', response.data.total_results)
        console.log('  - Query Time (ms):', response.data.query_time_ms)
        console.log('  - Citations Count:', response.data.citations?.length || 0)

        if (response.data.citations && response.data.citations.length > 0) {
          console.log('[RAG Frontend] Citations:')
          response.data.citations.forEach((citation, i) => {
            console.log(`  Citation ${i + 1}:`)
            console.log(`    - Title: ${citation.title}`)
            console.log(`    - Source: ${citation.source_type}`)
            console.log(`    - Confidence: ${citation.confidence}`)
            console.log(`    - Content length: ${citation.content?.length || 0}`)
          })
        } else {
          console.warn('[RAG Frontend] WARNING: No citations in response!')
          console.warn('[RAG Frontend] This could indicate:')
          console.warn('  1. No matching documents found')
          console.warn('  2. All results below confidence threshold')
          console.warn('  3. Database connection issue')
          console.warn('  4. Embedding generation issue')
        }
      } else {
        console.error('[RAG Frontend] ERROR: Response data is null or undefined!')
      }

      setResults(response.data)
      console.log('[RAG Frontend] Results set in state')
      console.log('[RAG Frontend] ============================================================')
    } catch (err) {
      const errorTime = Date.now() - startTime
      console.error('[RAG Frontend] ============================================================')
      console.error('[RAG Frontend] RAG query FAILED after', errorTime, 'ms')
      console.error('[RAG Frontend] Error object:', err)
      console.error('[RAG Frontend] Error type:', err.constructor.name)
      console.error('[RAG Frontend] Error message:', err.message)
      
      if (err.response) {
        console.error('[RAG Frontend] Response error details:')
        console.error('  - Status:', err.response.status)
        console.error('  - Status Text:', err.response.statusText)
        console.error('  - Headers:', err.response.headers)
        console.error('  - Data:', JSON.stringify(err.response.data, null, 2))
        
        if (err.response.data) {
          console.error('  - Error Detail:', err.response.data.detail)
          console.error('  - Error Type:', err.response.data.type)
        }
      } else if (err.request) {
        console.error('[RAG Frontend] Request error (no response):')
        console.error('  - Request:', err.request)
        console.error('  - This usually means the server is not reachable')
      } else {
        console.error('[RAG Frontend] Error setting up request:')
        console.error('  - Error:', err.message)
      }
      
      console.error('[RAG Frontend] Full error stack:', err.stack)
      console.error('[RAG Frontend] ============================================================')

      // Set user-friendly error message
      let errorMessage = 'Failed to query RAG system'
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
    } finally {
      setLoading(false)
      console.log('[RAG Frontend] Loading state set to false')
    }
  }

  const toggleSourceType = (type) => {
    setSourceTypes(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">Knowledge Base Search</h3>
            <p className="text-xs text-gray-500 mt-0.5">Query compliance rules, policies, and strategies</p>
          </div>
        </div>
      </div>

      <div className="mb-5">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          What would you like to know?
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., What are the compliance rules for BUY recommendations?"
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white transition-all duration-200 resize-none"
          rows={3}
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-5">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Filter by Source (optional)
          </label>
          <div className="space-y-2 bg-gray-50 p-3 rounded-lg border border-gray-200">
            {['compliance_rule', 'risk_policy', 'strategy_doc', 'execution_constraint'].map(type => (
              <label key={type} className="flex items-center cursor-pointer hover:bg-white px-2 py-1.5 rounded transition-colors">
                <input
                  type="checkbox"
                  checked={sourceTypes.includes(type)}
                  onChange={() => toggleSourceType(type)}
                  className="mr-2 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 capitalize">{type.replace(/_/g, ' ')}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Max Results
          </label>
          <input
            type="number"
            value={topKInput}
            onChange={(e) => {
              const value = e.target.value
              setTopKInput(value)
              // Update the actual topK value if valid
              const numValue = parseInt(value, 10)
              if (!isNaN(numValue) && numValue >= 1 && numValue <= 20) {
                setTopK(numValue)
              }
            }}
            onBlur={(e) => {
              // Validate and clamp on blur
              const value = parseInt(e.target.value, 10)
              if (isNaN(value) || value < 1) {
                setTopK(5)
                setTopKInput('5')
              } else if (value > 20) {
                setTopK(20)
                setTopKInput('20')
              } else {
                setTopK(value)
                setTopKInput(value.toString())
              }
            }}
            onFocus={(e) => {
              // Show current value when focused
              setTopKInput(topK.toString())
            }}
            min={1}
            max={20}
            step={1}
            className="w-full px-4 py-2.5 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white transition-all duration-200"
          />
        </div>
      </div>

      <button
        onClick={handleQuery}
        disabled={loading || !query.trim()}
        className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-medium rounded-lg shadow-md hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Searching Knowledge Base...</span>
          </>
        ) : (
          <>
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>Search Knowledge Base</span>
          </>
        )}
      </button>

      {loading && (
        <div className="mt-6 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
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
              <p className="text-sm font-medium text-gray-900">Analyzing your query...</p>
              <p className="text-xs text-gray-500 mt-1">Searching through knowledge base documents</p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-300 rounded-md">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">Query Failed</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
                <p className="mt-2 text-xs text-red-600">
                  Check the browser console for detailed error logs.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {results && (
        <div className="mt-4">
          {(!results.total_results || results.total_results === 0) ? (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 flex-1">
                  <h3 className="text-sm font-medium text-yellow-800">No Results Found</h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <p>Found 0 results{results.query_time_ms ? ` in ${results.query_time_ms.toFixed(2)}ms` : ''}</p>
                    <p className="mt-2 text-xs text-yellow-600">
                      This could mean:
                    </p>
                    <ul className="mt-1 text-xs text-yellow-600 list-disc list-inside">
                      <li>No documents match your query</li>
                      <li>All results are below the confidence threshold (0.5)</li>
                      <li>Check backend logs for detailed error information</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="mb-4 p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-semibold text-green-800">
                      Found {results.total_results || 0} {(results.total_results || 0) === 1 ? 'result' : 'results'}
                    </span>
                  </div>
                  {results.query_time_ms && (
                    <span className="text-xs text-green-600 font-medium">
                      {results.query_time_ms.toFixed(0)}ms
                    </span>
                  )}
                </div>
              </div>
              <CitationDisplay citations={results.citations || []} />
            </>
          )}
        </div>
      )}
    </div>
  )
}
