# EXECUTION CANVAS DEEP-DEBUG ANALYSIS

## SECTION A — CURRENT EXECUTION FLOW (TEXT DIAGRAM)

```
INITIAL STATE:
  executionState: 'IDLE'
  currentStepIndex: -1
  isPlaying: false
  completedSteps: Set()
  animationRef: null

AUTO-START FLOW (if autoStart=true):
  IDLE
    ↓ (useEffect line 222: setTimeout 400ms)
  EXECUTION_STARTED (currentStepIndex=0, isPlaying=true)
    ↓ (startExecution line 54: setTimeout 50ms)
  STEP_RUNNING (currentStepIndex=0)
    ↓ (auto-advance effect line 259: setTimeout 800ms)
  STEP_COMPLETED (completeCurrentStep called)
    ↓ (completeCurrentStep line 115: setTimeout 800ms) [DOUBLE-SCHEDULING!]
  STEP_RUNNING (currentStepIndex=1, advanceStep called)
    ↓ (repeat...)
  EXECUTION_FINISHED (all steps done)

MANUAL NAVIGATION FLOW:
  User clicks Next/Previous
    ↓ (nextStep/previousStep line 202/194)
  pause() called (clears timer, sets isPlaying=false)
    ↓
  goToStep(index) called
    ↓ (goToStep line 138)
  Timer cleared, currentStepIndex set, executionState='STEP_RUNNING'
    ↓
  BUT: isPlayingRef might be stale if pause() didn't sync

REPLAY FLOW:
  User clicks Replay
    ↓ (reset line 185)
  Timer cleared, initializeSteps() called
    ↓ (initializeSteps line 33)
  All state reset to initial
    ↓
  BUT: isPlayingRef.current not reset (line 40 missing)
  BUT: Nodes might not update if already at IDLE/-1
```

## SECTION B — ROOT CAUSES (FILE + LINE NUMBERS)

### ROOT CAUSE 1: Double-Scheduled Timers (Race Condition)
**File:** `apps/frontend/components/hooks/useExecutionStateMachine.js`
**Lines:** 235-291 (auto-advance effect) AND 83-135 (completeCurrentStep)

**Problem:**
- Auto-advance effect (line 259) schedules `completeCurrentStep()` after 800ms
- `completeCurrentStep()` (line 115) schedules `advanceStep()` after another 800ms
- Both timers use `animationRef.current`, causing ownership conflict
- If auto-advance effect cleanup runs (line 284-289), it cancels the timer from `completeCurrentStep`

**Evidence:**
```javascript
// Line 259: Auto-advance schedules completion
animationRef.current = setTimeout(() => {
  completeCurrentStep()  // This schedules ANOTHER timeout at line 115
}, delay)

// Line 115: completeCurrentStep schedules next step
animationRef.current = setTimeout(() => {
  advanceStep()
}, delay)
```

### ROOT CAUSE 2: Timer Cleanup Race Condition
**File:** `apps/frontend/components/hooks/useExecutionStateMachine.js`
**Lines:** 284-290 (auto-advance effect cleanup)

**Problem:**
- Auto-advance effect cleanup runs on EVERY dependency change
- This can cancel timers scheduled by `completeCurrentStep`
- Creates race between effect re-run and timer completion

**Evidence:**
```javascript
// Line 284-289: Cleanup runs on dependency change
return () => {
  if (animationRef.current) {
    clearTimeout(animationRef.current)  // Cancels timer from completeCurrentStep!
    animationRef.current = null
  }
}
```

### ROOT CAUSE 3: goToStep Doesn't Pause Auto-Run
**File:** `apps/frontend/components/hooks/useExecutionStateMachine.js`
**Lines:** 137-158 (goToStep function)

**Problem:**
- `goToStep` clears timer but doesn't set `isPlaying=false` or `isPlayingRef.current=false`
- `nextStep`/`previousStep` call `pause()` first, but `goToStep` itself doesn't ensure pause
- If `goToStep` is called directly, auto-run continues

**Evidence:**
```javascript
// Line 138-157: goToStep clears timer but doesn't pause
const goToStep = useCallback((index) => {
  if (animationRef.current) {
    clearTimeout(animationRef.current)  // Clears timer
    animationRef.current = null
  }
  // Missing: setIsPlaying(false) and isPlayingRef.current = false
  setCurrentStepIndex(index)
  setExecutionState('STEP_RUNNING')
}, [totalSteps])
```

### ROOT CAUSE 4: initializeSteps Doesn't Reset isPlayingRef
**File:** `apps/frontend/components/hooks/useExecutionStateMachine.js`
**Lines:** 33-43 (initializeSteps function)

**Problem:**
- `initializeSteps` sets `isPlaying=false` but doesn't update `isPlayingRef.current`
- After reset, ref might be stale, causing auto-advance to continue

**Evidence:**
```javascript
// Line 40: Sets state but not ref
setIsPlaying(false)
// Missing: isPlayingRef.current = false
```

### ROOT CAUSE 5: Node Reset Detection Misses Same-State Reset
**File:** `apps/frontend/components/ExecutionCanvas.js`
**Lines:** 209-283 (node update effect)

**Problem:**
- Effect only runs when `currentStepIndex` or `executionState` changes
- If reset happens when already at `IDLE`/`-1`, no change detected
- Nodes keep old `visualStatus`

**Evidence:**
```javascript
// Line 210-215: Only updates on change
const stepIndexChanged = prevStepIndexRef.current !== executionState.currentStepIndex
const executionStateChanged = prevExecutionStateRef.current !== executionState.executionState
// If reset from step 5 to -1, this triggers
// But if already at -1, no change detected
```

