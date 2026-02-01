'use client'

import DashboardLayout from '../../components/DashboardLayout'
import SoldHoldingsTable from '../../components/SoldHoldingsTable'

export default function PortfolioSold() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Sold Holdings</h1>
        <p className="text-gray-600">View your realized profits and sales history</p>
      </div>
      <SoldHoldingsTable onRefresh={() => {}} />
    </DashboardLayout>
  )
}
