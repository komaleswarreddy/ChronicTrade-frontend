/**
 * Builds React Flow graph structure from execution data
 * Maps backend data to nodes and edges for visualization
 */

export function buildExecutionGraph(data) {
  // MarkerType enum values
  const MarkerType = {
    ArrowClosed: 'arrowclosed',
  }
  const nodes = []
  const edges = []
  let yPosition = 0
  const horizontalSpacing = 250
  const verticalSpacing = 150
  
  // Track node positions
  const nodePositions = {}
  let currentX = 0
  let currentY = 0
  
  // 1. Execution Gates (before execution starts)
  if (data.gates && data.gates.gates) {
    const gates = Array.isArray(data.gates.gates) ? data.gates.gates : []
    gates.forEach((gate, index) => {
      const gateId = `gate-${gate.gate_type || index}`
      nodes.push({
        id: gateId,
        type: 'execution_gate',
        position: { x: currentX, y: currentY },
        data: {
          gateType: gate.gate_type,
          status: gate.status,
          blockReason: gate.block_reason,
          ...gate,
        },
      })
      nodePositions[gateId] = { x: currentX, y: currentY }
      currentX += horizontalSpacing
    })
    
    // Connect gates sequentially
    for (let i = 0; i < gates.length - 1; i++) {
      edges.push({
        id: `edge-gate-${i}-${i + 1}`,
        source: `gate-${gates[i].gate_type || i}`,
        target: `gate-${gates[i + 1].gate_type || i + 1}`,
        type: gates[i].status === 'BLOCKED' ? 'blocked' : 'smoothstep',
        animated: gates[i].status === 'PASSED',
        style: {
          stroke: gates[i].status === 'BLOCKED' ? '#ef4444' : '#10b981',
          strokeWidth: 2,
          strokeDasharray: gates[i].status === 'BLOCKED' ? '5,5' : '0',
        },
      })
    }
    
    currentY += verticalSpacing
    currentX = 0
  }
  
  // 2. Compliance Gate (if exists)
  if (data.compliance) {
    const complianceId = 'compliance-gate'
    nodes.push({
      id: complianceId,
      type: 'compliance_gate',
      position: { x: currentX, y: currentY },
      data: {
        overallResult: data.compliance.overall_result,
        failedRules: data.compliance.failed_rules || [],
        ...data.compliance,
      },
    })
    nodePositions[complianceId] = { x: currentX, y: currentY }
    currentY += verticalSpacing
  }
  
  // 3. Execution Steps (main flow) - Improved layout with better spacing
  if (data.steps && data.steps.length > 0) {
    const steps = data.steps.sort((a, b) => (a.step_order || 0) - (b.step_order || 0))
    
    // Calculate layout: vertical flow with consistent spacing
    steps.forEach((step, index) => {
      const stepId = `step-${step.id || index}`
      // Center-aligned vertical flow
      const stepX = currentX
      const stepY = currentY + index * verticalSpacing
      
      nodes.push({
        id: stepId,
        type: 'execution_step',
        position: { x: stepX, y: stepY },
        data: {
          stepName: step.step_name,
          stepOrder: step.step_order || index + 1,
          status: step.status,
          failureReason: step.failure_reason,
          completedAt: step.completed_at,
          stepData: step.step_data,
          ...step,
        },
      })
      nodePositions[stepId] = { x: stepX, y: stepY }
      
      // Connect to previous step
      if (index > 0) {
        const prevStepId = `step-${steps[index - 1].id || index - 1}`
        const isBlocked = step.status === 'FAILED'
        edges.push({
          id: `edge-${prevStepId}-${stepId}`,
          source: prevStepId,
          target: stepId,
          type: 'animated', // Use custom animated edge type
          animated: step.status === 'IN_PROGRESS' || step.status === 'SUCCESS',
          style: {
            stroke: isBlocked ? '#ef4444' : '#3b82f6',
            strokeWidth: 2,
            strokeDasharray: isBlocked ? '5,5' : '0',
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: isBlocked ? '#ef4444' : '#3b82f6',
          },
          data: {
            isActive: step.status === 'IN_PROGRESS',
            isSuccess: step.status === 'SUCCESS',
            isFailed: isBlocked,
          },
        })
      }
    })
    
    // Connect compliance gate to first step if exists
    if (data.compliance && steps.length > 0) {
      const firstStepId = `step-${steps[0].id || 0}`
      edges.push({
        id: 'edge-compliance-first-step',
        source: 'compliance-gate',
        target: firstStepId,
        type: 'animated', // Use custom animated edge
        animated: true,
        style: {
          stroke: '#10b981',
          strokeWidth: 2,
        },
        data: {
          isActive: true,
          isSuccess: true,
          isFailed: false,
        },
      })
    }
    
    // Connect last gate to first step if gates exist
    if (data.gates && data.gates.gates && steps.length > 0) {
      const gates = Array.isArray(data.gates.gates) ? data.gates.gates : []
      if (gates.length > 0) {
        const lastGateId = `gate-${gates[gates.length - 1].gate_type || gates.length - 1}`
        const firstStepId = `step-${steps[0].id || 0}`
        edges.push({
          id: 'edge-last-gate-first-step',
          source: lastGateId,
          target: firstStepId,
          type: 'animated', // Use custom animated edge
          animated: true,
          style: {
            stroke: '#10b981',
            strokeWidth: 2,
          },
          data: {
            isActive: true,
            isSuccess: true,
            isFailed: false,
          },
        })
      }
    }
    
    currentY += steps.length * verticalSpacing
  }
  
  // 4. Logistics Events (after execution)
  if (data.logistics && data.logistics.events) {
    const events = Array.isArray(data.logistics.events) ? data.logistics.events : []
    events.forEach((event, index) => {
      const eventId = `logistics-${event.id || index}`
      nodes.push({
        id: eventId,
        type: 'logistics_event',
        position: { x: currentX + index * horizontalSpacing, y: currentY },
        data: {
          eventType: event.event_type,
          status: event.status,
          riskLevel: event.risk_level,
          ...event,
        },
      })
      
      // Connect to previous logistics event or last execution step
      if (index > 0) {
        const prevEventId = `logistics-${events[index - 1].id || index - 1}`
        edges.push({
          id: `edge-${prevEventId}-${eventId}`,
          source: prevEventId,
          target: eventId,
          type: 'smoothstep',
          animated: true,
          style: {
            stroke: '#8b5cf6',
            strokeWidth: 2,
          },
        })
      } else if (data.steps && data.steps.length > 0) {
        // Connect to last execution step
        const lastStep = data.steps[data.steps.length - 1]
        const lastStepId = `step-${lastStep.id || data.steps.length - 1}`
        edges.push({
          id: `edge-${lastStepId}-${eventId}`,
          source: lastStepId,
          target: eventId,
          type: 'smoothstep',
          animated: true,
          style: {
            stroke: '#8b5cf6',
            strokeWidth: 2,
          },
        })
      }
    })
    
    currentY += verticalSpacing
  }
  
  // 5. Counterfactual Path (parallel shadow lane - right side)
  if (data.counterfactual) {
    const counterfactualId = 'counterfactual-path'
    // Position counterfactual as parallel shadow lane on the right
    nodes.push({
      id: counterfactualId,
      type: 'counterfactual_node',
      position: { x: currentX + horizontalSpacing * 1.5, y: currentY - verticalSpacing * 2 },
      data: {
        roiDelta: data.counterfactual.roi_delta,
        riskDelta: data.counterfactual.risk_delta,
        opportunityCost: data.counterfactual.opportunity_cost,
        ...data.counterfactual,
      },
    })
    
    // Connect counterfactual to execution start (dashed line)
    if (data.steps && data.steps.length > 0) {
      const firstStepId = `step-${data.steps[0].id || 0}`
      edges.push({
        id: 'edge-counterfactual-start',
        source: firstStepId,
        target: counterfactualId,
        type: 'smoothstep',
        animated: false,
        style: {
          stroke: '#9ca3af',
          strokeWidth: 1,
          strokeDasharray: '10,5',
          opacity: 0.5,
        },
      })
    }
  }
  
  return { nodes, edges }
}
