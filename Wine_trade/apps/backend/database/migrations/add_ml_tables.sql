-- Migration: Add ML and Learning tables
-- Run this after the base schema is applied

-- ML Models table
CREATE TABLE IF NOT EXISTS ml_models (
    id SERIAL PRIMARY KEY,
    model_id TEXT UNIQUE NOT NULL,
    model_type TEXT NOT NULL, -- 'price_prediction', 'risk_scoring'
    model_name TEXT NOT NULL,
    version INTEGER NOT NULL,
    model_path TEXT NOT NULL, -- Path to serialized model file
    training_dataset_hash TEXT NOT NULL,
    training_metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ML Training Runs table
CREATE TABLE IF NOT EXISTS ml_training_runs (
    id SERIAL PRIMARY KEY,
    model_id TEXT NOT NULL REFERENCES ml_models(model_id),
    run_id TEXT UNIQUE NOT NULL,
    dataset_hash TEXT NOT NULL,
    train_size INTEGER NOT NULL,
    validation_size INTEGER NOT NULL,
    metrics JSONB, -- train_accuracy, val_accuracy, etc.
    training_duration_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ML Predictions table (cache)
CREATE TABLE IF NOT EXISTS ml_predictions (
    id SERIAL PRIMARY KEY,
    model_id TEXT NOT NULL REFERENCES ml_models(model_id),
    prediction_key TEXT NOT NULL, -- Hash of input features
    prediction_value REAL NOT NULL,
    confidence_score REAL,
    input_features JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(model_id, prediction_key)
);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_expires ON ml_predictions(expires_at);

-- Learning Metrics table
CREATE TABLE IF NOT EXISTS learning_metrics (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    simulation_id TEXT,
    model_id TEXT NOT NULL REFERENCES ml_models(model_id),
    metric_type TEXT NOT NULL, -- 'roi_calibration', 'risk_calibration', 'bias_by_region'
    expected_value REAL,
    actual_value REAL,
    delta REAL,
    region TEXT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model Evaluations table
CREATE TABLE IF NOT EXISTS model_evaluations (
    id SERIAL PRIMARY KEY,
    model_id TEXT NOT NULL REFERENCES ml_models(model_id),
    evaluation_type TEXT NOT NULL, -- 'calibration_error', 'bias_analysis', 'drift_detection'
    metrics JSONB,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
