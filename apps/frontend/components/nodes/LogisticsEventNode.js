'use client'

import { memo } from 'react'
import { Handle, Position } from 'reactflow'
import { motion } from 'framer-motion'
import { Truck, Warehouse, Package, AlertTriangle } from 'lucide-react'

const riskColors = {
  LOW: 'bg-green-100 text-green-700 border-green-400',
  MEDIUM: 'bg-yellow-100 text-yellow-700 border-yellow-400',
  HIGH: 'bg-red-100 text-red-700 border-red-400',
}

function LogisticsEventNode({ data, selected }) {
  const riskLevel = data.riskLevel || 'LOW'
  const eventType = data.eventType || 'SHIPMENT'
  const Icon = eventType === 'SHIPMENT' ? Truck : eventType === 'STORAGE' ? Warehouse : Package
  
  return (
    <motion.div
      className={`px-4 py-3 rounded-lg border-2 ${riskColors[riskLevel]} ${
        selected ? 'ring-2 ring-blue-500 ring-offset-2' : ''
      } min-w-[180px] relative`}
      initial={{ scale: 0.9, opacity: 0, x: -20 }}
      animate={{ scale: 1, opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      
      <div className="flex items-center gap-2">
        <motion.div
          animate={{ x: [0, 5, 0] }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <Icon className="w-5 h-5" />
        </motion.div>
        <div className="flex-1">
          <div className="font-semibold text-sm">{data.eventType || 'Logistics Event'}</div>
          <div className="text-xs text-gray-600 mt-0.5">{data.status || 'In Transit'}</div>
        </div>
      </div>
      
      {riskLevel !== 'LOW' && (
        <div className="mt-2 pt-2 border-t border-gray-300 flex items-center gap-1">
          <AlertTriangle className="w-3 h-3 text-red-600" />
          <span className="text-xs font-semibold text-red-600">{riskLevel} Risk</span>
        </div>
      )}
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </motion.div>
  )
}

export default memo(LogisticsEventNode)
