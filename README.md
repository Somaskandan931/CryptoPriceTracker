# MarketIQ India

MarketIQ India is an AI-powered Indian stock market prediction and analytics platform that uses quantile regression–based deep learning models to generate probabilistic price forecasts, expected returns, and risk-aware insights for NSE-listed equities.

The system combines machine learning, financial analytics, and a modern React dashboard to provide traders, analysts, and researchers with transparent, interpretable predictions.
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![React](https://img.shields.io/badge/React-18.x-61dafb.svg)

## Features

- **AI-Powered Predictions**: Transformer-based deep learning model for price forecasting
- **Quantile Regression**: Probabilistic predictions with confidence intervals (Q10, Q50, Q90)
- **Multi-Asset Support**: Predict prices for hundreds of assets
- **Real-Time Data**: Integration with various APIs for live prices
- **Risk Analytics**: VaR, CVaR, Sharpe ratio, and volatility metrics
- **Explainable AI**: SHAP values for model interpretability
- **Interactive Dashboard**: Beautiful React-based UI with charts and visualizations
- **RESTful API**: Fast and scalable FastAPI backend

## Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Port 3000)   │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│  FastAPI Backend│
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│ Model│  │       │
│  AI  │  │  APIs │
└──────┘  └───────┘
```

### Tech Stack

**Backend:**
- Python 3.8+
- TensorFlow 2.x
- FastAPI
- Pandas, NumPy, Scikit-learn
- SHAP for explainability

**Frontend:**
- React 18
- Recharts for visualization
- Tailwind CSS
- Axios for API calls

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn
- 8GB+ RAM (for model training)
- GPU (optional, but recommended for faster training)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Somaskandan931/crypto-prediction-dashboard.git
cd asset-prediction-dashboard
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

**Create `requirements.txt`:**
```txt
tensorflow>=2.10.0
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.2.0
joblib>=1.2.0
requests>=2.28.0
python-multipart>=0.0.6
shap>=0.42.0
tqdm>=4.65.0
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Required packages
npm install recharts axios
```

## Usage

### Step 1: Fetch Historical Data

```bash
# From project root
python backend/data/fetch_data.py
```

⏱️ **Note**: This will take several hours to fetch data for all coins due to API rate limits. Consider modifying the script to fetch only top 100 coins for testing.

### Step 2: Train the Model

```bash
python backend/model/train_model.py
```

**Expected time**: 20-60 minutes depending on data size and hardware.

**Output files:**
- `backend/model/saved/crypto_transformer.keras`
- `backend/model/saved/scaler.pkl`
- `backend/model/saved/coin_encoder.pkl`

### Step 3: Start Backend API

```bash
# Option 1: Direct Python
python backend/main.py

# Option 2: Using Uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

### Step 4: Start Frontend

```bash
# In a new terminal
cd frontend
npm start
```

Dashboard will open at: `http://localhost:3000`

## API Endpoints

### Core Endpoints

| Method | Endpoint             | Description |
|--------|----------------------|-------------|
| GET | `/`                  | Health check |
| GET | `/assets`            | List all available coins |
| GET | `/predict/{assets}`  | Get price predictions |
| GET | `/live/{assets}`       | Get current live price |
| GET | `/risk/{assets}`       | Get risk metrics |
| GET | `/explain/{assets}`    | Get SHAP explanations |
| GET | `/importance/{assets}` | Get feature importance |
| POST | `/retrain/{assets}`    | Retrain model for specific coin |
| POST | `/retrain-all`       | Retrain entire model |




### Example Response

```json
{
  "coin": "bitcoin",
  "q10": 45230.50,
  "q50": 48500.75,
  "q90": 52100.25,
  "current_price": 47800.00,
  "confidence": 78.5
}
```


## Model Details

### Architecture

The system uses a **Transformer-based architecture** with the following components:

1. **Input Layer**: Price sequences (30 timesteps) + coin embeddings
2. **Transformer Blocks**: Multi-head attention with feedforward networks
3. **Pooling Layer**: Global average pooling
4. **Output Heads**: Three separate heads for quantile predictions

### Quantile Regression

The model predicts three quantiles:
- **Q10 (Conservative)**: 10th percentile - pessimistic scenario
- **Q50 (Expected)**: 50th percentile - median prediction
- **Q90 (Optimistic)**: 90th percentile - optimistic scenario

### Loss Function

Custom quantile loss for each output:

```python
def quantile_loss(q):
    def loss(y_true, y_pred):
        error = y_true - y_pred
        return tf.reduce_mean(tf.maximum(q * error, (q - 1) * error))
    return loss
```

### Training Configuration

- **Sequence Length**: 30 days
- **Batch Size**: 256
- **Epochs**: 20 (with early stopping)
- **Optimizer**: Adam (lr=0.001)
- **Regularization**: Dropout (0.1) + Layer Normalization

## Risk Metrics

The system calculates comprehensive risk metrics:

- **VaR (Value at Risk)**: Maximum expected loss at 95% confidence
- **CVaR (Conditional VaR)**: Expected loss beyond VaR threshold
- **Volatility**: Annualized standard deviation of returns
- **Sharpe Ratio**: Risk-adjusted return metric
- **Maximum Drawdown**: Largest peak-to-trough decline

## Configuration

### Modify Data Collection

Edit `backend/data/fetch_data.py`:

```python
# Fetch only top 100 coins
DAYS = 30  # Historical days to fetch
coins = get_all_coin_ids()[:100]  # Limit to 100 coins
```

### Adjust Model Parameters

Edit `backend/model/model.py`:

```python
model = build_transformer(
    seq_len=30,        # Sequence length
    num_coins=100,     # Number of coins
    d_model=128,       # Model dimension
    num_heads=4,       # Attention heads
    ff_dim=256,        # Feedforward dimension
    num_transformer_blocks=2,  # Transformer layers
    dropout=0.1        # Dropout rate
)
```

## Troubleshooting

### Issue: Model not found
```bash
# Solution: Train the model first
python backend/model/train_model.py
```

### Issue: API connection failed
```bash
# Solution: Check if backend is running
curl http://localhost:8000/
```

### Issue: Frontend can't connect
```bash
# Solution: Update API URL in cryptoApi.js
baseURL: "http://localhost:8000"
```

### Issue: Out of memory during training
```python
# Solution: Reduce batch size in train_model.py
BATCH_SIZE = 128  # Instead of 256
```

## Deployment

### Backend (Railway/Heroku)

```bash
# Create Procfile
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Frontend (Vercel/Netlify)

```bash
# Build command
npm run build

# Output directory
build/
```

## Performance

- **Prediction Time**: < 100ms per coin
- **Training Time**: ~30-60 minutes (depends on data size)
- **API Response Time**: < 200ms
- **Model Size**: ~50-100MB


## Acknowledgments

- [CoinGecko API](https://www.coingecko.com/en/api) for cryptocurrency data
- [TensorFlow](https://www.tensorflow.org/) for deep learning framework
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [React](https://reactjs.org/) for the frontend framework
