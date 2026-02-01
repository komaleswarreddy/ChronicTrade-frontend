'use client'

import DashboardLayout from '../../components/DashboardLayout'
import StrategyPerformancePanel from '../../components/StrategyPerformancePanel'

export default function AnalyticsStrategy() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Strategy Performance</h1>
        <p className="text-gray-600">Analyze the effectiveness of your trading strategies</p>
      </div>
      <StrategyPerformancePanel />
    </DashboardLayout>
  )
}
