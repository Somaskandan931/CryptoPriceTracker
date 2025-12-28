import os
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf

MODEL_PATH = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models/saved/crypto_transformer.keras"
SCALER_PATH = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models/scalers/coin_scalers.pkl"
ENCODER_PATH = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models/encoders/encoder.pkl"
DATA_DIR = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/data"
SEQ_LEN = 30


def quantile_loss ( q ) :
    """Quantile loss function for model compilation."""

    def loss ( y_true, y_pred ) :
        error = y_true - y_pred
        return tf.reduce_mean( tf.maximum( q * error, (q - 1) * error ) )

    return loss


# Load model and preprocessing artifacts once
try :
    # Load with custom objects for quantile loss
    custom_objects = {
        'quantile_loss' : quantile_loss,
        'loss' : quantile_loss( 0.5 )  # Default loss
    }
    model = tf.keras.models.load_model( MODEL_PATH, custom_objects=custom_objects, compile=False )

    # Recompile with quantile losses
    model.compile(
        optimizer=tf.keras.optimizers.Adam( learning_rate=0.001 ),
        loss={
            "q10" : quantile_loss( 0.1 ),
            "q50" : quantile_loss( 0.5 ),
            "q90" : quantile_loss( 0.9 ),
        }
    )

    scaler = joblib.load( SCALER_PATH )
    asset_encoder = joblib.load( ENCODER_PATH )
    print( "✅ Model and preprocessing artifacts loaded successfully" )
except FileNotFoundError as e :
    print( f"⚠️ File not found: {e}" )
    print( "Please train the model first by running train_model.py" )
    model = None
    scaler = None
    asset_encoder = None
except Exception as e :
    print( f"⚠️ Error loading model artifacts: {e}" )
    model = None
    scaler = None
    asset_encoder = None


def predict_price ( asset: str, days_ahead: int = 1 ) :
    """
    Predict future price for an Indian market asset using quantile regression.

    Args:
        asset: Asset identifier (e.g., 'nifty50', 'reliance', 'gold')
        days_ahead: Number of days into the future to predict (1-30)

    Returns:
        dict: Predictions with q10 (conservative), q50 (expected), q90 (optimistic)

    Raises:
        ValueError: If asset not found or insufficient data
        RuntimeError: If model not loaded
    """
    # Validate model is loaded
    if model is None or scaler is None or asset_encoder is None :
        raise RuntimeError(
            "Model not loaded. Please train the model first by running train_model.py"
        )

    # Validate asset exists
    if asset not in asset_encoder :
        available = list( asset_encoder.keys() )[:10]
        raise ValueError(
            f"Asset '{asset}' not found in trained model. "
            f"Available assets: {available}... (and {len( asset_encoder ) - 10} more)"
        )

    # Validate and clamp days_ahead
    if not isinstance( days_ahead, int ) or days_ahead < 1 :
        days_ahead = 1
    elif days_ahead > 30 :
        days_ahead = 30

    # Load historical data
    path = os.path.join( DATA_DIR, asset, f"{asset}.csv" )
    if not os.path.exists( path ) :
        raise ValueError( f"No historical data available for '{asset}' at {path}" )

    try :
        df = pd.read_csv( path )
        if 'Close' not in df.columns :
            raise ValueError( f"'Close' column not found in data for '{asset}'" )

        prices = df["Close"].values.reshape( -1, 1 )
    except Exception as e :
        raise ValueError( f"Error reading data for '{asset}': {e}" )

    if len( prices ) < SEQ_LEN :
        raise ValueError(
            f"Not enough data for '{asset}'. Need at least {SEQ_LEN} data points, got {len( prices )}"
        )

    # Get asset-specific scaler
    if asset not in scaler :
        raise ValueError(
            f"No scaler found for '{asset}'. Available scalers: {list( scaler.keys() )[:10]}..."
        )

    asset_scaler = scaler[asset]

    # Prepare input
    try :
        prices_scaled = asset_scaler.transform( prices )
    except Exception as e :
        raise ValueError( f"Error scaling prices for '{asset}': {e}" )

    X = prices_scaled[-SEQ_LEN :].reshape( 1, SEQ_LEN, 1 )
    asset_id = np.array( [[asset_encoder[asset]]], dtype=np.int32 )

    # Make prediction
    try :
        predictions = model.predict( [X, asset_id], verbose=0 )
        q10, q50, q90 = predictions
    except Exception as e :
        raise ValueError( f"Prediction failed for '{asset}': {e}" )

    # Inverse transform to original price scale
    try :
        q10 = asset_scaler.inverse_transform( q10.reshape( -1, 1 ) )[0][0]
        q50 = asset_scaler.inverse_transform( q50.reshape( -1, 1 ) )[0][0]
        q90 = asset_scaler.inverse_transform( q90.reshape( -1, 1 ) )[0][0]
    except Exception as e :
        raise ValueError( f"Error inverse transforming predictions for '{asset}': {e}" )

    # Get current price
    current_price = float( prices[-1][0] )

    # Adjust predictions based on days_ahead with bounds checking
    if days_ahead > 1 :
        # Volatility scales with square root of time (standard finance assumption)
        scale_factor = np.sqrt( days_ahead )

        # Cap scale factor to prevent unrealistic predictions
        max_scale = np.sqrt( 30 )  # Maximum reasonable scale
        scale_factor = min( scale_factor, max_scale )

        # Calculate price changes
        q10_change = (q10 - current_price) * scale_factor
        q50_change = (q50 - current_price) * scale_factor
        q90_change = (q90 - current_price) * scale_factor

        # Apply scaled changes
        q10 = current_price + q10_change
        q50 = current_price + q50_change
        q90 = current_price + q90_change

        # Ensure predictions maintain proper ordering and reasonable bounds
        # Predictions should not be negative
        q10 = max( 0.01, q10 )
        q50 = max( 0.01, q50 )
        q90 = max( 0.01, q90 )

        # Ensure proper quantile ordering (q10 < q50 < q90)
        q10 = min( q10, q50 * 0.95 )
        q90 = max( q90, q50 * 1.05 )

        # Prevent extreme predictions (more than 50% change seems unrealistic for most assets)
        max_change_pct = 0.50  # 50% max change
        q10 = max( q10, current_price * (1 - max_change_pct) )
        q90 = min( q90, current_price * (1 + max_change_pct) )

    # Determine currency based on asset type
    currency = "INR"
    if asset in ['gold', 'silver', 'crudeoil'] :
        currency = "USD"
    elif asset in ['usdinr', 'gbpinr', 'eurinr'] :
        currency = "INR per unit"

    return {
        "asset" : asset,
        "q10" : round( float( q10 ), 2 ),
        "q50" : round( float( q50 ), 2 ),
        "q90" : round( float( q90 ), 2 ),
        "current_price" : round( float( current_price ), 2 ),
        "days_ahead" : days_ahead,
        "prediction_range" : round( float( q90 - q10 ), 2 ),
        "currency" : currency
    }


