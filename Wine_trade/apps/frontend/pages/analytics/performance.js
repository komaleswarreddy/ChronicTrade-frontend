'use client'

import DashboardLayout from '../../components/DashboardLayout'
import PerformanceMetricsPanel from '../../components/PerformanceMetricsPanel'

export default function AnalyticsPerformance() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Performance Metrics</h1>
        <p className="text-gray-600">Track your trading performance and ROI</p>
      </div>
      <PerformanceMetricsPanel />
    </DashboardLayout>
  )
}
