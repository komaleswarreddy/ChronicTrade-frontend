'use client'

import DashboardLayout from '../../components/DashboardLayout'
import LearningInsightsPanel from '../../components/LearningInsightsPanel'

export default function LearningInsights() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Learning Insights</h1>
        <p className="text-gray-600">Observational metrics and model performance insights</p>
      </div>
      <LearningInsightsPanel />
    </DashboardLayout>
  )
}
