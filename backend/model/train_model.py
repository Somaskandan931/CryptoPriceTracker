import tensorflow as tf
import numpy as np
import os
import json

# Import from local modules
from dataset import load_dataset
from build_transformer import build_transformer
from metrics import rmse, mae, mape, r2_score, evaluate_predictions

SEQ_LEN = 30
EPOCHS = 20
BATCH_SIZE = 256
MODEL_PATH = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models/saved/crypto_transformer.keras"
METRICS_PATH = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models/saved/training_metrics.json"


def quantile_loss ( q ) :
    """
    Quantile loss function for probabilistic predictions.

    Args:
        q: Quantile level (e.g., 0.1, 0.5, 0.9)

    Returns:
        Loss function
    """

    def loss ( y_true, y_pred ) :
        error = y_true - y_pred
        return tf.reduce_mean( tf.maximum( q * error, (q - 1) * error ) )

    return loss


def evaluate_model ( model, X, y, coin_ids ) :
    """
    Evaluate model performance on the dataset.

    Args:
        model: Trained model
        X: Input sequences
        y: True values
        coin_ids: Coin identifiers

    Returns:
        dict: Evaluation metrics for each quantile
    """
    print( "\n📊 Evaluating model performance..." )

    # Get predictions - returns a list [q10, q50, q90]
    predictions = model.predict( [X, coin_ids], verbose=0 )

    # Extract predictions from list
    q10_pred = predictions[0].flatten()
    q50_pred = predictions[1].flatten()
    q90_pred = predictions[2].flatten()
    y_true = y.flatten()

    # Calculate metrics for each quantile
    metrics_results = {
        "q10" : evaluate_predictions( y_true, q10_pred ),
        "q50" : evaluate_predictions( y_true, q50_pred ),
        "q90" : evaluate_predictions( y_true, q90_pred )
    }

    # Print results
    print( "\n" + "=" * 60 )
    print( "📈 EVALUATION METRICS" )
    print( "=" * 60 )

    for quantile, metrics in metrics_results.items() :
        print( f"\n{quantile.upper()} (Quantile {quantile[1 :]}):" )
        print( f"   • RMSE: {metrics['rmse']:.4f}" )
        print( f"   • MAE:  {metrics['mae']:.4f}" )
        print( f"   • MAPE: {metrics['mape']:.2f}%" )
        print( f"   • R²:   {metrics['r2']:.4f}" )

    return metrics_results


def calculate_prediction_intervals ( model, X, coin_ids ) :
    """
    Calculate prediction interval statistics.

    Args:
        model: Trained model
        X: Input sequences
        coin_ids: Coin identifiers

    Returns:
        dict: Prediction interval statistics
    """
    predictions = model.predict( [X, coin_ids], verbose=0 )

    # Extract predictions from list [q10, q50, q90]
    q10 = predictions[0].flatten()
    q50 = predictions[1].flatten()
    q90 = predictions[2].flatten()

    # Calculate interval widths
    lower_interval = q50 - q10
    upper_interval = q90 - q50
    total_interval = q90 - q10

    interval_stats = {
        "mean_lower_interval" : float( np.mean( lower_interval ) ),
        "mean_upper_interval" : float( np.mean( upper_interval ) ),
        "mean_total_interval" : float( np.mean( total_interval ) ),
        "median_lower_interval" : float( np.median( lower_interval ) ),
        "median_upper_interval" : float( np.median( upper_interval ) ),
        "median_total_interval" : float( np.median( total_interval ) ),
    }

    print( "\n" + "=" * 60 )
    print( "📏 PREDICTION INTERVAL STATISTICS" )
    print( "=" * 60 )
    print( f"Mean 10-50 interval: {interval_stats['mean_lower_interval']:.4f}" )
    print( f"Mean 50-90 interval: {interval_stats['mean_upper_interval']:.4f}" )
    print( f"Mean 10-90 interval: {interval_stats['mean_total_interval']:.4f}" )

    return interval_stats


