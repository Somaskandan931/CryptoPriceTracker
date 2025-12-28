import joblib
import os

ENCODER_PATH = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/trained_models/encoders/encoder.pkl"
DATA_DIR = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/data"


def add_metals_to_encoder () :
    """
    Add gold and silver to the existing coin encoder
    """

    print( "Loading existing encoder..." )

    # Load existing encoder
    if os.path.exists( ENCODER_PATH ) :
        coin_encoder = joblib.load( ENCODER_PATH )
        print( f"✅ Loaded encoder with {len( coin_encoder )} coins" )
    else :
        print( "⚠️ Encoder not found, creating new one" )
        coin_encoder = {}

    # Get current max index
    max_index = max( coin_encoder.values() ) if coin_encoder else -1

    # Add gold and silver if they have data
    metals_to_add = []

    for metal in ['gold', 'silver'] :
        data_path = os.path.join( DATA_DIR, metal, f"{metal}.csv" )

        if os.path.exists( data_path ) :
            if metal not in coin_encoder :
                max_index += 1
                coin_encoder[metal] = max_index
                metals_to_add.append( metal )
                print( f"✅ Added {metal} with index {max_index}" )
            else :
                print( f"⚠️ {metal} already in encoder" )
        else :
            print( f"❌ No data found for {metal} at {data_path}" )

    # Save updated encoder
    if metals_to_add :
        os.makedirs( os.path.dirname( ENCODER_PATH ), exist_ok=True )
        joblib.dump( coin_encoder, ENCODER_PATH )
        print( f"\n✅ Encoder updated and saved" )
        print( f"Total coins: {len( coin_encoder )}" )
        print( f"New additions: {', '.join( metals_to_add )}" )
    else :
        print( "\nNo changes made to encoder" )

    return coin_encoder


if __name__ == "__main__" :
    print( "=" * 60 )
    print( "🔧 UPDATING ENCODER WITH PRECIOUS METALS" )
    print( "=" * 60 )

    encoder = add_metals_to_encoder()

    print( "\n" + "=" * 60 )
    print( "📋 CURRENT ENCODER CONTENTS" )
    print( "=" * 60 )

    # Show all coins including metals
    for coin, idx in sorted( encoder.items(), key=lambda x : x[1] ) :
        print( f"{idx:3d}: {coin}" )