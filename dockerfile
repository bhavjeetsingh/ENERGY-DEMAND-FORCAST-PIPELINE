# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install necessary Linux packages specifically for compiling dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies required for XGBoost, MLflow, and FastAPI
RUN pip install --no-cache-dir -r requirements.txt

# Copy the core code (src, app) and trained models (mlruns) into the container
COPY ./app ./app
COPY ./src ./src
# Warning: Ensure the mlruns directory is populated properly or MLFLOW_TRACKING_URI is set
COPY ./notebook/mlruns /app/mlruns

# Set MLflow environment variable to point to the local mlruns folder 
# This lets MLflow load the "energy-demand-forecaster" from the registered models
ENV MLFLOW_TRACKING_URI=file:///app/mlruns

# Expose the specific port the FastAPI application runs on
EXPOSE 8000

# Command to run the FastApi server using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
