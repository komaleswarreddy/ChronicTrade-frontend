'use client'

import DashboardLayout from '../../components/DashboardLayout'
import MLModelsPanel from '../../components/MLModelsPanel'

export default function LearningModels() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">ML Models</h1>
        <p className="text-gray-600">View trained machine learning models and predictions</p>
      </div>
      <MLModelsPanel />
    </DashboardLayout>
  )
}
