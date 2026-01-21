# MarketIQ India

### AI-Powered Multi-Asset Price Prediction Platform for Indian Markets

MarketIQ India is an **AI-powered price prediction and risk analytics platform** for **Indian stocks, indices, commodities, currencies, and cryptocurrencies**, built using **Transformer-based quantile regression models**.

The system provides **probabilistic forecasts (Q10, Q50, Q90)**, **risk metrics**, and **explainable AI insights**, delivered via a **FastAPI backend** and an **interactive React dashboard**.

---

## Key Highlights

* **Transformer-based deep learning model**
* **Quantile regression** for uncertainty-aware predictions
* **Indian market focus** (NSE stocks, indices, INR pairs)
* **Crypto + commodities support**
* **Risk analytics** (VaR, CVaR, Sharpe, volatility)
* **Explainable AI (SHAP)**
* **Production-ready REST API**
* **Modern React dashboard**

---

## Features

* **AI Price Forecasting**: Transformer model for time-series prediction
* **Probabilistic Outputs**: Q10 / Q50 / Q90 confidence bands
* **Multi-Asset Coverage**:

  * Indian stocks & indices
  * Cryptocurrencies
  * Gold, Silver, Crude Oil
  * Forex (USD/INR, EUR/INR, GBP/INR)
* **Risk Analytics**:

  * Value at Risk (VaR)
  * Conditional VaR (CVaR)
  * Volatility
  * Sharpe Ratio
  * Max Drawdown
* **Explainability**:

  * SHAP-based feature importance
* **Interactive Dashboard**:

  * Charts, confidence intervals, risk views
* **RESTful API**:

  * Prediction, risk, explainability, retraining

---

## System Architecture

```
┌──────────────────┐
│  React Frontend  │
│  (Port: 3000)    │
└────────┬─────────┘
         │ REST API
┌────────▼─────────┐
│ FastAPI Backend  │
│ (Port: 8000)     │
└────────┬─────────┘
         │
 ┌───────▼────────┐
 │ Transformer AI │
 │  Quantile Model│
 └───────┬────────┘
         │
 ┌───────▼────────┐
 │ Market Data    │
 │ APIs & CSVs    │
 └────────────────┘
```

---

## Tech Stack

### Backend

* Python 3.8+
* TensorFlow 2.x
* FastAPI
* Pandas, NumPy, Scikit-learn
* SHAP
* Joblib

### Frontend

* React 18
* Recharts
* Tailwind CSS
* Axios

---

## Data Sources

### Cryptocurrency Data

* **Source**: CoinGecko API
* **Coverage**: Top 50+ cryptocurrencies
* **Data**: OHLCV, historical prices (90 days)
* **Rate Limit**: 10,000 calls/month

```bash
python fetch_data.py
```

---

### Indian Stock Market Data

* **Source**: Yahoo Finance (yfinance)
* **Coverage**:

  * Indices: Nifty 50, Bank Nifty, Sensex
  * Stocks: IT, Banking, Energy, Auto, Pharma, FMCG, Metals
* **Assets**: 45+ NSE-listed stocks

```bash
python fetch_indian_market_data.py
```

---

### Commodities & Precious Metals

* **Source**: Yahoo Finance Futures
* **Assets**:

  * Gold (GC=F)
  * Silver (SI=F)
  * Crude Oil (CL=F)
* **Backup APIs**:

  * Alpha Vantage
  * Twelve Data

```bash
python fetch_metals_data.py
```

---

### Currency Exchange Rates

* **Source**: Yahoo Finance
* **Pairs**:

  * USD/INR
  * EUR/INR
  * GBP/INR

---

## Data Storage Structure

```
backend/data/
├── bitcoin/
│   └── bitcoin.csv
├── ethereum/
├── gold/
├── silver/
├── nifty50/
├── reliance/
└── ... (50+ assets)
```

Each dataset contains:

* `timestamp`
* `Open`
* `High`
* `Low`
* `Close`
* `Volume`

---

## Setup & Installation

### Backend Setup

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

---

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

---

## Complete Data Pipeline

```bash
pip install requests pandas yfinance tqdm joblib

python fetch_data.py
python fetch_indian_market_data.py
python fetch_metals_data.py
python add_metals_to_encoder.py
python verify_data.py
```

---

## Data Verification

```bash
python verify_data.py
```

Checks:

* Data freshness (< 7 days)
* Missing values
* Unrealistic prices
* File integrity

---

## Model Details

### Architecture

* Transformer encoder blocks
* Multi-head attention
* Global pooling
* Three output heads (Q10, Q50, Q90)

### Quantile Loss

```python
def quantile_loss(q):
    def loss(y_true, y_pred):
        error = y_true - y_pred
        return tf.reduce_mean(tf.maximum(q * error, (q - 1) * error))
    return loss
```

### Training Configuration

* Sequence length: 30 days
* Batch size: 256
* Epochs: 20 (early stopping)
* Optimizer: Adam
* Dropout: 0.1

---

## API Endpoints

| Method | Endpoint           | Description      |
| ------ | ------------------ | ---------------- |
| GET    | `/`                | Health check     |
| GET    | `/assets`          | List assets      |
| GET    | `/predict/{asset}` | Price prediction |
| GET    | `/risk/{asset}`    | Risk metrics     |
| GET    | `/explain/{asset}` | SHAP explanation |
| POST   | `/retrain/{asset}` | Retrain asset    |
| POST   | `/retrain-all`     | Retrain model    |

---

## Example API Response

```json
{
  "asset": "RELIANCE",
  "q10": 2480.50,
  "q50": 2552.75,
  "q90": 2631.20,
  "confidence": 81.4
}
```

---

## Deployment

### Backend

* Railway / Render / Heroku

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Frontend

* Vercel / Netlify

```bash
npm run build
```

---

## Important Notes

* Always run `verify_data.py` before training
* Respect CoinGecko rate limits
* Use weekly data refresh for Indian markets
* Reduce batch size if memory issues occur

---

## Acknowledgments

* CoinGecko API
* Yahoo Finance
* TensorFlow
* FastAPI
* React
