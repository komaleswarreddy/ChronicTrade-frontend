---
name: Complete Motia TypeScript Migration Plan
overview: ""
todos: []
---

# Complete Motia TypeScript Migration Plan

## Critical Discovery: Python vs TypeScript

The working Motia project uses **TypeScript**, not Python. The current implementation attempts to use Python (`.step.py`), but modern Motia is TypeScript-first. This explains why steps aren't being discovered.

## Architecture Comparison

### Current (Incorrect) Structure

- Python steps (`.step.py`)
- `motia.config.json` (JSON config)
- Python runtime (`python3.11`)
- `requirements.txt` for dependencies
- Manual database connections

### Target (Correct) Structure

- TypeScript steps (`.step.ts`)
- `motia.config.ts` (TypeScript config)
- Node.js runtime (TypeScript compiled)
- `package.json` with `@motiadev/*` packages
- Motia's built-in state management

## Phase 1: Project Structure Migration

### 1.1 Delete Python-Based Files

**Files to DELETE:**

- `apps/motia/steps/*.step.py` (all 6 Python step files)
- `apps/motia/lib/db.py` (replaced by Motia state)
- `apps/motia/lib/auth.py` (handled via FastAPI integration)
- `apps/motia/models/schemas.py` (replaced by TypeScript types)
- `apps/motia/requirements.txt` (not needed for TypeScript)
- `apps/motia/workflows/*.workflow.py` (workflows are implicit in TypeScript)
- `apps/motia/src/` directory (if exists, restructure)
- `apps/motia/venv/` (not needed)
- `apps/motia/python_modules/` (not needed)

### 1.2 Create TypeScript Project Structure

```
apps/motia/
├── src/
│   ├── steps/
│   │   ├── api/          # HTTP API endpoints
│   │   ├── events/        # Event-driven steps
│   │   └── crons/         # Scheduled tasks
│   ├── streams/           # Real-time streams
│   └── types/              # TypeScript type definitions
├── motia.config.ts        # TypeScript config (not JSON)
├── tsconfig.json          # TypeScript compiler config
├── package.json           # Node.js dependencies
└── .env                   # Environment variables
```

### 1.3 Update package.json

**Replace current package.json with:**

```json
{
  "name": "chronoshift-agents",
  "version": "1.0.0",
  "description": "ChronoShift Agentic Intelligence Service using Motia",
  "type": "module",
  "scripts": {
    "postinstall": "motia install",
    "dev": "motia dev",
    "start": "motia start",
    "build": "motia build",
    "generate-types": "motia generate-types"
  },
  "dependencies": {
    "@motiadev/core": "^0.17.9-beta.191",
    "@motiadev/plugin-endpoint": "^0.17.9-beta.191",
    "@motiadev/plugin-logs": "^0.17.9-beta.191",
    "@motiadev/plugin-observability": "^0.17.9-beta.191",
    "@motiadev/plugin-states": "^0.17.9-beta.191",
    "@motiadev/plugin-bullmq": "^0.17.9-beta.191",
    "motia": "^0.17.9-beta.191",
    "psycopg2-binary": "^2.9.9",
    "dotenv": "^16.4.5",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "@motiadev/workbench": "^0.17.9-beta.191",
    "@types/node": "^20.10.0",
    "typescript": "^5.7.3"
  }
}
```

## Phase 2: Configuration Migration

### 2.1 Create motia.config.ts

**Delete `motia.config.json`, create `motia.config.ts`:**

```typescript
import { defineConfig } from '@motiadev/core'
import endpointPlugin from '@motiadev/plugin-endpoint/plugin'
import logsPlugin from '@motiadev/plugin-logs/plugin'
import observabilityPlugin from '@motiadev/plugin-observability/plugin'
import statesPlugin from '@motiadev/plugin-states/plugin'
import bullmqPlugin from '@motiadev/plugin-bullmq/plugin'

export default defineConfig({
  plugins: [observabilityPlugin, statesPlugin, endpointPlugin, logsPlugin, bullmqPlugin],
  app: (app) => {
    // Health check endpoint for FastAPI integration
    app.get('/health', (_req, res) => {
      res.json({ 
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'chronoshift-agents'
      })
    })
  },
})
```

