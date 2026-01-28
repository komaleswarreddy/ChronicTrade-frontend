'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, Pause, SkipForward, SkipBack, RotateCcw } from 'lucide-react'

export default function TimelineController({ 
  nodes = [], 
  currentStepIndex = 0,
  onStepChange,
  onPlay,
  onPause,
  onReset,
  isPlaying = false 
}) {
  const executionSteps = nodes.filter(n => n.type === 'execution_step')
  const totalSteps = executionSteps.length
  
  const handlePrevious = () => {
    if (currentStepIndex > 0 && onStepChange) {
      onStepChange(currentStepIndex - 1)
    }
  }
  
  const handleNext = () => {
    if (currentStepIndex < totalSteps - 1 && onStepChange) {
      onStepChange(currentStepIndex + 1)
    }
  }
  
  const handlePlayPause = () => {
    if (isPlaying) {
      onPause()
    } else {
      onPlay()
    }
  }
  
  // Auto-play through steps - removed to prevent conflicts with state machine
  // The state machine handles auto-advancement internally
  
  if (totalSteps === 0) {
    return null
  }
  
  return (
    <motion.div
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-6 py-4 shadow-lg z-50"
    >
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between gap-4">
          {/* Playback Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrevious}
              disabled={currentStepIndex === 0}
              className={`p-2 rounded-md ${
                currentStepIndex === 0
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <SkipBack className="w-4 h-4" />
            </button>
            
            <button
              onClick={handlePlayPause}
              className="p-2 rounded-md bg-blue-600 text-white hover:bg-blue-700"
            >
              {isPlaying ? (
                <Pause className="w-4 h-4" />
              ) : (
                <Play className="w-4 h-4" />
              )}
            </button>
            
            <button
              onClick={handleNext}
              disabled={currentStepIndex === totalSteps - 1}
              className={`p-2 rounded-md ${
                currentStepIndex === totalSteps - 1
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <SkipForward className="w-4 h-4" />
            </button>
            
            <button
              onClick={onReset}
              className="p-2 rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
          
          {/* Progress Bar */}
          <div className="flex-1 max-w-md">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs text-gray-600">
                Step {currentStepIndex + 1} of {totalSteps}
              </span>
              {executionSteps[currentStepIndex] && (
                <span className="text-xs text-gray-500">
                  {executionSteps[currentStepIndex].data?.stepName || ''}
                </span>
              )}
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-blue-600 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ 
                  width: `${((currentStepIndex + 1) / totalSteps) * 100}%` 
                }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
          
          {/* Step Indicators */}
          <div className="flex items-center gap-1">
            {executionSteps.slice(0, 10).map((step, index) => (
              <button
                key={step.id}
                onClick={() => onStepChange(index)}
                className={`w-2 h-2 rounded-full transition-all ${
                  index === currentStepIndex
                    ? 'bg-blue-600 w-3 h-3'
                    : index < currentStepIndex
                    ? 'bg-green-500'
                    : 'bg-gray-300'
                }`}
                title={step.data?.stepName}
              />
            ))}
            {totalSteps > 10 && (
              <span className="text-xs text-gray-500 ml-1">+{totalSteps - 10}</span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
