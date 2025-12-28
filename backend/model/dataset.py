import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
import joblib
from datetime import datetime, timedelta

DATA_DIR = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/data"
SEQ_LEN = 30
SCALER_PATH = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models/scalers/scalar.pkl"
COIN_SCALERS_PATH = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models/scalers/coin_scalers.pkl"
ENCODER_PATH = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models/encoders/encoder.pkl"

# Configuration for handling different asset types
LOOKBACK_DAYS = 730  # Use last 2 years of data (balances recency with sufficient training data)


def load_dataset () :
    """
    Load and preprocess cryptocurrency/commodity data from all available assets.
    Uses per-coin scalers and recent data window to handle assets at all-time highs.

    Returns:
        tuple: (X, y, coin_ids, num_coins)
            - X: Input sequences (samples, seq_len, 1)
            - y: Target values (samples, 1)
            - coin_ids: Coin identifiers for each sample
            - num_coins: Total number of unique coins
    """
    X, y, coin_ids = [], [], []
    coin_to_idx = {}
    coin_scalers = {}  # Separate scaler for each coin/metal
    idx = 0

    if not os.path.exists( DATA_DIR ) :
        raise ValueError( f"Data directory not found: {DATA_DIR}" )

    print( f"📂 Loading data from {DATA_DIR}..." )
    print( f"⏰ Using last {LOOKBACK_DAYS} days of data for training" )

    for coin in os.listdir( DATA_DIR ) :
        path = os.path.join( DATA_DIR, coin, f"{coin}.csv" )

        if not os.path.exists( path ) :
            continue

        try :
            df = pd.read_csv( path )

            # Filter to recent data only (critical for assets at ATH)
            if 'timestamp' in df.columns :
                df['timestamp'] = pd.to_datetime( df['timestamp'] )
                cutoff_date = df['timestamp'].max() - timedelta( days=LOOKBACK_DAYS )
                df = df[df['timestamp'] >= cutoff_date]
                df = df.sort_values( 'timestamp' ).reset_index( drop=True )
            else :
                # If no timestamp column, take most recent rows
                df = df.tail( LOOKBACK_DAYS )

            if len( df ) < SEQ_LEN + 1 :
                print( f"⚠️ Skipping {coin}: insufficient data ({len( df )} rows, need {SEQ_LEN + 1})" )
                continue

            prices = df["Close"].values.reshape( -1, 1 )

            # Create coin-specific scaler using RobustScaler
            # RobustScaler is more robust to outliers and extreme values
            coin_scaler = RobustScaler()
            prices_scaled = coin_scaler.fit_transform( prices )

            # Store the scaler for this specific coin
            coin_scalers[coin] = coin_scaler

            # Map coin to index
            if coin not in coin_to_idx :
                coin_to_idx[coin] = idx
                idx += 1

            # Create sequences
            for i in range( len( prices_scaled ) - SEQ_LEN ) :
                X.append( prices_scaled[i :i + SEQ_LEN] )
                y.append( prices_scaled[i + SEQ_LEN] )
                coin_ids.append( coin_to_idx[coin] )

            # Log price range for debugging
            print( f"✅ {coin}: {len( df )} rows, price range ${prices.min():.2f} - ${prices.max():.2f}, "
                   f"current ${prices[-1][0]:.2f}" )

        except Exception as e :
            print( f"❌ Error loading {coin}: {e}" )
            continue

    if len( X ) == 0 :
        raise ValueError( "No valid data found. Check your data directory." )

    X = np.array( X )
    y = np.array( y )
    coin_ids = np.array( coin_ids )

    print( f"\n✅ Loaded {len( X )} samples from {len( coin_to_idx )} coins" )
    print( f"📊 Coins included: {', '.join( sorted( coin_to_idx.keys() ) )}" )

    # Save coin-specific scalers and encoder
    os.makedirs( os.path.dirname( SCALER_PATH ), exist_ok=True )

    # Save individual coin scalers (PRIMARY - used for predictions)
    joblib.dump( coin_scalers, COIN_SCALERS_PATH )
    print( f"💾 Saved {len( coin_scalers )} coin-specific scalers to {COIN_SCALERS_PATH}" )

    # Also save a global scaler for backward compatibility (but won't be used)
    global_scaler = RobustScaler()
    X_reshaped = X.reshape( -1, 1 )
    global_scaler.fit( X_reshaped )
    joblib.dump( global_scaler, SCALER_PATH )

    # Save encoder
    joblib.dump( coin_to_idx, ENCODER_PATH )
    print( f"💾 Saved encoder with {len( coin_to_idx )} coins" )

    return X, y, coin_ids, len( coin_to_idx )


def get_coin_scaler ( coin: str ) :
    """
    Get the scaler for a specific coin.

    Args:
        coin: Cryptocurrency/commodity identifier

    Returns:
        Scaler object for the specified coin
    """
    if not os.path.exists( COIN_SCALERS_PATH ) :
        raise FileNotFoundError(
            f"Coin scalers not found at {COIN_SCALERS_PATH}. "
            "Please run dataset.py or train_model.py first."
        )

    coin_scalers = joblib.load( COIN_SCALERS_PATH )

    if coin not in coin_scalers :
        raise ValueError(
            f"Scaler for '{coin}' not found. Available: {list( coin_scalers.keys() )}"
        )

    return coin_scalers[coin]


if __name__ == "__main__" :
    print( "=" * 60 )
    print( "📊 LOADING AND PREPROCESSING DATASET" )
    print( "=" * 60 )

    try :
        X, y, coin_ids, num_coins = load_dataset()

        print( "\n" + "=" * 60 )
        print( "✅ DATASET READY" )
        print( "=" * 60 )
        print( f"Samples: {len( X )}" )
        print( f"Coins: {num_coins}" )
        print( f"Input shape: {X.shape}" )
        print( f"Target shape: {y.shape}" )

    except Exception as e :
        print( f"\n❌ Error: {e}" )
        import traceback

        traceback.print_exc()