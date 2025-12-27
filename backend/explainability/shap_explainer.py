import shap
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

BASE_MODEL_DIR = "backend/model/models"
BASE_SCALER_DIR = "backend/model/scalers"
BASE_DATA_DIR = "backend/data/data"

def explain_prediction(coin: str):
    model = load_model(f"{BASE_MODEL_DIR}/{coin}/model.keras")
    scaler = joblib.load(f"{BASE_SCALER_DIR}/{coin}.pkl")

    df = pd.read_csv(f"{BASE_DATA_DIR}/{coin}/{coin}.csv")
    prices = df["Close"].values.reshape(-1, 1)
    scaled = scaler.transform(prices)

    window = 60
    X = np.array([scaled[-window:]])

    explainer = shap.GradientExplainer(model, X)
    shap_values = explainer.shap_values(X)

    return {
        "coin": coin,
        "shap_values": shap_values[0].flatten().tolist()
    }
