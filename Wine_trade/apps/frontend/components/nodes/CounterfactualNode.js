'use client'

import { memo } from 'react'
import { Handle, Position } from 'reactflow'
import { motion } from 'framer-motion'
import { GitBranch } from 'lucide-react'

function CounterfactualNode({ data, selected }) {
  const isPositive = (data.roiDelta || 0) > 0
  
  // Check for reduced motion preference
  const prefersReducedMotion = typeof window !== 'undefined' && 
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  
  return (
    <motion.div
      className={`px-4 py-3 rounded-lg border-2 border-dashed ${
        isPositive 
          ? 'bg-green-50/50 text-green-700 border-green-300/50' 
          : 'bg-gray-50/50 text-gray-700 border-gray-300/50'
      } ${
        selected ? 'ring-2 ring-blue-500 ring-offset-2' : ''
      } min-w-[180px] relative opacity-60`}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ 
        scale: 1, 
        opacity: 0.6,
        boxShadow: '0 0 10px rgba(0, 0, 0, 0.05)',
      }}
      transition={{ duration: prefersReducedMotion ? 0.1 : 0.2 }}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      
      <div className="flex items-center gap-2">
        <GitBranch className="w-5 h-5" />
        <div className="flex-1">
          <div className="font-semibold text-sm">Counterfactual</div>
          <div className="text-xs text-gray-600 mt-0.5">Alternative Path</div>
        </div>
      </div>
      
      {data.roiDelta !== undefined && (
        <div className={`mt-2 pt-2 border-t ${
          isPositive ? 'border-green-300' : 'border-gray-300'
        }`}>
          <div className={`text-xs font-semibold ${
            isPositive ? 'text-green-700' : 'text-gray-600'
          }`}>
            ROI Δ: {isPositive ? '+' : ''}{data.roiDelta?.toFixed(2)}%
          </div>
        </div>
      )}
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </motion.div>
  )
}

export default memo(CounterfactualNode)