### 2.2 Create tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022"],
    "moduleResolution": "node",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Phase 3: TypeScript Types Definition

### 3.1 Create src/types/index.ts

Define all data structures:

- `PriceDataPoint`
- `FeatureSet`
- `PricePrediction`
- `Recommendation`
- `ArbitrageOpportunity`
- `AgentRun`
- `AgentProposal`
- `AgentEvidence`

**Reference:** `Motia/src/types/index.ts` pattern

## Phase 4: Convert Steps to TypeScript

### 4.1 API Steps (src/steps/api/)

Convert Python steps to TypeScript API handlers:

**ingest_price.step.ts** → `src/steps/api/ingest-price.step.ts`

- Use `ApiRouteConfig` with `type: 'api'`
- Handler receives `req` object
- Use Motia state instead of direct DB queries
- Return `{ status, body }` response

**get-proposals.step.ts** → `src/steps/api/get-proposals.step.ts`

- GET endpoint for user-scoped proposals
- Query from Motia state or PostgreSQL via helper

**trigger-analysis.step.ts** → `src/steps/api/trigger-analysis.step.ts`

- POST endpoint to trigger agent workflow
- Emits event to start workflow

### 4.2 Event Steps (src/steps/events/)

Convert workflow steps to event handlers:

**features-gen.step.ts** → `src/steps/events/generate-features.step.ts`

- Subscribes to `price.ingested` event
- Computes features (volatility, momentum, etc.)
- Stores in Motia state
- Emits `features.generated` event

**predict-price.step.ts** → `src/steps/events/predict-price.step.ts`

- Subscribes to `features.generated`
- Uses ML model (Prophet/XGBoost via Python bridge or JS library)
- Stores predictions in state
- Emits `price.predicted` event

**recommend-price.step.ts** → `src/steps/events/recommend-price.step.ts`

- Subscribes to `price.predicted`
- Generates BUY/HOLD/SELL recommendation
- Stores in `agent_proposals` table
- Emits `recommendation.generated` event

**arbitrage-score.step.ts** → `src/steps/events/arbitrage-score.step.ts`

- Subscribes to `price.predicted`
- Analyzes cross-region opportunities
- Stores arbitrage proposals

**compliance-check.step.ts** → `src/steps/events/compliance-check.step.ts`

- Subscribes to `recommendation.generated`
- Validates against rules
- Updates proposal status

### 4.3 Step Pattern (Reference Implementation)

Each step follows this pattern:

```typescript
import { ApiRouteConfig, Handlers } from 'motia';
import type { YourType } from '../../types/index.js';

export const config: ApiRouteConfig = {
  name: 'StepName',
  type: 'api', // or 'event', 'cron'
  path: '/your-path',
  method: 'POST', // for API steps
  emits: ['event.name'], // events this step emits
  flows: ['workflow-name']
};

export const handler: Handlers['StepName'] = async (input, { emit, state, streams, logger, traceId }) => {
  // Implementation
};
```

## Phase 5: Database Integration

### 5.1 PostgreSQL Helper Module

Create `src/lib/db.ts` for direct PostgreSQL access when needed:

- Use `psycopg2-binary` via Node.js bridge OR
- Use `pg` (node-postgres) library
- Connection pooling
- Parameterized queries

### 5.2 Motia State vs PostgreSQL

- **Use Motia State for:**
  - Workflow state
  - Temporary data
  - Real-time updates

- **Use PostgreSQL for:**
  - Persistent agent runs (`agent_runs` table)
  - Agent proposals (`agent_proposals` table)
  - Evidence (`agent_evidence` table)
  - Features cache (`features_cache` table)

