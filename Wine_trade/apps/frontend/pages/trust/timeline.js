'use client'

import DashboardLayout from '../../components/DashboardLayout'
import DecisionTimeline from '../../components/DecisionTimeline'

export default function TrustTimeline() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Decision Timeline</h1>
        <p className="text-gray-600">Track the lifecycle of decisions from creation to execution</p>
      </div>
      <DecisionTimeline />
    </DashboardLayout>
  )
}
