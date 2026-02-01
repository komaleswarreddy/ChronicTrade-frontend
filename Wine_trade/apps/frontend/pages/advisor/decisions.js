'use client'

import DashboardLayout from '../../components/DashboardLayout'
import DecisionReplayPanel from '../../components/DecisionReplayPanel'

export default function AdvisorDecisions() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Decision Replay</h1>
        <p className="text-gray-600">View detailed decision lineage and policy evaluations</p>
      </div>
      <DecisionReplayPanel />
    </DashboardLayout>
  )
}