## Phase 6: Streams for Real-Time Updates

### 6.1 Create src/streams/agent-updates.stream.ts

Real-time updates for agent workflow progress:

```typescript
import { StreamConfig } from 'motia';
import { z } from 'zod';

export const agentUpdateSchema = z.object({
  runId: z.string(),
  status: z.string(),
  timestamp: z.string(),
  data: z.record(z.any()).optional(),
});

export const config: StreamConfig = {
  name: 'agentUpdates',
  schema: agentUpdateSchema,
};
```

## Phase 7: FastAPI Integration

### 7.1 Update FastAPI Endpoints

Modify `apps/backend/main.py`:

- Keep existing `/api/agents/*` endpoints
- Change to call Motia HTTP API (port 4001) instead of direct Python
- Use `httpx` or `requests` to call Motia endpoints
- Pass Clerk JWT in headers for user context

### 7.2 Motia Endpoints

- `POST /internal/ingest-price` - Trigger price ingestion
- `GET /internal/proposals?userId=...` - Get user proposals
- `POST /internal/trigger-analysis` - Start agent workflow

## Phase 8: Installation & Verification

### 8.1 Clean Install

```powershell
cd apps/motia
Remove-Item -Recurse -Force node_modules, dist, .motia -ErrorAction SilentlyContinue
npm install
```

### 8.2 Verify Step Discovery

```powershell
npm run build
# Should show: "✓ Discovered N steps"
```

### 8.3 Start Development Server

```powershell
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/wine_trade"
npm run dev
# Should show: "Motia dev server running on port 4001"
```

## Phase 9: Migration Checklist

### Files to Delete

- [ ] All `.step.py` files
- [ ] `motia.config.json`
- [ ] `requirements.txt`
- [ ] `lib/db.py`, `lib/auth.py`
- [ ] `models/schemas.py`
- [ ] `workflows/*.workflow.py`
- [ ] `src/` directory (restructure)
- [ ] `venv/`, `python_modules/`

### Files to Create

- [ ] `motia.config.ts`
- [ ] `tsconfig.json`
- [ ] `src/types/index.ts`
- [ ] `src/steps/api/*.step.ts` (3-4 files)
- [ ] `src/steps/events/*.step.ts` (5-6 files)
- [ ] `src/streams/agent-updates.stream.ts`
- [ ] `src/lib/db.ts` (if needed)

### Configuration Updates

- [ ] Update `package.json` with correct dependencies
- [ ] Add `postinstall` script
- [ ] Update `.env` with correct variables
- [ ] Update FastAPI to call Motia HTTP API

## Key Differences Summary

| Aspect | Python (Current) | TypeScript (Target) |

|--------|------------------|---------------------|

| Step Files | `.step.py` | `.step.ts` |

| Config | `motia.config.json` | `motia.config.ts` |

| Runtime | Python 3.11 | Node.js (TypeScript) |

| Dependencies | `requirements.txt` | `package.json` |

| State | Direct DB queries | Motia state API |

| Types | Python dataclasses | TypeScript interfaces |

| Discovery | Manual | Auto via TypeScript |

## Critical Notes

1. **No Python Steps**: Motia's modern architecture is TypeScript-first
2. **State Management**: Use Motia's built-in state, not direct DB access
3. **Event-Driven**: Steps communicate via events, not direct calls
4. **Type Safety**: TypeScript provides compile-time type checking
5. **Auto-Discovery**: Steps are automatically discovered from `src/steps/`
6. **FastAPI Integration**: FastAPI calls Motia via HTTP, not Python imports

## Success Criteria

- [ ] `npm run build` discovers all steps
- [ ] `npm run dev` starts without errors
- [ ] Steps are accessible via HTTP endpoints
- [ ] Events trigger correctly
- [ ] FastAPI can call Motia endpoints
- [ ] Agent workflow executes end-to-end
- [ ] Real-time updates work via streams