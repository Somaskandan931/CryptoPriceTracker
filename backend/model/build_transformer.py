import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.layers import (
    Input, Dense, Dropout, LayerNormalization,
    MultiHeadAttention, Embedding, Concatenate
)


def build_transformer ( seq_len: int, num_coins: int, d_model: int = 128,
                        num_heads: int = 4, ff_dim: int = 256,
                        num_transformer_blocks: int = 2, dropout: float = 0.1 ) :
    """
    Build a Transformer model for cryptocurrency price prediction with quantile outputs.

    Architecture:
    - Embedding layer for coin identifiers
    - Transformer blocks with multi-head attention
    - Three output heads for quantile predictions (Q10, Q50, Q90)

    Args:
        seq_len: Length of input sequences
        num_coins: Number of unique cryptocurrencies
        d_model: Dimension of the model (embedding size)
        num_heads: Number of attention heads
        ff_dim: Dimension of feedforward network
        num_transformer_blocks: Number of transformer blocks to stack
        dropout: Dropout rate

    Returns:
        tf.keras.Model: Compiled transformer model
    """

    # Input layers
    price_input = Input( shape=(seq_len, 1), name='price_input' )
    coin_input = Input( shape=(1,), dtype=tf.int32, name='coin_input' )

    # Coin embedding
    coin_embedding = Embedding(
        input_dim=num_coins,
        output_dim=d_model,
        name='coin_embedding'
    )( coin_input )
    coin_embedding = layers.Flatten()( coin_embedding )

    # Project price input to d_model dimensions
    x = Dense( d_model, activation='relu', name='price_projection' )( price_input )

    # Add positional encoding
    positions = tf.range( start=0, limit=seq_len, delta=1 )
    position_embedding = layers.Embedding(
        input_dim=seq_len,
        output_dim=d_model,
        name='position_embedding'
    )( positions )

    x = x + position_embedding

    # Transformer blocks
    for i in range( num_transformer_blocks ) :
        # Multi-head attention
        attention_output = MultiHeadAttention(
            num_heads=num_heads,
            key_dim=d_model // num_heads,
            dropout=dropout,
            name=f'attention_{i}'
        )( x, x )

        attention_output = Dropout( dropout )( attention_output )
        x = LayerNormalization( epsilon=1e-6, name=f'norm1_{i}' )( x + attention_output )

        # Feedforward network
        ffn = tf.keras.Sequential( [
            Dense( ff_dim, activation='relu', name=f'ffn_dense1_{i}' ),
            Dropout( dropout ),
            Dense( d_model, name=f'ffn_dense2_{i}' )
        ], name=f'ffn_{i}' )

        ffn_output = ffn( x )
        ffn_output = Dropout( dropout )( ffn_output )
        x = LayerNormalization( epsilon=1e-6, name=f'norm2_{i}' )( x + ffn_output )

    # Global pooling
    x = layers.GlobalAveragePooling1D( name='global_pooling' )( x )

    # Concatenate with coin embedding
    x = Concatenate( name='concat_features' )( [x, coin_embedding] )

    # Dense layers
    x = Dense( 256, activation='relu', name='dense1' )( x )
    x = Dropout( dropout )( x )
    x = Dense( 128, activation='relu', name='dense2' )( x )
    x = Dropout( dropout )( x )

    # Quantile output heads
    q10_output = Dense( 1, activation='linear', name='q10' )( x )
    q50_output = Dense( 1, activation='linear', name='q50' )( x )
    q90_output = Dense( 1, activation='linear', name='q90' )( x )

    # Build model
    model = Model(
        inputs=[price_input, coin_input],
        outputs=[q10_output, q50_output, q90_output],
        name='crypto_transformer'
    )

    return model


