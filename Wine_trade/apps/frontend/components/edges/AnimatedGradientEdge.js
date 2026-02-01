'use client'

import { memo } from 'react'
import { getSmoothStepPath } from 'reactflow'

/**
 * Custom animated edge with gradient and flowing effects
 * Creates a visually stunning flow between nodes
 */
function AnimatedGradientEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  animated = false,
  data,
}) {
  // Use smoothstep for better visual flow
  const [edgePath] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  })

  // Determine edge state and colors
  // CRITICAL: isActive should be true for both animated transitions AND completed flows
  const isActive = animated || data?.isActive || false
  const isSuccess = data?.isSuccess || style?.stroke === '#10b981'
  const isFailed = data?.isFailed || style?.stroke === '#ef4444'
  // Show flowing animation for both active transitions and completed success edges
  const isPending = !isActive && !isSuccess && !isFailed
  const shouldShowFlowing = isActive || (isSuccess && !isFailed) // Flow for active OR completed success edges

  // Color scheme based on state
  const getGradientColors = () => {
    if (isFailed) {
      return {
        start: '#ef4444',
        mid: '#dc2626',
        end: '#b91c1c',
      }
    }
    if (isSuccess || isActive) {
      return {
        start: '#10b981',
        mid: '#34d399',
        end: '#059669',
      }
    }
    return {
      start: '#3b82f6',
      mid: '#60a5fa',
      end: '#2563eb',
    }
  }

  const colors = getGradientColors()
  const strokeWidth = shouldShowFlowing ? 4 : isPending ? 2 : 3
  const uniqueId = id.replace(/[^a-zA-Z0-9]/g, '-')
  
  // Debug logging for flowing edges
  if (shouldShowFlowing && process.env.NODE_ENV === 'development') {
    console.log('[AnimatedGradientEdge] RENDERING_FLOWING_EDGE', {
      id: id.substring(0, 20),
      isActive,
      isSuccess,
      shouldShowFlowing,
      animated
    })
  }

  return (
    <>
      <defs>
        {/* Base gradient */}
        <linearGradient id={`gradient-${uniqueId}`} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={colors.start} stopOpacity={isPending ? 0.4 : 0.9} />
          <stop offset="50%" stopColor={colors.mid} stopOpacity={isPending ? 0.5 : 1} />
          <stop offset="100%" stopColor={colors.end} stopOpacity={isPending ? 0.4 : 0.9} />
        </linearGradient>
        
        {/* Animated flowing gradient for active edges */}
        {shouldShowFlowing && (
          <linearGradient id={`animated-gradient-${uniqueId}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={colors.start} stopOpacity="0.4">
              <animate
                attributeName="stop-opacity"
                values="0.4;1;0.4"
                dur="2s"
                repeatCount="indefinite"
              />
            </stop>
            <stop offset="30%" stopColor={colors.mid} stopOpacity="0.6">
              <animate
                attributeName="stop-opacity"
                values="0.6;1;0.6"
                dur="1.5s"
                repeatCount="indefinite"
                begin="0.2s"
              />
            </stop>
            <stop offset="60%" stopColor={colors.end} stopOpacity="0.8">
              <animate
                attributeName="stop-opacity"
                values="0.8;1;0.8"
                dur="1.8s"
                repeatCount="indefinite"
                begin="0.4s"
              />
            </stop>
            <stop offset="100%" stopColor={colors.start} stopOpacity="0.4">
              <animate
                attributeName="stop-opacity"
                values="0.4;1;0.4"
                dur="2s"
                repeatCount="indefinite"
                begin="0.6s"
              />
            </stop>
          </linearGradient>
        )}

        {/* Glow filter for active edges */}
        {shouldShowFlowing && (
          <filter id={`glow-${uniqueId}`} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        )}

        {/* Flowing dash pattern for active edges */}
        {shouldShowFlowing && (
          <>
            <style>
              {`
                @keyframes flow-${uniqueId} {
                  0% {
                    stroke-dashoffset: 0;
                  }
                  100% {
                    stroke-dashoffset: 20;
                  }
                }
                .flowing-edge-${uniqueId} {
                  animation: flow-${uniqueId} 1.5s linear infinite;
                  stroke-dasharray: 8 4;
                }
              `}
            </style>
          </>
        )}
      </defs>

      {/* Shadow/glow layer for depth on active edges */}
      {shouldShowFlowing && (
        <path
          d={edgePath}
          fill="none"
          stroke={colors.start}
          strokeWidth={strokeWidth + 6}
          strokeOpacity="0.15"
          filter={`url(#glow-${uniqueId})`}
          style={{ pointerEvents: 'none' }}
        />
      )}

      {/* Main edge path with gradient */}
      <path
        d={edgePath}
        fill="none"
        stroke={shouldShowFlowing ? `url(#animated-gradient-${uniqueId})` : `url(#gradient-${uniqueId})`}
        strokeWidth={shouldShowFlowing ? (strokeWidth + 1) : strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
        markerEnd={markerEnd}
        className={shouldShowFlowing ? `flowing-edge-${uniqueId}` : ''}
        opacity={isPending ? 0.4 : shouldShowFlowing ? 1 : 0.8}
        style={{
          ...style,
          filter: shouldShowFlowing ? `url(#glow-${uniqueId})` : 'none',
          transition: 'opacity 0.3s ease, stroke-width 0.3s ease',
        }}
      />

      {/* Animated flowing dot for active edges */}
      {shouldShowFlowing && (
        <g>
          <circle r="5" fill={colors.mid} opacity="0.9">
            <animateMotion
              dur="2s"
              repeatCount="indefinite"
              path={edgePath}
            />
            <animate
              attributeName="opacity"
              values="0.3;1;0.3"
              dur="1.5s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="r"
              values="3;6;3"
              dur="1.5s"
              repeatCount="indefinite"
            />
          </circle>
          {/* Secondary flowing dot for extra visual appeal */}
          <circle r="3" fill={colors.start} opacity="0.7">
            <animateMotion
              dur="2.5s"
              repeatCount="indefinite"
              path={edgePath}
              begin="0.5s"
            />
            <animate
              attributeName="opacity"
              values="0.2;0.8;0.2"
              dur="2s"
              repeatCount="indefinite"
            />
          </circle>
        </g>
      )}
    </>
  )
}

export default memo(AnimatedGradientEdge)
