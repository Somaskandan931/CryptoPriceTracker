import joblib
import os

ENCODER_PATH = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models/encoders/encoder.pkl"
DATA_DIR = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/data"
MODEL_DIR = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models"


def load_coin_encoder () :
    """Load the coin encoders from disk."""
    if not os.path.exists( ENCODER_PATH ) :
        raise FileNotFoundError(
            f"Coin encoders not found at {ENCODER_PATH}. "
            "Please run dataset.py or train_model.py first."
        )

    try :
        return joblib.load( ENCODER_PATH )
    except Exception as e :
        raise ValueError( f"Error loading coin encoders: {e}" )


# Load encoders once at module level
try :
    coin_encoder = load_coin_encoder()
except Exception as e :
    print( f"⚠️ Warning: {e}" )
    coin_encoder = {}


def has_coin_data ( coin: str ) :
    """
    Check if a coin has the necessary data files.

    Args:
        coin: Cryptocurrency identifier

    Returns:
        bool: True if coin has data file
    """
    data_path = os.path.join( DATA_DIR, coin, f"{coin}.csv" )
    return os.path.exists( data_path )


def has_coin_model ( coin: str ) :
    """
    Check if a coin has a trained model.

    Args:
        coin: Cryptocurrency identifier

    Returns:
        bool: True if coin has model file
    """
    model_path = os.path.join( MODEL_DIR, coin, f"{coin}_quantile_model.pkl" )
    return os.path.exists( model_path )


def is_coin_ready ( coin: str ) :
    """
    Check if a coin is fully ready for predictions.
    Requires both encoder entry, data file, and trained model.

    Args:
        coin: Cryptocurrency identifier

    Returns:
        bool: True if coin is ready for predictions
    """
    return (
            coin in coin_encoder and
            has_coin_data( coin ) and
            has_coin_model( coin )
    )


def get_all_coins () :
    """
    Get list of all available cryptocurrency identifiers that are ready for predictions.
    Only returns coins that have both data files and trained models.

    Returns:
        list: Sorted list of coin identifiers that are ready
    """
    if not coin_encoder :
        return []

    # TEMPORARY: Return coins that have at least data files
    # TODO: Change back to is_coin_ready(coin) once models are trained
    coins_with_data = [
        coin for coin in coin_encoder.keys()
        if has_coin_data( coin )
    ]

    return sorted( coins_with_data )


def get_all_coins_in_encoder () :
    """
    Get list of ALL coins in the encoder, regardless of data availability.

    Returns:
        list: Sorted list of all coin identifiers in encoder
    """
    if not coin_encoder :
        return []
    return sorted( list( coin_encoder.keys() ) )


def get_coin_index ( coin: str ) :
    """
    Get the numeric index for a coin.

    Args:
        coin: Cryptocurrency identifier

    Returns:
        int: Numeric index of the coin

    Raises:
        ValueError: If coin not found
    """
    if coin not in coin_encoder :
        raise ValueError( f"Coin '{coin}' not found in encoders" )

    return coin_encoder[coin]


def is_coin_available ( coin: str ) :
    """
    Check if a coin is available in the trained model.

    Args:
        coin: Cryptocurrency identifier

    Returns:
        bool: True if coin is available
    """
    return coin in coin_encoder


def get_coin_status ( coin: str ) :
    """
    Get detailed status information for a coin.

    Args:
        coin: Cryptocurrency identifier

    Returns:
        dict: Status information including what files exist
    """
    return {
        "coin" : coin,
        "in_encoder" : coin in coin_encoder,
        "has_data" : has_coin_data( coin ),
        "has_model" : has_coin_model( coin ),
        "ready" : is_coin_ready( coin )
    }