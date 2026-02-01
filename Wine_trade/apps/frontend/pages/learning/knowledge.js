'use client'

import DashboardLayout from '../../components/DashboardLayout'
import RAGQueryPanel from '../../components/RAGQueryPanel'

export default function LearningKnowledge() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Knowledge Base</h1>
        <p className="text-gray-600">Search compliance rules, policies, and strategies</p>
      </div>
      <RAGQueryPanel />
    </DashboardLayout>
  )
}
