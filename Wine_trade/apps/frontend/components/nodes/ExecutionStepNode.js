'use client'

import { memo } from 'react'
import { Handle, Position } from 'reactflow'
import { motion } from 'framer-motion'
import { CheckCircle2, XCircle, Loader2, Clock } from 'lucide-react'

const statusConfig = {
  PENDING: {
    color: 'bg-gray-100 text-gray-600 border-gray-300',
    icon: Clock,
    glow: '',
  },
  IN_PROGRESS: {
    color: 'bg-blue-100 text-blue-700 border-blue-400',
    icon: Loader2,
    glow: 'shadow-blue-400/50 shadow-lg',
    animate: true,
  },
  SUCCESS: {
    color: 'bg-green-100 text-green-700 border-green-400',
    icon: CheckCircle2,
    glow: 'shadow-green-400/50 shadow-lg',
  },
  FAILED: {
    color: 'bg-red-100 text-red-700 border-red-400',
    icon: XCircle,
    glow: 'shadow-red-400/50 shadow-lg',
  },
  COMPENSATED: {
    color: 'bg-yellow-100 text-yellow-700 border-yellow-400',
    icon: CheckCircle2,
    glow: '',
  },
}

function ExecutionStepNode({ data, selected }) {
  // Use visualStatus if available (for cinematic animation), otherwise fall back to status
  const displayStatus = data.visualStatus || data.status
  const config = statusConfig[displayStatus] || statusConfig.PENDING
  const Icon = config.icon
  const isRunning = displayStatus === 'IN_PROGRESS' || displayStatus === 'RUNNING'
  const isPending = displayStatus === 'PENDING'
  const isFailed = displayStatus === 'FAILED'
  
  // Check for reduced motion preference
  const prefersReducedMotion = typeof window !== 'undefined' && 
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  
  return (
    <motion.div
      className={`px-4 py-3 rounded-lg border-2 ${
        isPending ? 'border-dashed border-gray-300 bg-gray-50 text-gray-500' : config.color
      } ${config.glow} ${
        selected ? 'ring-2 ring-blue-500 ring-offset-2' : ''
      } min-w-[200px] relative transition-all duration-300`}
      initial={{ scale: 0.9, opacity: isPending ? 0.5 : 0 }}
      animate={{ 
        scale: 1, 
        opacity: isPending ? 0.6 : 1,
        ...(isRunning && !prefersReducedMotion && {
          scale: [1, 1.02, 1],
        }),
        ...(isFailed && !prefersReducedMotion && {
          x: [0, -5, 5, -5, 5, 0],
        }),
      }}
      transition={{
        duration: prefersReducedMotion ? 0.1 : 0.2,
        ...(isRunning && !prefersReducedMotion && {
          scale: {
            repeat: Infinity,
            duration: 2,
            ease: 'easeInOut',
          },
        }),
        ...(isFailed && !prefersReducedMotion && {
          x: {
            duration: 0.5,
            ease: 'easeInOut',
          },
        }),
      }}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      
      <div className="flex items-start gap-3">
        {/* Step Number Badge */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
          displayStatus === 'SUCCESS' ? 'bg-green-500 text-white' :
          displayStatus === 'FAILED' ? 'bg-red-500 text-white' :
          displayStatus === 'IN_PROGRESS' || displayStatus === 'RUNNING' ? 'bg-blue-500 text-white' :
          'bg-gray-400 text-white'
        }`}>
          {data.stepOrder}
        </div>
        
        {/* Step Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Icon 
              className={`w-4 h-4 ${isRunning ? 'animate-spin' : ''}`} 
            />
            <span className="font-semibold text-sm">{data.stepName}</span>
          </div>
          
          {isFailed && data.failureReason && (
            <div className="text-xs text-red-600 mt-1 line-clamp-2">
              {data.failureReason}
            </div>
          )}
          
          {data.completedAt && (
            <div className="text-xs text-gray-500 mt-1">
              {new Date(data.completedAt).toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>
      
      {/* Progress Ring for Running State */}
      {isRunning && !prefersReducedMotion && (
        <motion.div
          className="absolute inset-0 rounded-lg border-4 border-blue-400 border-t-transparent"
          animate={{ rotate: 360 }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      )}
      
      {/* Progress Bar for Running State */}
      {isRunning && (
        <motion.div
          className="absolute bottom-0 left-0 right-0 h-1 bg-blue-200 rounded-b-lg overflow-hidden"
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'linear',
          }}
        >
          <motion.div
            className="h-full bg-blue-600"
            animate={{ x: ['-100%', '100%'] }}
            transition={{
              duration: 1,
              repeat: Infinity,
              ease: 'linear',
            }}
          />
        </motion.div>
      )}
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </motion.div>
  )
}

export default memo(ExecutionStepNode)
