'use client'

import DashboardLayout from '../../components/DashboardLayout'
import DecisionReplayPanel from '../../components/DecisionReplayPanel'

export default function TrustReplay() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Decision Replay</h1>
        <p className="text-gray-600">View detailed decision lineage and policy evaluations for any simulation</p>
      </div>
      <DecisionReplayPanel />
    </DashboardLayout>
  )
}
