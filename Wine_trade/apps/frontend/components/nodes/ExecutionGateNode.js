'use client'

import { memo } from 'react'
import { Handle, Position } from 'reactflow'
import { motion } from 'framer-motion'
import { Lock, Unlock, AlertCircle } from 'lucide-react'

function ExecutionGateNode({ data, selected }) {
  const isPassed = data.status === 'PASSED'
  const isBlocked = data.status === 'BLOCKED'
  const Icon = isPassed ? Unlock : Lock
  
  const colorClass = isPassed 
    ? 'bg-green-100 text-green-700 border-green-400 shadow-green-400/50 shadow-lg'
    : isBlocked
    ? 'bg-red-100 text-red-700 border-red-400 shadow-red-400/50 shadow-lg'
    : 'bg-gray-100 text-gray-700 border-gray-400'
  
  return (
    <motion.div
      className={`px-4 py-3 rounded-lg border-2 ${colorClass} ${
        selected ? 'ring-2 ring-blue-500 ring-offset-2' : ''
      } min-w-[180px] relative`}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ 
        scale: 1, 
        opacity: 1,
        ...(isPassed && {
          scale: [1, 1.05, 1],
        }),
      }}
      transition={{
        duration: 0.2,
        ...(isPassed && {
          scale: {
            duration: 0.3,
          },
        }),
      }}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      
      <div className="flex items-center gap-2">
        <Icon className={`w-5 h-5 ${isPassed ? 'animate-pulse' : ''}`} />
        <div className="flex-1">
          <div className="font-semibold text-sm">{data.gateType || 'Execution Gate'}</div>
          <div className="text-xs text-gray-600 mt-0.5">
            {isPassed ? 'Unlocked' : isBlocked ? 'Blocked' : 'Pending'}
          </div>
        </div>
      </div>
      
      {isBlocked && data.blockReason && (
        <div className="mt-2 pt-2 border-t border-gray-300">
          <div className="flex items-start gap-1">
            <AlertCircle className="w-3 h-3 text-red-600 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-red-600 line-clamp-2">{data.blockReason}</div>
          </div>
        </div>
      )}
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </motion.div>
  )
}

export default memo(ExecutionGateNode)
