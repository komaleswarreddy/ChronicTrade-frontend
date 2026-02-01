'use client'

import DashboardLayout from '../../components/DashboardLayout'
import SimulationHistoryTable from '../../components/SimulationHistoryTable'

export default function AdvisorSimulations() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Simulation History</h1>
        <p className="text-gray-600">View and manage your trading simulations</p>
      </div>
      <SimulationHistoryTable onSimulationUpdate={() => {}} />
    </DashboardLayout>
  )
}
