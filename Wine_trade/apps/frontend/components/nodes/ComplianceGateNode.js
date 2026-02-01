'use client'

import { memo } from 'react'
import { Handle, Position } from 'reactflow'
import { motion } from 'framer-motion'
import { Shield, ShieldCheck, ShieldX, ShieldAlert } from 'lucide-react'

const statusConfig = {
  PASS: {
    color: 'bg-green-100 text-green-700 border-green-400',
    icon: ShieldCheck,
    glow: 'shadow-green-400/50 shadow-lg',
  },
  FAIL: {
    color: 'bg-red-100 text-red-700 border-red-400',
    icon: ShieldX,
    glow: 'shadow-red-400/50 shadow-lg',
  },
  CONDITIONAL: {
    color: 'bg-yellow-100 text-yellow-700 border-yellow-400',
    icon: ShieldAlert,
    glow: 'shadow-yellow-400/50 shadow-lg',
  },
}

function ComplianceGateNode({ data, selected }) {
  const status = data.overallResult || 'CONDITIONAL'
  const config = statusConfig[status] || statusConfig.CONDITIONAL
  const Icon = config.icon
  
  return (
    <motion.div
      className={`px-4 py-3 rounded-lg border-2 ${config.color} ${config.glow} ${
        selected ? 'ring-2 ring-blue-500 ring-offset-2' : ''
      } min-w-[180px] relative`}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.2 }}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      
      <div className="flex items-center gap-2">
        <Icon className="w-5 h-5" />
        <div className="flex-1">
          <div className="font-semibold text-sm">Compliance Gate</div>
          <div className="text-xs text-gray-600 mt-0.5">{status}</div>
        </div>
      </div>
      
      {data.failedRules && data.failedRules.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-300">
          <div className="text-xs text-red-600">
            {data.failedRules.length} rule{data.failedRules.length > 1 ? 's' : ''} failed
          </div>
        </div>
      )}
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </motion.div>
  )
}

export default memo(ComplianceGateNode)
