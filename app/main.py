from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import mlflow
import uvicorn
import os

# Initialize FastAPI App
app = FastAPI(
    title="India Energy Demand Forecaster API",
    description="Machine Learning REST API for real-time predictions of India's electricity demand (IEX).",
    version="1.0.0"
)

# --- Configuration & Model Loading ---
MODEL_NAME = "energy-demand-forecaster"
STAGE = "production"

try:
    print(f"Loading MLflow model: {MODEL_NAME}...")
    # Optionally load the specific 'production' stage model if managed
    # model_uri = f"models:/{MODEL_NAME}/{STAGE}" 
    # For now, default to the latest version registered
    model_uri = f"models:/{MODEL_NAME}/latest" 
    model = mlflow.pyfunc.load_model(model_uri)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Failed to load model from MLflow: {e}")
    model = None

# --- Data Pydantic Models for Input Validation ---
class PredictionRequest(BaseModel):
    """
    Simulates the required features for the XGBoost model.
    In reality, we would pass raw timestamps and a few variables, and 
    src.features.engineer_features() would compute the lags from a Redis cache or DB.
    """
    # Assuming the most important features passed statically for the example
    hour_of_day: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    month: int = Field(..., ge=1, le=12)
    demand_lag_24h: float = Field(..., description="Electricity demand 24 hours prior (MW)")
    demand_lag_168h: float = Field(..., description="Electricity demand 1 week prior (MW)")
    temp_celsius: float = Field(..., description="Average national temperature proxy")

class PredictionResponse(BaseModel):
    predicted_demand_mw: float
    model_version: str

# --- Endpoints ---

@app.get("/health")
def health_check():
    """Health check endpoint for Docker / Kubernetes probes."""
    return {"status": "ok", "model_loaded": model is not None}

@app.get("/model-info")
def get_model_info():
    """Returns metadata about the active model loaded into memory."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")
    
    return {
        "model_name": MODEL_NAME,
        "input_schema": str(model.metadata.signature) if model.metadata else "Unknown"
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_demand(request: PredictionRequest):
    """
    Accepts historical lag features and calendar information to forecast 
    the next hour's electricity demand in MW.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model is currently unavailable.")
    
    try:
        # 1. Convert incoming JSON request to pandas DataFrame
        input_data = pd.DataFrame([request.model_dump()])
        
        # Note: If passing raw data, you would call your src.features function here
        # e.g.: input_data = engineer_features(input_data)
        
        # 2. Run Inference
        prediction = model.predict(input_data)
        
        return PredictionResponse(
            predicted_demand_mw=round(float(prediction[0]), 2),
            model_version="latest"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

# To run locally: uvicorn app.main:app --host 0.0.0.0 --port 8000