def save_training_results ( history, metrics_results, interval_stats ) :
    """
    Save training history and metrics to file.

    Args:
        history: Training history object
        metrics_results: Evaluation metrics
        interval_stats: Prediction interval statistics
    """
    results = {
        "training_history" : {
            "loss" : [float( x ) for x in history.history['loss']],
            "val_loss" : [float( x ) for x in history.history['val_loss']],
            "q10_loss" : [float( x ) for x in history.history['q10_loss']],
            "q50_loss" : [float( x ) for x in history.history['q50_loss']],
            "q90_loss" : [float( x ) for x in history.history['q90_loss']],
        },
        "evaluation_metrics" : metrics_results,
        "prediction_intervals" : interval_stats,
        "model_config" : {
            "seq_len" : SEQ_LEN,
            "epochs" : EPOCHS,
            "batch_size" : BATCH_SIZE,
            "scaler_type" : "coin_specific_robust",
            "lookback_window" : "730_days"
        }
    }

    os.makedirs( os.path.dirname( METRICS_PATH ), exist_ok=True )
    with open( METRICS_PATH, 'w' ) as f :
        json.dump( results, f, indent=2 )

    print( f"\n💾 Training results saved to {METRICS_PATH}" )


def main () :
    print( "=" * 60 )
    print( "🚀 CRYPTO TRANSFORMER TRAINING" )
    print( "=" * 60 )
    print( "\n⚠️ IMPORTANT: Make sure you've run verify_data.py first!" )
    print( "This ensures your data has current prices for gold/silver.\n" )

    # Load dataset
    print( "\n📦 Loading dataset with coin-specific scalers..." )
    try :
        X, y, coin_ids, num_coins = load_dataset()
    except Exception as e :
        print( f"❌ Failed to load dataset: {e}" )
        print( "\nTroubleshooting:" )
        print( "1. Make sure you've fetched data: python fetch_data.py" )
        print( "2. For metals: python fetch_metals_data.py" )
        print( "3. Add metals to encoder: python add_metals_to_encoder.py" )
        print( "4. Verify data: python verify_data.py" )
        return

    print( f"\n📊 Dataset Info:" )
    print( f"   • Coins: {num_coins}" )
    print( f"   • Samples: {len( X )}" )
    print( f"   • Sequence Length: {SEQ_LEN}" )
    print( f"   • Input Shape: {X.shape}" )
    print( f"   • Using: Coin-specific RobustScalers" )
    print( f"   • Training window: Last 730 days per asset" )

    # Build model using the function from build_transformer module
    print( "\n🏗️ Building transformer model..." )
    transformer_model = build_transformer( SEQ_LEN, num_coins )

    print( f"\n📈 Model Architecture:" )
    transformer_model.summary()

    # Compile model
    print( "\n⚙️ Compiling model with quantile losses..." )
    transformer_model.compile(
        optimizer=tf.keras.optimizers.Adam( learning_rate=0.001 ),
        loss={
            "q10" : quantile_loss( 0.1 ),
            "q50" : quantile_loss( 0.5 ),
            "q90" : quantile_loss( 0.9 ),
        },
        metrics={
            "q10" : "mae",
            "q50" : "mae",
            "q90" : "mae",
        }
    )

    # Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='loss',
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1
        ),
        tf.keras.callbacks.ModelCheckpoint(
            MODEL_PATH,
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]

    # Train model
    print( f"\n🎯 Training for {EPOCHS} epochs..." )
    print( "=" * 60 )

    history = transformer_model.fit(
        [X, coin_ids],
        {"q10" : y, "q50" : y, "q90" : y},
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.1,
        callbacks=callbacks,
        verbose=1
    )

    # Evaluate model
    metrics_results = evaluate_model( transformer_model, X, y, coin_ids )

    # Calculate prediction intervals
    interval_stats = calculate_prediction_intervals( transformer_model, X, coin_ids )

    # Save model (if not already saved by ModelCheckpoint)
    print( "\n💾 Saving final model..." )
    os.makedirs( os.path.dirname( MODEL_PATH ), exist_ok=True )
    transformer_model.save( MODEL_PATH )
    print( f"✅ Model saved to {MODEL_PATH}" )

    # Save training results
    save_training_results( history, metrics_results, interval_stats )

    print( "\n" + "=" * 60 )
    print( "🎉 TRAINING COMPLETE!" )
    print( "=" * 60 )
    print( f"\n📁 Outputs:" )
    print( f"   • Model: {MODEL_PATH}" )
    print( f"   • Metrics: {METRICS_PATH}" )
    print( f"   • Scalers: coin_scalers.pkl (coin-specific)" )
    print( f"   • Encoder: encoder.pkl" )

    print( f"\n🧪 Next Steps:" )
    print( f"   1. Test predictions: python predictor.py" )
    print( f"   2. Start API: python main.py" )
    print( f"   3. Check predictions for gold/silver match current prices" )


if __name__ == "__main__" :
    main()