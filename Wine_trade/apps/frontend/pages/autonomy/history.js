'use client'

import DashboardLayout from '../../components/DashboardLayout'
import ExecutionHistoryTable from '../../components/ExecutionHistoryTable'

export default function AutonomyHistory() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Execution History</h1>
        <p className="text-gray-600">View history of autonomous executions</p>
      </div>
      <ExecutionHistoryTable />
    </DashboardLayout>
  )
}
