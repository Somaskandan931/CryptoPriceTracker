import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

MODEL_PATH = "backend/model/lstm_model.keras"
SCALER_PATH = "backend/model/scaler.pkl"
DATA_PATH = "backend/data/btc.csv"

model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

def predict_price(coin: str):
    df = pd.read_csv(DATA_PATH)

    prices = df["Close"].values.reshape(-1, 1)
    scaled = scaler.transform(prices)

    X = []
    window = 60
    X.append(scaled[-window:])
    X = np.array(X)

    prediction = model.predict(X)
    return scaler.inverse_transform(prediction)[0][0]
