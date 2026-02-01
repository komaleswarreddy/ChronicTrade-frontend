'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import DashboardLayout from '../../components/DashboardLayout'
import api from '../../lib/api'
import AdvisorCard from '../../components/AdvisorCard'

export default function AdvisorRecommendations() {
  const [agentProposals, setAgentProposals] = useState([])
  const [loading, setLoading] = useState(true)
  const [runningAgent, setRunningAgent] = useState(false)
  const [agentError, setAgentError] = useState(null)
  const [agentProgress, setAgentProgress] = useState('')
  const { user, loading: authLoading, isAuthenticated } = useAuth()

  const fetchProposals = async () => {
    if (authLoading || !user || !isAuthenticated()) {
      setLoading(false)
      return
    }
    
    try {
      setLoading(true)
      const proposalsRes = await api.get('/api/agent/proposals?limit=20')
      setAgentProposals(proposalsRes.data || [])
    } catch (err) {
      console.error('Failed to fetch proposals:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!authLoading && user && isAuthenticated()) {
      fetchProposals()
    }
  }, [authLoading, user, isAuthenticated])

  const handleRunAgent = async () => {
    if (!isAuthenticated() || runningAgent) return
    
    setRunningAgent(true)
    setAgentError(null)
    setAgentProgress('Starting analysis...')
    
    try {
      const progressInterval = setInterval(() => {
        setAgentProgress(prev => {
          if (prev === 'Starting analysis...') return 'Fetching portfolio data...'
          if (prev === 'Fetching portfolio data...') return 'Analyzing market trends...'
          if (prev === 'Analyzing market trends...') return 'Evaluating opportunities...'
          if (prev === 'Evaluating opportunities...') return 'Generating recommendations...'
          return 'Finalizing analysis...'
        })
      }, 5000)
      
      const runRes = await api.post(
        '/api/agent/run',
        { asset_id: null },
        { timeout: 90000 }
      )
      
      clearInterval(progressInterval)
      setAgentProgress('')
      
      if (runRes.data.success) {
        setAgentProgress('Saving results...')
        if (runRes.data.results?.recommendation) {
          const rec = runRes.data.results.recommendation
          if (rec && rec.asset_id) {
            const tempProposal = {
              proposal_id: runRes.data.run_id || `temp_${Date.now()}`,
              asset_id: rec.asset_id,
              asset_name: rec.asset_id.replace('asset_', 'Asset '),
              recommendation: rec.action || 'HOLD',
              confidence_score: runRes.data.results.confidence_score || 0.5,
              expected_roi: rec.expected_roi,
              rationale: rec.rationale || runRes.data.results.explanation || '',
              compliance_status: runRes.data.results.compliance_status || 'PENDING'
            }
            setAgentProposals([tempProposal])
          }
        }
        await new Promise(resolve => setTimeout(resolve, 2000))
        await fetchProposals()
        setAgentProgress('')
      } else {
        setAgentError(runRes.data.error || 'Agent analysis failed')
        setAgentProgress('')
      }
    } catch (err) {
      console.error('Failed to run agent:', err)
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        setAgentError('Agent analysis timed out. Please try again.')
      } else {
        setAgentError(err.response?.data?.error || err.message || 'Failed to run agent analysis.')
      }
      setAgentProgress('')
    } finally {
      setRunningAgent(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Advisor Recommendations</h1>
            <p className="text-gray-600">Get personalized trading recommendations</p>
          </div>
          <button
            onClick={handleRunAgent}
            disabled={runningAgent}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium flex items-center gap-2"
          >
            {runningAgent ? (
              <>
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {agentProgress || 'Analyzing...'}
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Run AI Analysis
              </>
            )}
          </button>
        </div>
      </div>
      
      {agentError && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-800 p-3 rounded-lg text-sm">
          <strong>Error:</strong> {agentError}
        </div>
      )}
      
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading recommendations...</p>
        </div>
      ) : agentProposals.length > 0 ? (
        <div className="space-y-4">
          {agentProposals.map((proposal) => (
            <AdvisorCard
              key={proposal.proposal_id}
              proposal={proposal}
              onAction={async () => {
                await fetchProposals()
              }}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          <p className="mb-2">No AI recommendations yet</p>
          <p className="text-sm">Click "Run AI Analysis" to get personalized trading recommendations</p>
        </div>
      )}
    </DashboardLayout>
  )
}