### ROOT CAUSE 6: startExecution Uses setTimeout Without Cleanup
**File:** `apps/frontend/components/hooks/useExecutionStateMachine.js`
**Lines:** 46-59 (startExecution function)

**Problem:**
- `startExecution` schedules a setTimeout (line 54) but doesn't store it in `animationRef`
- If `startExecution` is called multiple times, multiple timers run
- No cleanup mechanism

**Evidence:**
```javascript
// Line 54: setTimeout not stored in animationRef
setTimeout(() => {
  setExecutionState('STEP_RUNNING')
}, 50)
```

## SECTION C — FINAL CANONICAL EXECUTION MODEL

### State Definitions
```typescript
executionState: 'IDLE' | 'EXECUTION_STARTED' | 'STEP_RUNNING' | 'STEP_COMPLETED' | 'EXECUTION_FINISHED'
currentStepIndex: number (-1 = no step, 0+ = active step)
isPlaying: boolean (true = auto-run active, false = paused/manual)
completedSteps: Set<number> (indices of completed steps)
animationRef: { current: NodeJS.Timeout | null } (SINGLE timer owner)
```

### Transition Rules

**RULE 1: Single Timer Owner**
- Only the auto-advance effect (lines 235-291) may schedule timers
- All timers must use `animationRef.current`
- All timer scheduling must go through the auto-advance effect

**RULE 2: Single Transition Loop**
```
STEP_RUNNING (stepIndex=N)
  ↓ (auto-advance effect: check stepStatus, schedule completion)
  [timeout 800ms]
  ↓
STEP_COMPLETED (stepIndex=N)
  ↓ (auto-advance effect: schedule advance)
  [timeout 800ms]
  ↓
STEP_RUNNING (stepIndex=N+1)
```

**RULE 3: Manual Navigation Override**
- `goToStep` must:
  1. Clear timer
  2. Set `isPlaying=false`
  3. Set `isPlayingRef.current=false`
  4. Update state

**RULE 4: Reset Invariant**
- `reset()` must leave system identical to fresh load
- All refs must be reset
- All state must be reset
- Nodes must be forced to PENDING

## SECTION D — SURGICAL CODE FIXES

### FIX 1: Remove Double-Scheduling from completeCurrentStep
**File:** `apps/frontend/components/hooks/useExecutionStateMachine.js`
**Lines:** 83-135

**Change:**
- Remove setTimeout from `completeCurrentStep` (lines 111-131)
- Let auto-advance effect handle STEP_COMPLETED → STEP_RUNNING transition

### FIX 2: Consolidate Timer Logic in Auto-Advance Effect
**File:** `apps/frontend/components/hooks/useExecutionStateMachine.js`
**Lines:** 235-291

**Change:**
- Add handling for STEP_COMPLETED state
- Single effect handles both STEP_RUNNING → STEP_COMPLETED and STEP_COMPLETED → STEP_RUNNING
- Remove cleanup that cancels timers from other functions

### FIX 3: Fix goToStep to Pause Auto-Run
**File:** `apps/frontend/components/hooks/useExecutionStateMachine.js`
**Lines:** 137-158

**Change:**
- Add `setIsPlaying(false)` and `isPlayingRef.current = false` before state update

### FIX 4: Fix initializeSteps to Reset Ref
**File:** `apps/frontend/components/hooks/useExecutionStateMachine.js`
**Lines:** 33-43

**Change:**
- Add `isPlayingRef.current = false` after `setIsPlaying(false)`

### FIX 5: Fix startExecution Timer Management
**File:** `apps/frontend/components/hooks/useExecutionStateMachine.js`
**Lines:** 46-59

**Change:**
- Store setTimeout in `animationRef.current` or use a separate ref
- Clear previous timer before scheduling new one

### FIX 6: Force Node Reset Detection
**File:** `apps/frontend/components/ExecutionCanvas.js`
**Lines:** 209-283

**Change:**
- Add detection for reset transition (IDLE state with currentStepIndex === -1)
- Force node update even if state values haven't changed

## SECTION E — WHY THIS IS NOW DETERMINISTIC

### Auto-Run Cannot Stall
- **Single timer owner:** Only auto-advance effect schedules timers, eliminating conflicts
- **Sequential chaining:** STEP_RUNNING → STEP_COMPLETED → STEP_RUNNING(next) is guaranteed
- **No double-scheduling:** Removed nested timeouts that could cancel each other
- **Ref synchronization:** `isPlayingRef` always reflects current state

### Steps Cannot Skip
- **Single transition loop:** All step advances go through same path
- **State machine enforcement:** `advanceStep` only called from auto-advance effect
- **No race conditions:** Timer cleanup doesn't interfere with scheduled transitions

### Manual Navigation Cannot Desync
- **Hard pause:** `goToStep` immediately sets `isPlaying=false` and clears timers
- **State consistency:** Manual navigation sets state synchronously, no async race
- **Visual sync:** Node update effect runs immediately on `currentStepIndex` change

### Replay Always Fully Resets
- **Complete ref reset:** `isPlayingRef.current = false` ensures no stale state
- **Complete state reset:** All state variables reset to initial values
- **Forced node update:** Reset detection ensures nodes update even if state values unchanged
- **Timer cleanup:** All timers cleared before reset

### React Flow Always Re-Renders Correctly
- **New object creation:** Nodes always recreated (no conditional returns)
- **Change detection:** Effect runs on state change OR reset detection
- **VisualStatus derivation:** Always derived from execution state, never stored inconsistently
