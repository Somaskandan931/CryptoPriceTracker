import shap
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
import os

BASE_MODEL_DIR = "backend/model/models"
BASE_SCALER_DIR = "backend/model/scalers"
BASE_DATA_DIR = "backend/data/data"
WINDOW = 60


def explain_prediction ( coin: str, num_samples: int = 100 ) :
    """
    Generate SHAP values to explain model predictions for a cryptocurrency.

    SHAP (SHapley Additive exPlanations) values show the contribution of each
    input feature to the model's prediction.

    Args:
        coin: Cryptocurrency identifier
        num_samples: Number of background samples for SHAP explainer

    Returns:
        dict: SHAP values and explanation data

    Raises:
        ValueError: If model or data not found
    """
    # Validate paths
    model_path = os.path.join( BASE_MODEL_DIR, coin, "model.keras" )
    scaler_path = os.path.join( BASE_SCALER_DIR, f"{coin}.pkl" )
    data_path = os.path.join( BASE_DATA_DIR, coin, f"{coin}.csv" )

    if not os.path.exists( model_path ) :
        raise ValueError( f"Model not found for '{coin}' at {model_path}" )

    if not os.path.exists( scaler_path ) :
        raise ValueError( f"Scaler not found for '{coin}' at {scaler_path}" )

    if not os.path.exists( data_path ) :
        raise ValueError( f"Data not found for '{coin}' at {data_path}" )

    try :
        # Load model and scaler
        model = load_model( model_path )
        scaler = joblib.load( scaler_path )

        # Load and prepare data
        df = pd.read_csv( data_path )
        prices = df["Close"].values.reshape( -1, 1 )

        if len( prices ) < WINDOW :
            raise ValueError( f"Not enough data for '{coin}'. Need at least {WINDOW} points." )

        # Scale prices
        scaled_prices = scaler.transform( prices )

        # Prepare input for explanation (last window)
        X_explain = scaled_prices[-WINDOW :].reshape( 1, WINDOW, 1 )

        # Create background dataset for SHAP
        # Use a sample of historical windows
        background_data = []
        for i in range( max( 0, len( scaled_prices ) - num_samples - WINDOW ), len( scaled_prices ) - WINDOW ) :
            background_data.append( scaled_prices[i :i + WINDOW] )

        background_data = np.array( background_data )

        # Create SHAP explainer
        explainer = shap.GradientExplainer( model, background_data )

        # Calculate SHAP values
        shap_values = explainer.shap_values( X_explain )

        # Flatten SHAP values for JSON serialization
        shap_values_flat = shap_values[0].flatten().tolist()

        return {
            "coin" : coin,
            "shap_values" : shap_values_flat,
            "window_size" : WINDOW,
            "explanation" : "Positive values indicate features that increase the prediction, negative values decrease it"
        }

    except Exception as e :
        raise ValueError( f"Error generating explanation for '{coin}': {e}" )


def get_feature_importance ( coin: str ) :
    """
    Get aggregated feature importance for a coin.

    Args:
        coin: Cryptocurrency identifier

    Returns:
        dict: Feature importance summary
    """
    try :
        shap_data = explain_prediction( coin )
        shap_values = np.array( shap_data["shap_values"] )

        # Calculate average absolute SHAP value (feature importance)
        avg_importance = np.mean( np.abs( shap_values ) )
        max_importance = np.max( np.abs( shap_values ) )

        return {
            "coin" : coin,
            "avg_importance" : float( avg_importance ),
            "max_importance" : float( max_importance ),
            "most_important_step" : int( np.argmax( np.abs( shap_values ) ) )
        }

    except Exception as e :
        raise ValueError( f"Error calculating feature importance for '{coin}': {e}" )