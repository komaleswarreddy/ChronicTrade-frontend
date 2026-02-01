'use client'

import DashboardLayout from '../../components/DashboardLayout'
import AutonomousExecutionPanel from '../../components/AutonomousExecutionPanel'

export default function AutonomyExecution() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Autonomous Execution</h1>
        <p className="text-gray-600">Manage and monitor autonomous trade executions</p>
      </div>
      <AutonomousExecutionPanel />
    </DashboardLayout>
  )
}