def build_lstm_model ( seq_len: int, num_coins: int, lstm_units: int = 128,
                       dropout: float = 0.2 ) :
    """
    Alternative LSTM model for cryptocurrency price prediction.

    Args:
        seq_len: Length of input sequences
        num_coins: Number of unique cryptocurrencies
        lstm_units: Number of LSTM units
        dropout: Dropout rate

    Returns:
        tf.keras.Model: Compiled LSTM model
    """

    # Input layers
    price_input = Input( shape=(seq_len, 1), name='price_input' )
    coin_input = Input( shape=(1,), dtype=tf.int32, name='coin_input' )

    # Coin embedding
    coin_embedding = Embedding(
        input_dim=num_coins,
        output_dim=64,
        name='coin_embedding'
    )( coin_input )
    coin_embedding = layers.Flatten()( coin_embedding )

    # LSTM layers
    x = layers.LSTM( lstm_units, return_sequences=True, name='lstm1' )( price_input )
    x = Dropout( dropout )( x )
    x = layers.LSTM( lstm_units // 2, name='lstm2' )( x )
    x = Dropout( dropout )( x )

    # Concatenate with coin embedding
    x = Concatenate( name='concat_features' )( [x, coin_embedding] )

    # Dense layers
    x = Dense( 128, activation='relu', name='dense1' )( x )
    x = Dropout( dropout )( x )
    x = Dense( 64, activation='relu', name='dense2' )( x )

    # Quantile output heads
    q10_output = Dense( 1, activation='linear', name='q10' )( x )
    q50_output = Dense( 1, activation='linear', name='q50' )( x )
    q90_output = Dense( 1, activation='linear', name='q90' )( x )

    # Build model
    model = Model(
        inputs=[price_input, coin_input],
        outputs=[q10_output, q50_output, q90_output],
        name='crypto_lstm'
    )

    return model


def build_cnn_lstm_hybrid ( seq_len: int, num_coins: int, dropout: float = 0.2 ) :
    """
    Hybrid CNN-LSTM model for cryptocurrency price prediction.

    Args:
        seq_len: Length of input sequences
        num_coins: Number of unique cryptocurrencies
        dropout: Dropout rate

    Returns:
        tf.keras.Model: Compiled CNN-LSTM model
    """

    # Input layers
    price_input = Input( shape=(seq_len, 1), name='price_input' )
    coin_input = Input( shape=(1,), dtype=tf.int32, name='coin_input' )

    # Coin embedding
    coin_embedding = Embedding(
        input_dim=num_coins,
        output_dim=64,
        name='coin_embedding'
    )( coin_input )
    coin_embedding = layers.Flatten()( coin_embedding )

    # CNN layers for feature extraction
    x = layers.Conv1D( filters=64, kernel_size=3, activation='relu', padding='same' )( price_input )
    x = layers.MaxPooling1D( pool_size=2 )( x )
    x = layers.Conv1D( filters=128, kernel_size=3, activation='relu', padding='same' )( x )
    x = layers.MaxPooling1D( pool_size=2 )( x )

    # LSTM layers for sequence modeling
    x = layers.LSTM( 64, return_sequences=True )( x )
    x = Dropout( dropout )( x )
    x = layers.LSTM( 32 )( x )
    x = Dropout( dropout )( x )

    # Concatenate with coin embedding
    x = Concatenate( name='concat_features' )( [x, coin_embedding] )

    # Dense layers
    x = Dense( 128, activation='relu' )( x )
    x = Dropout( dropout )( x )
    x = Dense( 64, activation='relu' )( x )

    # Quantile output heads
    q10_output = Dense( 1, activation='linear', name='q10' )( x )
    q50_output = Dense( 1, activation='linear', name='q50' )( x )
    q90_output = Dense( 1, activation='linear', name='q90' )( x )

    # Build model
    model = Model(
        inputs=[price_input, coin_input],
        outputs=[q10_output, q50_output, q90_output],
        name='crypto_cnn_lstm'
    )

    return model


if __name__ == "__main__" :
    # Test model creation
    print( "🔨 Building Transformer model..." )
    model = build_transformer( seq_len=30, num_coins=100 )
    print( model.summary() )

    print( "\n" + "=" * 60 )
    print( "✅ Model created successfully!" )
    print( f"Total parameters: {model.count_params():,}" )