'use client'

import { useCallback, useMemo, useState, useEffect, useRef } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import axios from 'axios'
import ExecutionStepNode from './nodes/ExecutionStepNode'
import ComplianceGateNode from './nodes/ComplianceGateNode'
import ExecutionGateNode from './nodes/ExecutionGateNode'
import LogisticsEventNode from './nodes/LogisticsEventNode'
import CounterfactualNode from './nodes/CounterfactualNode'
import AnimatedGradientEdge from './edges/AnimatedGradientEdge'
import { buildExecutionGraph } from './utils/executionGraphBuilder'
import { useExecutionStateMachine } from './hooks/useExecutionStateMachine'

const nodeTypes = {
  execution_step: ExecutionStepNode,
  compliance_gate: ComplianceGateNode,
  execution_gate: ExecutionGateNode,
  logistics_event: LogisticsEventNode,
  counterfactual_node: CounterfactualNode,
}

const edgeTypes = {
  default: AnimatedGradientEdge,
  animated: AnimatedGradientEdge,
  smoothstep: AnimatedGradientEdge,
}

export default function ExecutionCanvas({ 
  simulationId, 
  getToken,
  onNodeSelect,
  selectedNodeId,
  onNodesChange: externalOnNodesChange,
  autoStart = false,
  onExecutionStateChange,
  playbackControls
}) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [executionData, setExecutionData] = useState(null)
  const reactFlowInstance = useRef(null)
  const initialNodesRef = useRef([])
  
  // FIX #5: Stabilize nodes reference for state machine
  // Only recalculate when nodes actually change (by content, not just reference)
  // State machine filters for execution_step nodes internally, so we pass all nodes
  const stableNodesRef = useRef([])
  const prevNodesHashRef = useRef('')
  const stableNodesForStateMachine = useMemo(() => {
    // Create a hash of node IDs, types, and statuses to detect actual content changes
    // Include both originalStatus and visualStatus to catch all changes
    const nodesHash = nodes.length > 0 
      ? nodes.map(n => `${n.id}:${n.type}:${n.data?.originalStatus || n.data?.status || 'PENDING'}:${n.data?.visualStatus || 'PENDING'}`).join('|')
      : ''
    
    // Always create new array reference if hash changed OR if nodes array length changed
    // This ensures state machine gets updated nodes even if hash is same but array is new
    if (prevNodesHashRef.current !== nodesHash || stableNodesRef.current.length !== nodes.length) {
      prevNodesHashRef.current = nodesHash
      // Return new array reference - state machine will filter for execution_step internally
      stableNodesRef.current = [...nodes]
      console.log('[ExecutionCanvas] STABLE_NODES_UPDATED', { 
        nodeCount: nodes.length, 
        executionStepCount: nodes.filter(n => n.type === 'execution_step').length,
        hash: nodesHash.substring(0, 100) 
      })
      return stableNodesRef.current
    }
    
    // Content unchanged - return previous reference to maintain stability
    return stableNodesRef.current
  }, [nodes])
  
  // Execution state machine - use stable nodes reference
  const executionState = useExecutionStateMachine(stableNodesForStateMachine, autoStart)
  
  // Expose nodes to parent - use memoized hash to prevent infinite loops
  const nodesHash = useMemo(() => {
    return nodes
      .map(n => `${n.id}:${n.data?.visualStatus || 'PENDING'}`)
      .join('|')
  }, [nodes])
  
  const prevNodesHashForParentRef = useRef('') // Renamed to avoid conflict with prevNodesHashRef above
  const externalOnNodesChangeRef = useRef(externalOnNodesChange)
  externalOnNodesChangeRef.current = externalOnNodesChange
  
  useEffect(() => {
    // Only call if nodes hash actually changed
    if (externalOnNodesChangeRef.current && nodes.length > 0 && prevNodesHashForParentRef.current !== nodesHash) {
      prevNodesHashForParentRef.current = nodesHash
      externalOnNodesChangeRef.current(nodes)
    }
  }, [nodesHash, nodes.length]) // Depend on hash and length only
  
  // Expose execution state to parent - only send primitive values
  const executionStateRef = useRef(executionState)
  executionStateRef.current = executionState
  
  useEffect(() => {
    if (onExecutionStateChange) {
      // Only send primitive values to prevent infinite loops
      onExecutionStateChange({
        currentStepIndex: executionState.currentStepIndex,
        executionState: executionState.executionState,
        isPlaying: executionState.isPlaying,
        totalSteps: executionState.totalSteps,
      })
    }
  }, [executionState.currentStepIndex, executionState.executionState, executionState.isPlaying, executionState.totalSteps, onExecutionStateChange])
  
  // Sync playback controls - use ref to prevent re-renders
  useEffect(() => {
    if (playbackControls?.current) {
      playbackControls.current.play = executionState.play
      playbackControls.current.pause = executionState.pause
      playbackControls.current.reset = executionState.reset
      playbackControls.current.nextStep = executionState.nextStep
      playbackControls.current.previousStep = executionState.previousStep
      playbackControls.current.goToStep = executionState.goToStep
    }
  }, [executionState.play, executionState.pause, executionState.reset, executionState.nextStep, executionState.previousStep, executionState.goToStep, playbackControls])

  // Reset execution state when simulationId changes
  useEffect(() => {
    if (simulationId) {
      // Reset nodes and edges
      setNodes([])
      setEdges([])
      setExecutionData(null)
      initialNodesRef.current = []
    }
  }, [simulationId, setNodes, setEdges])

  // Fetch all execution data
  useEffect(() => {
    if (!simulationId || !getToken) return
    
    const fetchAllData = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const token = await getToken()
        if (!token || !token.trim()) {
          throw new Error('No authentication token available')
        }
        
        const authConfig = {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
        
        const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:4000'
        
        // Fetch all data in parallel
        const [stepsRes, complianceRes, gatesRes, logisticsRes, counterfactualRes] = await Promise.allSettled([
          axios.get(`${API_BASE}/api/executions/${simulationId}/steps`, authConfig),
          axios.get(`${API_BASE}/api/compliance/${simulationId}/evaluation`, authConfig).catch(() => ({ data: null })),
          axios.get(`${API_BASE}/api/executions/${simulationId}/gates`, authConfig).catch(() => ({ data: null })),
          axios.get(`${API_BASE}/api/logistics/${simulationId}/timeline`, authConfig).catch(() => ({ data: null })),
          axios.get(`${API_BASE}/api/counterfactual/${simulationId}`, authConfig).catch(() => ({ data: null })),
        ])
        
        const data = {
          steps: stepsRes.status === 'fulfilled' ? (stepsRes.value.data?.steps || []) : [],
          compliance: complianceRes.status === 'fulfilled' && complianceRes.value?.data ? complianceRes.value.data : null,
          gates: gatesRes.status === 'fulfilled' && gatesRes.value?.data ? gatesRes.value.data : null,
          logistics: logisticsRes.status === 'fulfilled' && logisticsRes.value?.data ? logisticsRes.value.data : null,
          counterfactual: counterfactualRes.status === 'fulfilled' && counterfactualRes.value?.data ? counterfactualRes.value.data : null,
        }
        
        setExecutionData(data)
        
        // Build graph from data
        const { nodes: graphNodes, edges: graphEdges } = buildExecutionGraph(data)
        
        // Initialize all execution steps to PENDING state for cinematic effect
        const initializedNodes = graphNodes.map(node => {
          if (node.type === 'execution_step') {
            return {
              ...node,
              data: {
                ...node.data,
                visualStatus: 'PENDING', // Override for visual state
                originalStatus: node.data.status || 'PENDING', // Preserve original status
              }
            }
          }
          return node
        })
        
        initialNodesRef.current = initializedNodes
        setNodes(initializedNodes)
        setEdges(graphEdges)
        
        // Fit view after nodes are set
        setTimeout(() => {
          if (reactFlowInstance.current) {
            reactFlowInstance.current.fitView({ padding: 0.2, duration: 300 })
          }
        }, 100)
        
      } catch (err) {
        console.error('Failed to fetch execution data:', err)
        setError(err.response?.data?.detail || err.message || 'Failed to fetch execution data')
      } finally {
        setLoading(false)
      }
    }
    
    fetchAllData()
  }, [simulationId, getToken])

  const onNodeClick = useCallback((event, node) => {
    if (onNodeSelect) {
      onNodeSelect(node)
    }
  }, [onNodeSelect])

  const onInit = useCallback((instance) => {
    reactFlowInstance.current = instance
  }, [])

  // Update node visual states based on execution state machine
  // Use refs to track previous values and only update when actually changed
  const prevStepIndexRef = useRef(-1)
  const prevExecutionStateRef = useRef('IDLE')
  const prevSelectedNodeIdRef = useRef(null)
  const getStepStateRef = useRef(executionState.getStepState)
  getStepStateRef.current = executionState.getStepState
  
  useEffect(() => {
    const stepIndexChanged = prevStepIndexRef.current !== executionState.currentStepIndex
    const executionStateChanged = prevExecutionStateRef.current !== executionState.executionState
    const selectedNodeChanged = prevSelectedNodeIdRef.current !== selectedNodeId
    
    // FIX: Detect reset transition (IDLE state with currentStepIndex === -1)
    const isReset = executionState.executionState === 'IDLE' && executionState.currentStepIndex === -1
    const wasReset = prevStepIndexRef.current !== -1 && executionState.currentStepIndex === -1
    
    // Only update if something actually changed OR if reset occurred
    if (stepIndexChanged || executionStateChanged || selectedNodeChanged || wasReset) {
      prevStepIndexRef.current = executionState.currentStepIndex
      prevExecutionStateRef.current = executionState.executionState
      prevSelectedNodeIdRef.current = selectedNodeId
      
      console.log('[ExecutionCanvas] UPDATING_NODES', { 
        stepIndex: executionState.currentStepIndex, 
        executionState: executionState.executionState,
        changed: { stepIndexChanged, executionStateChanged, selectedNodeChanged, wasReset, isReset }
      })
      
      setNodes((nds) => {
        const updatedNodes = nds.map((node) => {
          if (node.type === 'execution_step') {
            const stepIndex = nds.filter(n => n.type === 'execution_step').indexOf(node)
            
            // FIX: Force all nodes to PENDING on reset
            if (isReset || wasReset) {
              return {
                ...node,
                selected: node.id === selectedNodeId,
                data: {
                  ...node.data,
                  visualStatus: 'PENDING',
                }
              }
            }
            
            const stepState = getStepStateRef.current(stepIndex)
            
            // Map step state to visual status
            let visualStatus = 'PENDING'
            if (stepState === 'RUNNING') {
              visualStatus = 'IN_PROGRESS'
            } else if (stepState === 'COMPLETED') {
              visualStatus = node.data?.originalStatus === 'FAILED' ? 'FAILED' : 'SUCCESS'
            } else {
              visualStatus = 'PENDING'
            }
            
            // Log status changes
            if (node.data?.visualStatus !== visualStatus) {
              console.log('[ExecutionCanvas] NODE_STATUS_CHANGE', { 
                nodeId: node.id, 
                stepIndex, 
                oldStatus: node.data?.visualStatus, 
                newStatus: visualStatus,
                stepState 
              })
            }
            
            // Always create a new object to ensure React Flow detects the change
            // This is important for proper re-rendering
            return {
              ...node,
              selected: node.id === selectedNodeId,
              data: {
                ...node.data,
                visualStatus,
              }
            }
          }
          
          // Always create new object for non-execution-step nodes too
          return {
            ...node,
            selected: node.id === selectedNodeId,
          }
        })
        
        console.log('[ExecutionCanvas] NODES_UPDATED', { 
          count: updatedNodes.length,
          executionSteps: updatedNodes.filter(n => n.type === 'execution_step').map(n => ({
            id: n.id,
            visualStatus: n.data?.visualStatus
          }))
        })
        
        return updatedNodes
      })
    }
  }, [executionState.currentStepIndex, executionState.executionState, selectedNodeId, setNodes])
  
  // Update edge animations based on execution state
  // Use ref to track previous node states and only update when changed
  const prevNodesStateRef = useRef('')
  
  useEffect(() => {
    // Create a simple hash of node visual states to detect changes
    const nodesStateHash = nodes
      .filter(n => n.type === 'execution_step')
      .map(n => `${n.id}:${n.data?.visualStatus || 'PENDING'}`)
      .join('|')
    
    // Only update if node states actually changed
    if (prevNodesStateRef.current !== nodesStateHash) {
      prevNodesStateRef.current = nodesStateHash
      
      setEdges((eds) =>
        eds.map((edge) => {
          const sourceNode = nodes.find(n => n.id === edge.source)
          const targetNode = nodes.find(n => n.id === edge.target)
          
          // Determine edge state for custom animated edge
          const isExecutionStepEdge = 
            sourceNode?.type === 'execution_step' &&
            targetNode?.type === 'execution_step'
          
          const sourceStatus = sourceNode?.data?.visualStatus || 'PENDING'
          const targetStatus = targetNode?.data?.visualStatus || 'PENDING'
          
          // CRITICAL FIX: Animate edge in multiple scenarios:
          // 1. Source is SUCCESS and target is IN_PROGRESS (transitioning)
          // 2. Source is SUCCESS and target is SUCCESS (completed, show flowing)
          // 3. Source is SUCCESS and target is PENDING (just completed, show flowing)
          const shouldAnimate = 
            isExecutionStepEdge &&
            sourceStatus === 'SUCCESS' &&
            (targetStatus === 'IN_PROGRESS' || targetStatus === 'SUCCESS' || targetStatus === 'PENDING')
          
          // Determine success/failed state
          const isSuccess = 
            isExecutionStepEdge &&
            (sourceStatus === 'SUCCESS' || targetStatus === 'SUCCESS')
          
          const isFailed = 
            isExecutionStepEdge &&
            (sourceStatus === 'FAILED' || targetStatus === 'FAILED')
          
          // Also animate if both are SUCCESS (completed flow)
          const isCompletedFlow = 
            isExecutionStepEdge &&
            sourceStatus === 'SUCCESS' &&
            targetStatus === 'SUCCESS'
          
          const newStroke = shouldAnimate ? '#10b981' : 
                           isFailed ? '#ef4444' : 
                           isSuccess ? '#10b981' : 
                           (edge.style?.stroke || '#3b82f6')
          
          // Use custom animated edge type for execution step edges
          const edgeType = isExecutionStepEdge ? 'animated' : edge.type || 'default'
          
          // CRITICAL FIX: Update edge data to trigger animations
          const edgeData = {
            isActive: shouldAnimate || isCompletedFlow, // Animate both transitioning and completed flows
            isSuccess: isSuccess && !shouldAnimate && !isCompletedFlow,
            isFailed: isFailed,
          }
          
          // Always update edge data to ensure animations trigger
          const finalAnimated = shouldAnimate || isCompletedFlow
          const dataChanged = JSON.stringify(edge.data || {}) !== JSON.stringify(edgeData)
          const animatedChanged = edge.animated !== finalAnimated
          const strokeChanged = edge.style?.stroke !== newStroke
          const typeChanged = edge.type !== edgeType
          
          // Update if any property changed
          if (!animatedChanged && !strokeChanged && !typeChanged && !dataChanged) {
            return edge
          }
          
          console.log('[ExecutionCanvas] UPDATING_EDGE', {
            edgeId: edge.id,
            sourceStatus,
            targetStatus,
            finalAnimated,
            edgeData,
            dataChanged,
            animatedChanged,
            strokeChanged,
            typeChanged
          })
          
          return {
            ...edge,
            type: edgeType,
            animated: finalAnimated, // Animate both transitioning and completed
            data: edgeData,
            style: {
              ...(edge.style || {}),
              stroke: newStroke,
            }
          }
        })
      )
    }
  }, [nodes, setEdges])

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading execution canvas...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center p-6 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-semibold mb-2">Error loading execution canvas</p>
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-full bg-gray-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onInit={onInit}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={true}
        panOnScroll={true}
        zoomOnScroll={true}
        zoomOnPinch={true}
      >
        <Background color="#e5e7eb" gap={16} />
        <Controls />
        <MiniMap 
          nodeColor={(node) => {
            if (node.type === 'execution_step') {
              // Use visualStatus instead of status for MiniMap
              const visualStatus = node.data?.visualStatus || node.data?.status
              if (visualStatus === 'SUCCESS') return '#10b981'
              if (visualStatus === 'FAILED') return '#ef4444'
              if (visualStatus === 'IN_PROGRESS') return '#3b82f6'
              return '#9ca3af'
            }
            return '#6b7280'
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </div>
  )
}
