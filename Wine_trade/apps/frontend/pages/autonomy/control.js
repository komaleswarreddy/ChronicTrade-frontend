'use client'

import DashboardLayout from '../../components/DashboardLayout'
import AutonomyControlPanel from '../../components/AutonomyControlPanel'

export default function AutonomyControl() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Autonomy Control</h1>
        <p className="text-gray-600">Enable or disable autonomous trading</p>
      </div>
      <AutonomyControlPanel />
    </DashboardLayout>
  )
}
