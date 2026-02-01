# Complete Testing Guide for RAG + ML + Learning Features

This guide provides step-by-step instructions to test all newly implemented features end-to-end.

## Prerequisites

1. **Backend Running**: `cd apps/backend && python start.py`
2. **Frontend Running**: `cd apps/frontend && npm run dev`
3. **Database**: PostgreSQL with schema applied
4. **Authentication**: Sign in to the application

## Feature 1: RAG (Retrieval-Augmented Generation)

### 1.1 Test RAG Document Ingestion

**Backend Test:**
```bash
# Initialize RAG documents
cd apps/backend
python scripts/init_rag_documents.py
```

**Expected Result:**
- Documents ingested into `rag_documents` table
- Chunks created in `rag_chunks` table
- Embeddings generated (if sentence-transformers installed)

**Verify:**
```sql
SELECT COUNT(*) FROM rag_documents;
SELECT COUNT(*) FROM rag_chunks;
```

### 1.2 Test RAG Query via Frontend

1. Navigate to Dashboard
2. Scroll to "RAG Knowledge Query" panel
3. Enter query: "What are the compliance rules for BUY recommendations?"
4. Select source types (optional): `compliance_rule`
5. Set Top K: 5
6. Click "Query RAG System"

**Expected Result:**
- Citations displayed with:
  - Document ID
  - Source type
  - Confidence score
  - Content snippet

### 1.3 Test RAG Query via API

```bash
curl -X POST http://localhost:4000/api/rag/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "query": "What are the risk policies?",
    "source_types": ["risk_policy"],
    "top_k": 5
  }'
```

**Expected Response:**
```json
{
  "citations": [
    {
      "document_id": "...",
      "chunk_index": 0,
      "content": "...",
      "confidence": 0.85,
      "source_type": "risk_policy"
    }
  ],
  "total_results": 5,
  "query_time_ms": 123.45
}
```

### 1.4 Test RAG in Compliance Check

1. Run AI Analysis (click "Run AI Analysis" button)
2. Wait for agent to complete
3. View a proposal's details
4. Check Compliance Evaluation Panel in simulation details
5. Look for "Knowledge Sources" section with citations

**Expected Result:**
- RAG citations appear in compliance evaluation
- Citations link to relevant compliance rules

## Feature 2: ML Models (Price Prediction & Risk Scoring)

### 2.1 View ML Models

1. Navigate to Dashboard
2. Scroll to "Learning Dashboard"
3. Click "ML Models" tab

**Expected Result:**
- List of trained models:
  - Model type (price_prediction or risk_scoring)
  - Model name and version
  - Training metrics (R², MAE, etc.)
  - Active status

### 2.2 Test ML Price Prediction

**API Test:**
```bash
curl -X POST http://localhost:4000/api/ml/predict/price \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "asset_id": "asset_123",
    "current_price": 100.0,
    "region": "Bordeaux",
    "vintage": 2020,
    "market_conditions": {
      "demand_trend": "increasing",
      "supply_level": "normal"
    }
  }'
```

**Expected Response:**
```json
{
  "predicted_price": 105.50,
  "confidence": 0.82,
  "model_id": "price_prediction_v1",
  "prediction_time_ms": 45.2
}
```

### 2.3 Test ML Risk Scoring

**API Test:**
```bash
curl -X POST http://localhost:4000/api/ml/predict/risk \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "asset_id": "asset_123",
    "price_volatility": 0.15,
    "region": "Bordeaux",
    "holding_period_days": 30,
    "market_conditions": {
      "liquidity": "medium",
      "demand_trend": "stable"
    }
  }'
```

**Expected Response:**
```json
{
  "risk_score": 0.35,
  "confidence": 0.78,
  "model_id": "risk_scoring_v1",
  "prediction_time_ms": 38.5
}
```

### 2.4 Verify ML Integration in Agent Proposals

1. Run AI Analysis
2. View proposal details
3. Check for:
   - Expected ROI (from price prediction model)
   - Risk Score (from risk scoring model)
   - Model information in tooltips

**Expected Result:**
- Proposals show ML-predicted values
- Risk scores displayed with color coding (green/yellow/red)

## Feature 3: Learning & Feedback Loop

### 3.1 View Learning Insights

1. Navigate to Dashboard
2. Scroll to "Learning Dashboard"
3. Click "Learning Insights" tab

**Expected Metrics:**
- Overall Calibration Error
- Confidence Calibration (by model component)
- Strategy Performance (by region/strategy)

### 3.2 Test Learning Metrics API

