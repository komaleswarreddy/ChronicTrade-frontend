'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import ExecutionCanvas from './ExecutionCanvas'
import ExecutionInspectorPanel from './ExecutionInspectorPanel'
import TimelineController from './TimelineController'
import ExecutionStepsPanel from './ExecutionStepsPanel'
import ComplianceEvaluationPanel from './ComplianceEvaluationPanel'
import CounterfactualPanel from './CounterfactualPanel'
import LogisticsTimelinePanel from './LogisticsTimelinePanel'
import ExecutionGatesPanel from './ExecutionGatesPanel'
import DecisionReplayPanel from './DecisionReplayPanel'
import DecisionTimeline from './DecisionTimeline'

export default function SimulationDetailModal({ simulation, isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('canvas') // Default to canvas view
  const [selectedNode, setSelectedNode] = useState(null)
  const [canvasError, setCanvasError] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [canvasNodes, setCanvasNodes] = useState([])
  const [executionState, setExecutionState] = useState(null)
  const playbackControlsRef = useRef(null)
  
  // Auto-start execution when modal opens if simulation is EXECUTED
  const shouldAutoStart = simulation?.status === 'EXECUTED'

  // Reset tab when modal opens - default to canvas for executed simulations
  useEffect(() => {
    if (isOpen) {
      setActiveTab(simulation?.status === 'EXECUTED' ? 'canvas' : 'execution')
    }
  }, [isOpen, simulation])

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen || !simulation) {
    return null
  }

  // Debug logging
  console.log('[SimulationDetailModal] Rendering modal:', {
    isOpen,
    simulationId: simulation?.id,
    activeTab
  })

  const tabs = [
    { id: 'canvas', label: 'Execution Canvas', icon: '🎨' },
    { id: 'execution', label: 'Execution Steps', icon: '⚙️' },
    { id: 'compliance', label: 'Compliance', icon: '✓' },
    { id: 'gates', label: 'Execution Gates', icon: '🚪' },
    { id: 'logistics', label: 'Logistics', icon: '📦' },
    { id: 'counterfactual', label: 'Counterfactual', icon: '🔮' },
    { id: 'decision', label: 'Decision Replay', icon: '📋' },
  ]
  
  const handleNodeSelect = (node) => {
    setSelectedNode(node)
  }
  
  const handleCloseInspector = () => {
    setSelectedNode(null)
  }
  
  const handleStepChange = useCallback((index) => {
    console.log('[SimulationDetailModal] HANDLE_STEP_CHANGE', { index, hasControls: !!playbackControlsRef.current })
    if (playbackControlsRef.current?.goToStep) {
      playbackControlsRef.current.goToStep(index)
    }
    // Don't manually set currentStepIndex here - let the state machine handle it
    // The state machine will update it via handleExecutionStateChange
  }, [])
  
  const handlePlay = () => {
    if (playbackControlsRef.current?.play) {
      playbackControlsRef.current.play()
    }
    // FIX #1: Removed setIsPlaying(true) - state machine owns isPlaying state
  }
  
  const handlePause = () => {
    if (playbackControlsRef.current?.pause) {
      playbackControlsRef.current.pause()
    }
    // FIX #1: Removed setIsPlaying(false) - state machine owns isPlaying state
  }
  
  const handleReset = () => {
    if (playbackControlsRef.current?.reset) {
      playbackControlsRef.current.reset()
    }
    // FIX #3: Removed local state mutations - state machine owns all execution state
    // setCurrentStepIndex(0) and setIsPlaying(false) are handled by state machine's reset()
  }
  
  const handleExecutionStateChange = useCallback((state) => {
    // Only update if values actually changed to prevent infinite loops
    setExecutionState(prev => {
      if (prev?.currentStepIndex === state.currentStepIndex && 
          prev?.executionState === state.executionState && 
          prev?.isPlaying === state.isPlaying) {
        return prev
      }
      return state
    })
    setCurrentStepIndex(prev => prev !== state.currentStepIndex ? state.currentStepIndex : prev)
    setIsPlaying(prev => prev !== state.isPlaying ? state.isPlaying : prev)
  }, [])

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" style={{ zIndex: 9999 }}>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
        onClick={onClose}
        style={{ zIndex: 9998 }}
      ></div>

      {/* Modal Container */}
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0" style={{ zIndex: 9999, position: 'relative' }}>
        {/* Modal */}
        <div 
          className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-6xl sm:w-full relative"
          style={{ zIndex: 10000 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Simulation Details: {simulation.asset_name || simulation.asset_id}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Action: {simulation.action} | Quantity: {simulation.quantity} | Status: {simulation.status}
                </p>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-1">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          {activeTab === 'canvas' ? (
            <div className="relative" style={{ height: '70vh' }}>
              <div className="flex h-full">
                {/* Execution Canvas */}
                <div className="flex-1 relative">
                  {canvasError ? (
                    <div className="h-full flex items-center justify-center bg-gray-50">
                      <div className="text-center p-6">
                        <p className="text-red-600 mb-4">Canvas failed to load. Using fallback view.</p>
                        <button
                          onClick={() => setActiveTab('execution')}
                          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                        >
                          View Execution Steps
                        </button>
                      </div>
                    </div>
                  ) : (
                    <ExecutionCanvas
                      simulationId={simulation.id}
                      onNodeSelect={handleNodeSelect}
                      selectedNodeId={selectedNode?.id}
                      onNodesChange={setCanvasNodes}
                      autoStart={shouldAutoStart}
                      onExecutionStateChange={handleExecutionStateChange}
                      playbackControls={playbackControlsRef}
                    />
                  )}
                </div>
                
                {/* Inspector Panel */}
                {selectedNode && (
                  <ExecutionInspectorPanel
                    selectedNode={selectedNode}
                    onClose={handleCloseInspector}
                  />
                )}
              </div>
              
              {/* Timeline Controller */}
              {/* FIX #2: Always render controls - don't wait for executionState */}
              <TimelineController
                nodes={canvasNodes}
                currentStepIndex={executionState?.currentStepIndex ?? -1}
                onStepChange={handleStepChange}
                onPlay={handlePlay}
                onPause={handlePause}
                onReset={handleReset}
                isPlaying={executionState?.isPlaying ?? false}
              />
            </div>
          ) : (
            <div className="px-6 py-6 max-h-[70vh] overflow-y-auto bg-white">
              {activeTab === 'execution' && (
                <div key="execution-tab">
                  <ExecutionStepsPanel simulationId={simulation.id} />
                </div>
              )}
              
              {activeTab === 'compliance' && (
                <div key="compliance-tab">
                  <ComplianceEvaluationPanel simulationId={simulation.id} />
                </div>
              )}
              
              {activeTab === 'gates' && (
                <div key="gates-tab">
                  <ExecutionGatesPanel simulationId={simulation.id} />
                </div>
              )}
              
              {activeTab === 'logistics' && (
                <div key="logistics-tab">
                  <LogisticsTimelinePanel simulationId={simulation.id} />
                </div>
              )}
              
              {activeTab === 'counterfactual' && (
                <div key="counterfactual-tab">
                  <CounterfactualPanel simulationId={simulation.id} />
                </div>
              )}
              
              {activeTab === 'decision' && (
                <div key="decision-tab" className="space-y-6">
                  <DecisionReplayPanel simulationId={simulation.id} />
                  <DecisionTimeline simulationId={simulation.id} />
                </div>
              )}
            </div>
          )}

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
