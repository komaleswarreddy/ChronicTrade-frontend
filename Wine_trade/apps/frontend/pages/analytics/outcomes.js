'use client'

import DashboardLayout from '../../components/DashboardLayout'
import OutcomeHistoryTable from '../../components/OutcomeHistoryTable'

export default function AnalyticsOutcomes() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Outcome History</h1>
        <p className="text-gray-600">Review realized outcomes and performance deltas</p>
      </div>
      <OutcomeHistoryTable />
    </DashboardLayout>
  )
}
