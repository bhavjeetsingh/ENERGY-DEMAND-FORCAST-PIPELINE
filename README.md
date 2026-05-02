# ⚡ India Energy Demand Forecaster

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking_&_Registry-0194E2.svg?logo=mlflow)](https://mlflow.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?logo=docker)](https://www.docker.com/)

An end-to-end Machine Learning Operations (MLOps) pipeline that forecasts India's electricity demand (IEX Market Clearing Volume) 24 hours ahead to minimize grid imbalance penalties.

## 🏢 Business Problem
India's grid operators pay ~₹5/kWh in imbalance charges when actual demand deviates from the schedule. At a 180 GW national base load, a **1% forecast error equals a 1,800 MW deviation, costing approximately ₹9 crore per hour**. This API minimizes that error using historical IEX data, calendar effects, and Open-Meteo weather features.

## 🏗️ Architecture
```mermaid
graph LR
    A[(IEX Data)] --> C
    B((Open-Meteo API)) --> C
    C[Feature Pipeline] --> D[XGBoost Training]
    D -- Logs Metrics & Model --> E[(MLflow Registry)]
    E -. Loads Model .-> F[FastAPI Docker Container]
    G[Client Request] --> F
    F --> H{P10 / P50 / P90 Forecast}
    
    classDef blue fill:#3498db,stroke:#2980b9,color:#fff;
    classDef green fill:#2ecc71,stroke:#27ae60,color:#fff;
    class C,D blue;
    class F,H green;

# 1. Clone the repository
git clone [https://github.com/yourusername/energy-demand-forecaster.git](https://github.com/yourusername/energy-demand-forecaster.git)
cd energy-demand-forecaster

# 2. Build and run the containers
docker-compose up --build

Access the UIs:

📖 Interactive API Docs (Swagger): http://localhost:8000/docs

📊 MLflow Tracking Server: http://localhost:5000

curl -X 'POST' \
  '[http://127.0.0.1:8000/predict](http://127.0.0.1:8000/predict)' \
  -H 'Content-Type: application/json' \
  -d '{
  "hour": 14,
  "dow": 2,
  "month": 5,
  "is_holiday": 0,
  "mcv_lag_1h": 3500.5,
  "mcv_lag_24h": 3600.2,
  "mcv_lag_168h": 3400.1,
  "mcp_lag_24h": 4500.0,
  "roll24_mean": 3550.0,
  "roll24_std": 150.0,
  "roll168_mean": 3450.0,
  "temp_c": 32.5,
  "humidity_pct": 60.0,
  "feels_like_c": 35.0
}'

{
  "forecast_mcv_mw": 3415.6,
  "p10_mw": 2410.8,
  "p90_mw": 4420.2,
  "model_version": "1",
  "note": "IEX MCV forecast: 3,416 MW  |  Implied all-India demand: ~38.0 GW"
}

Model,MAPE (%),RMSE (MW),Latency
XGBoost (Production),2.3%,"4,120",18ms
LSTM (2-Layer),2.7%,"4,850",45ms
Prophet,3.8%,"6,840",210ms

📁 Project Structure
├── app/
│   ├── main.py          # FastAPI application
│   └── schema.py        # Pydantic data validation
├── notebook/
│   ├── 01_eda.ipynb     # Data exploration & feature engineering
│   └── 02_modelling.ipynb # Model training & MLflow logging
├── src/
│   ├── features.py      # Core data processing logic
│   └── compare_runs.py  # MLflow metrics extraction
├── tests/
│   └── test_api.py      # Pytest automated API testing
├── Dockerfile           # FastAPI container blueprint
├── docker-compose.yml   # Multi-container orchestration
└── requirements.txt     # Python dependencies