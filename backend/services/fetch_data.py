import requests
import pandas as pd
from pathlib import Path

# backend/data/
DATA_DIR = Path(__file__).resolve().parent
DATA_DIR.mkdir(exist_ok=True)

def fetch_crypto_history(coin="bitcoin", days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {"vs_currency": "usd", "days": days}

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    prices = [p[1] for p in data["prices"]]

    df = pd.DataFrame(prices, columns=["Close"])

    file_path = DATA_DIR / f"{coin}.csv"
    df.to_csv(file_path, index=False)

    print(f"✅ Saved historical data for {coin} → {file_path}")

if __name__ == "__main__":
    fetch_crypto_history("bitcoin")
    fetch_crypto_history("ethereum")