def get_prediction_confidence ( asset: str ) :
    """
    Calculate prediction confidence based on historical volatility.

    Args:
        asset: Asset identifier

    Returns:
        float: Confidence score (0-100)
    """
    path = os.path.join( DATA_DIR, asset, f"{asset}.csv" )

    if not os.path.exists( path ) :
        return None

    try :
        df = pd.read_csv( path )
        if 'Close' not in df.columns :
            return None

        prices = df["Close"].values

        if len( prices ) < 2 :
            return None

        # Calculate volatility
        returns = np.diff( prices ) / prices[:-1]
        volatility = np.std( returns )

        # Higher volatility = lower confidence
        # Normalize to 0-100 scale
        confidence = max( 0, min( 100, 100 * (1 - volatility * 10) ) )

        return round( confidence, 2 )
    except Exception :
        return None


# ============================================================
# TEST PREDICTIONS
# ============================================================
if __name__ == "__main__" :
    print( "\n" + "=" * 60 )
    print( "🇮🇳 TESTING INDIAN MARKET PREDICTIONS" )
    print( "=" * 60 )

    # Check if model is loaded
    if model is None or scaler is None or asset_encoder is None :
        print( "\n❌ Model not loaded. Please run train_model.py first." )
        exit( 1 )

    # Test various Indian market assets
    test_assets = [
        "nifty50",
        "banknifty",
        "reliance",
        "tcs",
        "hdfcbank",
        "gold",
        "usdinr"
    ]

    # Test different time horizons
    test_days = [1, 7, 14, 30]

    print( f"\n📊 Available assets in model: {len( asset_encoder )}" )
    print( f"🎯 Testing {len( test_assets )} assets with {len( test_days )} time horizons\n" )

    success_count = 0
    error_count = 0

    for asset in test_assets :
        try :
            # Determine asset type emoji
            if asset in ['nifty50', 'banknifty', 'sensex'] :
                emoji = "📊"
            elif asset in ['gold', 'silver', 'crudeoil'] :
                emoji = "🥇"
            elif asset in ['usdinr', 'gbpinr', 'eurinr'] :
                emoji = "💱"
            else :
                emoji = "📈"

            print( f"\n{'─' * 60}" )
            print( f"{emoji} {asset.upper()}" )
            print( f"{'─' * 60}" )

            for days in test_days :
                pred = predict_price( asset, days_ahead=days )

                current = pred['current_price']
                expected = pred['q50']
                change_pct = ((expected - current) / current) * 100 if current > 0 else 0
                currency_symbol = "₹" if pred['currency'] == "INR" else "$"

                print( f"\n  📅 {days}-Day Prediction:" )
                print( f"     Current: {currency_symbol}{current:,.2f}" )
                print( f"     Expected: {currency_symbol}{expected:,.2f} ({change_pct:+.2f}%)" )
                print( f"     Range: {currency_symbol}{pred['q10']:,.2f} - {currency_symbol}{pred['q90']:,.2f}" )

            print( f"\n✅ All predictions successful for {asset}" )
            success_count += 1

        except Exception as e :
            print( f"\n❌ Error with {asset}: {e}" )
            error_count += 1
            continue

    print( "\n" + "=" * 60 )
    print( f"✅ Testing complete!" )
    print( f"   Success: {success_count}/{len( test_assets )}" )
    print( f"   Errors: {error_count}/{len( test_assets )}" )
    print( "=" * 60 )