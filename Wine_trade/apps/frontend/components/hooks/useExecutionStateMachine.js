'use client'

import { useState, useEffect, useCallback, useRef, useMemo } from 'react'

/**
 * Execution State Machine
 * States: IDLE → EXECUTION_STARTED → STEP_RUNNING → STEP_COMPLETED → EXECUTION_FINISHED
 */
export function useExecutionStateMachine(nodes = [], autoStart = false) {
  const [executionState, setExecutionState] = useState('IDLE')
  const [currentStepIndex, setCurrentStepIndex] = useState(-1)
  const [isPlaying, setIsPlaying] = useState(false)
  const [completedSteps, setCompletedSteps] = useState(new Set())
  const animationRef = useRef(null)
  const isPlayingRef = useRef(false) // Ref to track isPlaying for closures
  const currentStepIndexRef = useRef(-1) // FIX #4: Track step index for guard logic
  const prefersReducedMotion = useRef(
    typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  )
  
  // Keep ref in sync with state
  useEffect(() => {
    isPlayingRef.current = isPlaying
  }, [isPlaying])

  // CRITICAL FIX: Memoize executionSteps to prevent recalculation on every render
  // This ensures stable reference and prevents stale closures in effects
  const executionSteps = useMemo(() => {
    return nodes.filter(n => n.type === 'execution_step')
  }, [nodes])
  const totalSteps = executionSteps.length
  
  // Store executionSteps in ref for access in timeout callbacks (avoids stale closures)
  const executionStepsRef = useRef(executionSteps)
  useEffect(() => {
    executionStepsRef.current = executionSteps
  }, [executionSteps])
  
  // Refs for auto-start tracking
  const autoStartRef = useRef(autoStart)
  const hasAutoStartedRef = useRef(false)

  // Initialize all steps to PENDING state
  const initializeSteps = useCallback(() => {
    if (animationRef.current) {
      clearTimeout(animationRef.current)
      animationRef.current = null
    }
    setExecutionState('IDLE')
    setCurrentStepIndex(-1)
    setIsPlaying(false)
    isPlayingRef.current = false // FIX: Reset ref to prevent stale state
    currentStepIndexRef.current = -1 // FIX #4: Reset step index ref
    setCompletedSteps(new Set())
    hasAutoStartedRef.current = false // Reset auto-start flag
  }, [])

  // Start execution
  const startExecution = useCallback(() => {
    if (executionState === 'IDLE' && totalSteps > 0) {
      console.log('[StateMachine] START_EXECUTION', { totalSteps, currentStepIndex: -1 })
      // Clear any existing timer first
      if (animationRef.current) {
        clearTimeout(animationRef.current)
        animationRef.current = null
      }
      setExecutionState('EXECUTION_STARTED')
      setCurrentStepIndex(0)
      currentStepIndexRef.current = 0 // CRITICAL FIX: Update ref immediately
      setIsPlaying(true)
      isPlayingRef.current = true
      // Immediately transition to STEP_RUNNING for the first step
      // Store in animationRef for proper cleanup
      animationRef.current = setTimeout(() => {
        console.log('[StateMachine] TRANSITION: EXECUTION_STARTED → STEP_RUNNING', { stepIndex: 0 })
        animationRef.current = null
        setExecutionState('STEP_RUNNING')
      }, 50)
    }
  }, [executionState, totalSteps])

  // Advance to next step
  const advanceStep = useCallback(() => {
    if (currentStepIndex < totalSteps - 1) {
      const nextIndex = currentStepIndex + 1
      console.log('[StateMachine] ADVANCE_STEP', { from: currentStepIndex, to: nextIndex, totalSteps })
      setCurrentStepIndex(nextIndex)
      currentStepIndexRef.current = nextIndex // CRITICAL FIX: Update ref immediately
      setExecutionState('STEP_RUNNING')
      
      // Mark previous step as completed
      if (currentStepIndex >= 0) {
        setCompletedSteps(prev => new Set([...prev, currentStepIndex]))
      }
    } else {
      // All steps completed
      console.log('[StateMachine] ALL_STEPS_COMPLETED', { currentStepIndex, totalSteps })
      setCompletedSteps(prev => new Set([...prev, currentStepIndex]))
      setExecutionState('EXECUTION_FINISHED')
      setIsPlaying(false)
    }
  }, [currentStepIndex, totalSteps])

  // Complete current step
  // FIX: Removed setTimeout - auto-advance effect handles STEP_COMPLETED → STEP_RUNNING transition
  const completeCurrentStep = useCallback(() => {
    if (executionState === 'STEP_RUNNING' || executionState === 'EXECUTION_STARTED') {
      // CRITICAL FIX: Use ref to get current executionSteps (avoids stale closure)
      const currentStep = executionStepsRef.current?.[currentStepIndex]
      const stepStatus = currentStep?.data?.originalStatus || currentStep?.data?.status
      
      // Defensive check: if step doesn't exist, skip completion
      if (!currentStep) {
        console.warn('[StateMachine] COMPLETE_STEP - STEP_NOT_FOUND', { currentStepIndex, totalSteps })
        return
      }
      
      const stepFailed = stepStatus === 'FAILED'
      const isLastStep = currentStepIndex === totalSteps - 1
      
      console.log('[StateMachine] COMPLETE_STEP', { 
        stepIndex: currentStepIndex, 
        executionState, 
        stepStatus, 
        stepFailed,
        isLastStep,
        totalSteps,
        isPlaying: isPlayingRef.current 
      })
      
      if (stepFailed) {
        // Stop execution on failure
        console.log('[StateMachine] STEP_FAILED - stopping execution')
        setIsPlaying(false)
        isPlayingRef.current = false
        setExecutionState('EXECUTION_FINISHED')
        // Mark current step as completed even if failed
        setCompletedSteps(prev => new Set([...prev, currentStepIndex]))
      } else if (isLastStep) {
        // CRITICAL FIX: Last step - immediately finish execution (FORCE COMPLETION)
        console.log('[StateMachine] LAST_STEP_COMPLETED - FORCING_FINISH', { 
          stepIndex: currentStepIndex, 
          totalSteps 
        })
        setExecutionState('STEP_COMPLETED')
        // Mark current step as completed
        setCompletedSteps(prev => new Set([...prev, currentStepIndex]))
        // Immediately transition to FINISHED - don't wait for effect
        // FORCE: Use 2-second delay even for last step completion
        setTimeout(() => {
          console.log('[StateMachine] FORCE_FINISH_TRANSITION')
          setExecutionState('EXECUTION_FINISHED')
          setIsPlaying(false)
          isPlayingRef.current = false
        }, 2000) // FORCE: Strict 2-second delay before finishing
      } else {
        // Not last step - normal completion flow
        setExecutionState('STEP_COMPLETED')
        // Mark current step as completed
        setCompletedSteps(prev => new Set([...prev, currentStepIndex]))
        // FIX: Removed setTimeout - let auto-advance effect handle transition to next step
      }
    }
  }, [executionState, currentStepIndex, totalSteps])
  // CRITICAL FIX: Removed executionSteps from dependencies - use ref instead to avoid stale closures

  // Go to specific step
  const goToStep = useCallback((index) => {
    if (index >= 0 && index < totalSteps) {
      console.log('[StateMachine] GO_TO_STEP', { index, totalSteps })
      // Clear any pending animations
      if (animationRef.current) {
        console.log('[StateMachine] CLEARING_PENDING_ANIMATION')
        clearTimeout(animationRef.current)
        animationRef.current = null
      }
      
      // FIX: Pause auto-run when manually navigating
      setIsPlaying(false)
      isPlayingRef.current = false
      currentStepIndexRef.current = index // CRITICAL FIX: Update ref immediately
      
      setCurrentStepIndex(index)
      setExecutionState('STEP_RUNNING')
      
      // Mark all previous steps as completed
      const newCompleted = new Set()
      for (let i = 0; i < index; i++) {
        newCompleted.add(i)
      }
      setCompletedSteps(newCompleted)
    }
  }, [totalSteps])

  // Play/pause
  const play = useCallback(() => {
    console.log('[StateMachine] PLAY', { executionState })
    if (executionState === 'IDLE') {
      startExecution()
    } else {
      setIsPlaying(true)
      isPlayingRef.current = true
      if (executionState === 'STEP_COMPLETED') {
        advanceStep()
      }
    }
  }, [executionState, startExecution, advanceStep])

  const pause = useCallback(() => {
    console.log('[StateMachine] PAUSE')
    setIsPlaying(false)
    isPlayingRef.current = false
    if (animationRef.current) {
      clearTimeout(animationRef.current)
      animationRef.current = null
    }
  }, [])

  // Reset execution
  const reset = useCallback(() => {
    if (animationRef.current) {
      clearTimeout(animationRef.current)
      animationRef.current = null
    }
    initializeSteps()
  }, [initializeSteps])

  // Previous step
  const previousStep = useCallback(() => {
    if (currentStepIndex > 0) {
      pause()
      goToStep(currentStepIndex - 1)
    }
  }, [currentStepIndex, goToStep, pause])

  // Next step
  const nextStep = useCallback(() => {
    if (currentStepIndex < totalSteps - 1) {
      pause()
      goToStep(currentStepIndex + 1)
    }
  }, [currentStepIndex, totalSteps, goToStep, pause])

  // Auto-start if enabled - reset when autoStart changes
  useEffect(() => {
    // Reset if autoStart changes from true to false or vice versa
    if (autoStartRef.current !== autoStart) {
      autoStartRef.current = autoStart
      hasAutoStartedRef.current = false
      if (!autoStart) {
        // Reset execution if autoStart is disabled
        initializeSteps()
      }
    }
  }, [autoStart, initializeSteps])
  
  // FIX #1: Reset hasAutoStartedRef when totalSteps changes from 0 to > 0
  // This handles the race condition where nodes load after state machine initializes
  const prevTotalStepsRef = useRef(0)
  useEffect(() => {
    if (prevTotalStepsRef.current === 0 && totalSteps > 0) {
      console.log('[StateMachine] NODES_LOADED', { totalSteps, autoStart, hasAutoStarted: hasAutoStartedRef.current })
      // Nodes just loaded - reset auto-start flag to allow auto-start to trigger
      hasAutoStartedRef.current = false
    }
    prevTotalStepsRef.current = totalSteps
  }, [totalSteps, autoStart])
  
  useEffect(() => {
    if (autoStart && !hasAutoStartedRef.current && executionState === 'IDLE' && totalSteps > 0) {
      hasAutoStartedRef.current = true
      const delay = prefersReducedMotion.current ? 100 : 400
      console.log('[StateMachine] AUTO_START_TRIGGERED', { totalSteps, delay })
      const timer = setTimeout(() => {
        startExecution()
      }, delay)
      return () => clearTimeout(timer)
    }
  }, [autoStart, executionState, totalSteps, startExecution])

  // Auto-advance effect - SINGLE TIMER OWNER
  // Handles both STEP_RUNNING → STEP_COMPLETED and STEP_COMPLETED → STEP_RUNNING transitions
  // FIX #4: Single cleanup function - React only runs one cleanup per effect
  useEffect(() => {
    let timeoutId = null
    
    // Handle STEP_COMPLETED → advance to next step
    if (executionState === 'STEP_COMPLETED' && isPlayingRef.current && currentStepIndex >= 0) {
      // FORCE: Strict 2-second delay between execution steps
      const delay = 2000
      const stepIdx = currentStepIndex // Capture current value to avoid stale closure
      console.log('[StateMachine] SCHEDULING_ADVANCE_FROM_COMPLETED', { delay, stepIdx, totalSteps, message: 'STRICT_2_SEC_DELAY' })
      
      // Clear any existing timeout first
      if (animationRef.current) {
        clearTimeout(animationRef.current)
        animationRef.current = null
      }
      
      timeoutId = setTimeout(() => {
        console.log('[StateMachine] TIMEOUT_ADVANCE_FIRED', { 
          isPlaying: isPlayingRef.current, 
          stepIdx, 
          totalSteps 
        })
        animationRef.current = null
        
        // Double-check we're still playing (use ref, not state)
        if (isPlayingRef.current) {
          if (stepIdx < totalSteps - 1) {
            advanceStep()
          } else if (stepIdx === totalSteps - 1) {
            // FIX #3: Explicit last-step termination - prevents step-7 freeze
            console.log('[StateMachine] FINISHED_VIA_ADVANCE - last step completed', { stepIdx, totalSteps })
            setExecutionState('EXECUTION_FINISHED')
            setIsPlaying(false)
            isPlayingRef.current = false
          }
        }
      }, delay)
      
      animationRef.current = timeoutId
    }
    
    // Handle STEP_RUNNING → complete step
    if (executionState === 'STEP_RUNNING' && isPlayingRef.current && currentStepIndex >= 0) {
      // FIX #4: Guard against rapid rescheduling - only skip if timer exists AND same step index
      // This prevents stalling when step index changes but timer from previous step still exists
      if (animationRef.current && currentStepIndexRef.current === currentStepIndex) {
        // Timer already scheduled for THIS step - don't reschedule
        console.log('[StateMachine] TIMER_ALREADY_SCHEDULED - skipping reschedule', { stepIndex: currentStepIndex })
        timeoutId = animationRef.current // Use existing timer for cleanup
      } else {
        // New step or no timer - schedule normally
        currentStepIndexRef.current = currentStepIndex
        // CRITICAL FIX: Use ref to get current executionSteps (avoids stale closure)
        const currentStep = executionStepsRef.current?.[currentStepIndex]
        // Check originalStatus (the actual backend status) instead of status
        const stepStatus = currentStep?.data?.originalStatus || currentStep?.data?.status
        
        // Defensive check: if step doesn't exist, skip scheduling
        if (!currentStep) {
          console.warn('[StateMachine] STEP_NOT_FOUND', { currentStepIndex, totalSteps, executionStepsLength: executionStepsRef.current?.length })
          return
        }
        
        console.log('[StateMachine] AUTO_ADVANCE_CHECK', { 
          executionState, 
          isPlaying: isPlayingRef.current, 
          currentStepIndex, 
          stepStatus,
          stepName: currentStep?.data?.stepName 
        })
        
        if (stepStatus === 'SUCCESS') {
          // FORCE: Show step completion for 1 second before marking as completed
          // Then 2-second delay will happen in STEP_COMPLETED → next step transition
          const delay = 1000 // 1 second to show completion animation
          console.log('[StateMachine] SCHEDULING_COMPLETE_SUCCESS', { delay, message: 'STEP_COMPLETION_ANIMATION' })
          timeoutId = setTimeout(() => {
            console.log('[StateMachine] TIMEOUT_COMPLETE_SUCCESS_FIRED')
            animationRef.current = null
            // Double-check we're still playing (use ref, not stale state)
            if (isPlayingRef.current) {
              completeCurrentStep()
            }
          }, delay)
          animationRef.current = timeoutId
        } else if (stepStatus === 'FAILED') {
          // Immediately complete failed steps (no delay for failures)
          console.log('[StateMachine] IMMEDIATE_COMPLETE_FAILED')
          completeCurrentStep()
        } else {
          // If status is not SUCCESS or FAILED, wait 1 second then mark as completed
          // This handles cases where status might be IN_PROGRESS or other states
          const delay = 1000 // 1 second to show completion animation
          console.log('[StateMachine] SCHEDULING_COMPLETE_OTHER', { delay, stepStatus, message: 'STEP_COMPLETION_ANIMATION' })
          timeoutId = setTimeout(() => {
            console.log('[StateMachine] TIMEOUT_COMPLETE_OTHER_FIRED')
            animationRef.current = null
            // Double-check we're still playing (use ref, not stale state)
            if (isPlayingRef.current) {
              completeCurrentStep()
            }
          }, delay)
          animationRef.current = timeoutId
        }
      }
    }
    
    // FIX #4: Single cleanup function for entire effect
    return () => {
      if (timeoutId) {
        console.log('[StateMachine] CLEANUP_TIMEOUT', { timeoutId })
        clearTimeout(timeoutId)
        if (animationRef.current === timeoutId) {
          animationRef.current = null
        }
      }
    }
  }, [executionState, currentStepIndex, completeCurrentStep, advanceStep, totalSteps, executionSteps])
  // CRITICAL FIX: Added executionSteps back to dependencies - now memoized so it only changes when nodes actually change
  // This ensures effect re-runs when step data changes, preventing stale closures

  // Get step state - memoize to prevent recreation
  const getStepState = useCallback((stepIndex) => {
    if (stepIndex < 0 || stepIndex >= totalSteps) return 'HIDDEN'
    
    // CRITICAL FIX: If execution is finished, all steps up to and including currentStepIndex are completed
    if (executionState === 'EXECUTION_FINISHED') {
      if (stepIndex <= currentStepIndex && currentStepIndex >= 0) {
        return 'COMPLETED'
      }
      return 'PENDING'
    }
    
    if (stepIndex < currentStepIndex) {
      return 'COMPLETED'
    } else if (stepIndex === currentStepIndex) {
      return executionState === 'STEP_RUNNING' ? 'RUNNING' : 
             executionState === 'STEP_COMPLETED' ? 'COMPLETED' : 'PENDING'
    } else {
      return 'PENDING'
    }
  }, [currentStepIndex, executionState, totalSteps])

  // Memoize return object to prevent unnecessary re-renders
  return useMemo(() => ({
    executionState,
    currentStepIndex,
    isPlaying,
    completedSteps,
    totalSteps,
    startExecution,
    play,
    pause,
    reset,
    previousStep,
    nextStep,
    goToStep,
    getStepState,
  }), [
    executionState,
    currentStepIndex,
    isPlaying,
    completedSteps,
    totalSteps,
    startExecution,
    play,
    pause,
    reset,
    previousStep,
    nextStep,
    goToStep,
    getStepState,
  ])
}
