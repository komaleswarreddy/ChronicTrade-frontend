'use client'

import DashboardLayout from '../../components/DashboardLayout'
import CapitalSummaryPanel from '../../components/CapitalSummaryPanel'

export default function PortfolioCapital() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Capital Summary</h1>
        <p className="text-gray-600">Manage your trading capital and exposure</p>
      </div>
      <CapitalSummaryPanel />
    </DashboardLayout>
  )
}
