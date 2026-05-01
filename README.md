# 🇮🇳 India Energy Demand Forecaster (IEX Pipeline)

This project is an end-to-end MLOps pipeline for predicting the 24-hour ahead electricity demand in India. It fetches raw meteorological data, engineers temporal lag features, trains robust machine-learning models (XGBoost, Prophet, LSTM) via `MLflow`, and automatically serves the winning model with a high-performance `FastAPI` endpoint.

---

## 1. 🌍 Executive Summary
Accurately predicting India's massive **180+ GW peak electricity demand** is critical for grid stability and minimizing deviation settlement penalties. A 1% forecasting error can cost the grid approximately ₹9 crore/hour in deviation settlements. This pipeline demonstrates how to capture seasonal, daily, and lag behavior from the Indian Energy Exchange (IEX) to minimize error (MAPE) using robust time-series Walk-Forward Validation.

## 2. ⚙️ Technology Stack
The pipeline follows modern Enterprise MLOps architecture:
- **Environment:** `pyenv` + `virtualenv` + `.env`
- **Data Engineering:** `pandas`, `numpy`, `parquet` formats
- **Time-Series Models:** 
  - XGBoost (Tree-based Regression)
  - Prophet (Facebook's additive forecasting)
  - LSTM (TensorFlow Keras Deep Learning)
- **Interpretability:** `SHAP` (Feature summary plots)
- **MLOps / Tracking:** `MLflow` (Metrics, Walk-Forward runs, Model Registry)
- **Serving / Inference:** `FastAPI` + `Pydantic` 
- **Containerization:** `Docker` + `docker-compose.yml`

## 3. 📁 Structure & Reproducibility
* `data/` — Raw CSVs and processed Parquet files ensuring zero data leakage
* `notebook/` 
  * `01_eda.ipynb`: Outlier detection, timezone cleaning, correlation maps, and lag feature construction via `.shift()`.
  * `02_modelling.ipynb`: Walk-Forward validation, XGBoost Baseline, Prophet modeling, LSTM scaling via `MinMaxScaler`, SHAP values, and MLflow logging.
* `src/features.py` — The core logic for `engineer_features()` cleanly extracted from Jupyter for production API usage.
* `app/main.py` — A FastAPI REST API that automatically loads the `"energy-demand-forecaster"` registered in MLflow.
* `Dockerfile` / `docker-compose.yml` — Containerizes both the API and the standalone MLflow UI.

## 4. 🚀 Quickstart Guide
1. **Clone the Repo & Create a Virtual Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Execute the Modeling Pipeline:**
   Walk through `notebook/01_eda.ipynb` and `02_modelling.ipynb` to download the processed data, train XGBoost/Prophet/LSTM, and securely register the winning model to the local `mlruns/` directory using `mlflow`.
3. **Spin up the Model Serving Infrastructure:**
   ```bash
   docker-compose up --build
   ```
4. **Access the Microservices:**
   * **API Docs (Swagger):** `http://localhost:8000/docs`
   * **MLflow Tracking UI:** `http://localhost:5000`

## 5. 🎯 Business Impact & Future Roadmap
* **Financial Impact:** Lowering the baseline MAPE below 4% yields an estimated system savings of ₹20-50 crore weekly by avoiding short-term power-purchase imbalances. 
* **Roadmap Phase 2:**
  - Automated Airflow/Prefect retrain DAG running weekly
  - Deploy Docker container to Azure App Service or AWS ECS
  - Inject real-time weather API integration (AccuWeather/OpenWeather) 