```bash
curl http://localhost:4000/api/learning/metrics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response:**
```json
{
  "overall_calibration_error": 0.12,
  "confidence_calibration": [
    {
      "model_component": "price_prediction",
      "predicted_confidence": 0.85,
      "observed_success_rate": 0.82,
      "calibration_delta": 0.03,
      "sample_size": 150
    }
  ],
  "strategy_performance": [
    {
      "strategy_name": "Bordeaux",
      "avg_expected_roi": 12.5,
      "avg_actual_roi": 11.8,
      "confidence_error": 0.7,
      "sample_size": 45
    }
  ]
}
```

### 3.3 Verify Learning Metrics Update

1. Execute several simulations
2. Record outcomes (sell holdings, track ROI)
3. Wait for metrics calculation
4. Refresh Learning Insights panel

**Expected Result:**
- Metrics update based on actual outcomes
- Calibration errors calculated
- Strategy performance tracked

## Feature 4: End-to-End Integration Test

### 4.1 Complete Workflow

1. **Initialize RAG:**
   ```bash
   python apps/backend/scripts/init_rag_documents.py
   ```

2. **Run AI Analysis:**
   - Click "Run AI Analysis" on dashboard
   - Wait for completion

3. **Verify RAG Citations:**
   - View proposal details
   - Check compliance evaluation
   - Verify citations appear

4. **Verify ML Predictions:**
   - Check Expected ROI (from ML model)
   - Check Risk Score (from ML model)
   - Verify model info in ML Models panel

5. **Test RAG Query:**
   - Use RAG Query Panel
   - Query: "What are compliance rules?"
   - Verify citations returned

6. **Check Learning Metrics:**
   - View Learning Dashboard
   - Verify metrics calculated
   - Check ML model performance

### 4.2 Verify Citations in Multiple Places

**Locations to Check:**
1. ✅ Compliance Evaluation Panel (in simulation details)
2. ✅ AdvisorCard (in proposal details - Knowledge Sources section)
3. ✅ RAG Query Panel (direct query results)

## Feature 5: API Endpoints Verification

### 5.1 RAG Endpoints

```bash
# List documents
curl http://localhost:4000/api/rag/documents \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Query RAG
curl -X POST http://localhost:4000/api/rag/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "test", "top_k": 5}'
```

### 5.2 ML Endpoints

```bash
# List models
curl http://localhost:4000/api/ml/models \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Predict price
curl -X POST http://localhost:4000/api/ml/predict/price \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"asset_id": "test", "current_price": 100}'

# Predict risk
curl -X POST http://localhost:4000/api/ml/predict/risk \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"asset_id": "test", "price_volatility": 0.1}'
```

### 5.3 Learning Endpoints

```bash
# Get metrics
curl http://localhost:4000/api/learning/metrics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Troubleshooting

### RAG Not Working

1. **Check pgvector extension:**
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```
   If not installed, install pgvector on PostgreSQL server.

2. **Check documents ingested:**
   ```sql
   SELECT COUNT(*) FROM rag_documents;
   ```
   If 0, run: `python apps/backend/scripts/init_rag_documents.py`

3. **Check embeddings:**
   ```sql
   SELECT COUNT(*) FROM rag_embeddings;
   ```
   If 0, sentence-transformers may not be installed (fallback mode).

### ML Models Not Showing

1. **Check models table:**
   ```sql
   SELECT * FROM ml_models;
   ```
   If empty, models need to be trained first.

2. **Train models:**
   ```bash
   curl -X POST http://localhost:4000/api/ml/train \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"model_type": "price_prediction"}'
   ```

### Learning Metrics Empty

1. **Check outcomes recorded:**
   ```sql
   SELECT COUNT(*) FROM outcomes;
   ```
   Need outcomes to calculate metrics.

2. **Execute simulations and record outcomes:**
   - Create simulations
   - Execute them
   - Sell holdings to create outcomes
   - Wait for metrics calculation

## Success Criteria

✅ **RAG:**
- Documents can be queried via frontend
- Citations appear in compliance evaluations
- Citations appear in proposal details

✅ **ML:**
- Models visible in ML Models panel
- Price predictions work via API
- Risk scores work via API
- Predictions integrated into agent proposals

✅ **Learning:**
- Learning metrics displayed
- Calibration errors calculated
- Strategy performance tracked
- ML model performance visible

✅ **Integration:**
- All features work together
- Citations appear in multiple places
- ML predictions used in agent decisions
- Learning metrics update based on outcomes

## Next Steps

1. Train initial ML models with historical data
2. Ingest more RAG documents (compliance rules, policies)
3. Execute simulations to generate learning data
4. Monitor learning metrics over time
5. Retrain ML models based on performance
