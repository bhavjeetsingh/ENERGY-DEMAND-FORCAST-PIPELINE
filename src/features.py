import pandas as pd

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply feature engineering to the raw dataset to extract calendar 
    and rolling/lag features, preparing it for ML model predictions.
    This creates features such as 'hour', 'dayofweek', 'month', 
    and time-based lags exactly as they were engineered during EDA.
    """
    df_feat = df.copy()
    
    # Sort chronologically just in case
    if 'timestamp' in df_feat.columns:
        df_feat['timestamp'] = pd.to_datetime(df_feat['timestamp'])
        df_feat = df_feat.sort_values('timestamp').reset_index(drop=True)
        
        # Calendar Features
        df_feat['hour_of_day'] = df_feat['timestamp'].dt.hour
        df_feat['day_of_week'] = df_feat['timestamp'].dt.dayofweek
        df_feat['month'] = df_feat['timestamp'].dt.month
        df_feat['is_weekend'] = df_feat['day_of_week'].isin([5, 6]).astype(int)
        
        # Example of Lag features to be constructed
        # If your EDA notebook constructs other lags (e.g. demand_lag_24h, demand_lag_168h),
        # they must be recreated dynamically here before prediction
        # For a FastAPI endpoint predicting single rows, the API will need to look up historical 
        # mcv_mw values from a database/cache or they must be passed in the request.
        
    return df_feat
