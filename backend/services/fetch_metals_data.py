import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import time


def fetch_with_yfinance_library ( metal='gold', days=1825 ) :
    """
    Fetch using yfinance library (most reliable method)
    Install with: pip install yfinance
    """
    try :
        import yfinance as yf

        symbol_map = {
            'gold' : 'GC=F',  # Gold Futures
            'silver' : 'SI=F'  # Silver Futures
        }

        symbol = symbol_map.get( metal.lower() )

        print( f"Fetching {metal} data using yfinance library..." )

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta( days=days )

        # Download data
        ticker = yf.Ticker( symbol )
        df = ticker.history( start=start_date, end=end_date )

        if df.empty :
            print( f"No data returned for {metal}" )
            return None

        # Reset index to get Date as column
        df = df.reset_index()

        # Rename columns to match crypto format
        df = df.rename( columns={
            'Date' : 'timestamp',
            'Open' : 'Open',
            'High' : 'High',
            'Low' : 'Low',
            'Close' : 'Close',
            'Volume' : 'Volume'
        } )

        # Keep only required columns
        df = df[['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]

        print( f"✅ Fetched {len( df )} records for {metal}" )
        return df

    except ImportError :
        print( "yfinance library not installed. Run: pip install yfinance" )
        return None
    except Exception as e :
        print( f"Error with yfinance: {e}" )
        return None


def fetch_with_alpha_vantage ( metal='gold', api_key='demo' ) :
    """
    Fetch using Alpha Vantage API
    Get free API key from: https://www.alphavantage.co/support/#api-key
    Free tier: 25 requests per day
    """

    print( f"Fetching {metal} data using Alpha Vantage..." )

    # Alpha Vantage commodities functions
    function_map = {
        'gold' : 'XAU',  # Gold in USD
        'silver' : 'XAG'  # Silver in USD
    }

    symbol = function_map.get( metal.lower() )

    url = "https://www.alphavantage.co/query"
    params = {
        'function' : 'FX_DAILY',
        'from_symbol' : symbol,
        'to_symbol' : 'USD',
        'apikey' : api_key,
        'outputsize' : 'full'
    }

    try :
        response = requests.get( url, params=params, timeout=30 )
        data = response.json()

        if 'Time Series FX (Daily)' not in data :
            error_msg = data.get( 'Note', data.get( 'Error Message', 'Unknown error' ) )
            print( f"Alpha Vantage error: {error_msg}" )
            return None

        # Convert to DataFrame
        time_series = data['Time Series FX (Daily)']
        df = pd.DataFrame.from_dict( time_series, orient='index' )

        # Rename columns
        df = df.rename( columns={
            '1. open' : 'Open',
            '2. high' : 'High',
            '3. low' : 'Low',
            '4. close' : 'Close'
        } )

        df['Volume'] = 0  # Volume not available for forex
        df.index = pd.to_datetime( df.index )
        df = df.reset_index().rename( columns={'index' : 'timestamp'} )

        # Convert to numeric
        for col in ['Open', 'High', 'Low', 'Close'] :
            df[col] = pd.to_numeric( df[col] )

        # Sort by date
        df = df.sort_values( 'timestamp' ).reset_index( drop=True )

        print( f"✅ Fetched {len( df )} records for {metal}" )
        return df

    except Exception as e :
        print( f"Error fetching {metal} with Alpha Vantage: {e}" )
        return None


def fetch_with_twelve_data ( metal='gold', api_key='demo' ) :
    """
    Fetch using Twelve Data API
    Get free API key from: https://twelvedata.com/
    Free tier: 800 requests per day
    """

    print( f"Fetching {metal} data using Twelve Data..." )

    symbol_map = {
        'gold' : 'XAU/USD',
        'silver' : 'XAG/USD'
    }

    symbol = symbol_map.get( metal.lower() )

    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol' : symbol,
        'interval' : '1day',
        'outputsize' : 5000,
        'apikey' : api_key
    }

    try :
        response = requests.get( url, params=params, timeout=30 )
        data = response.json()

        if 'values' not in data :
            error_msg = data.get( 'message', 'Unknown error' )
            print( f"Twelve Data error: {error_msg}" )
            return None

        # Convert to DataFrame
        df = pd.DataFrame( data['values'] )

        # Rename and convert columns
        df = df.rename( columns={
            'datetime' : 'timestamp',
            'open' : 'Open',
            'high' : 'High',
            'low' : 'Low',
            'close' : 'Close',
            'volume' : 'Volume'
        } )

        df['timestamp'] = pd.to_datetime( df['timestamp'] )

        for col in ['Open', 'High', 'Low', 'Close'] :
            df[col] = pd.to_numeric( df[col] )

        df['Volume'] = 0

        # Sort by date
        df = df.sort_values( 'timestamp' ).reset_index( drop=True )

        print( f"✅ Fetched {len( df )} records for {metal}" )
        return df

    except Exception as e :
        print( f"Error fetching {metal} with Twelve Data: {e}" )
        return None


def create_sample_data ( metal='gold' ) :
    """
    Create sample data for testing (last resort)
    """
    print( f"⚠️ Creating sample data for {metal}" )

    # Base price
    base_prices = {
        'gold' : 2000,
        'silver' : 25
    }

    base_price = base_prices.get( metal.lower(), 100 )

    # Generate 365 days of sample data
    dates = pd.date_range( end=datetime.now(), periods=365, freq='D' )

    # Create realistic-looking data with random walk
    import numpy as np
    np.random.seed( 42 )

    returns = np.random.normal( 0.0002, 0.02, len( dates ) )
    prices = base_price * np.exp( np.cumsum( returns ) )

    df = pd.DataFrame( {
        'timestamp' : dates,
        'Open' : prices * np.random.uniform( 0.99, 1.01, len( dates ) ),
        'High' : prices * np.random.uniform( 1.00, 1.02, len( dates ) ),
        'Low' : prices * np.random.uniform( 0.98, 1.00, len( dates ) ),
        'Close' : prices,
        'Volume' : np.random.randint( 10000, 100000, len( dates ) )
    } )

    return df


def save_metal_data ( metal='gold', output_dir='data', alpha_vantage_key=None, twelve_data_key=None ) :
    """
    Fetch and save metal data with multiple fallback methods

    Args:
        metal: 'gold' or 'silver'
        output_dir: Base directory for data storage
        alpha_vantage_key: Optional Alpha Vantage API key
        twelve_data_key: Optional Twelve Data API key
    """
    print( f"\n{'=' * 60}" )
    print( f"📊 FETCHING {metal.upper()} DATA" )
    print( f"{'=' * 60}" )

    df = None

    # Try methods in order of preference
    methods = [
        ('yfinance', lambda : fetch_with_yfinance_library( metal )),
    ]

    if alpha_vantage_key :
        methods.append( ('Alpha Vantage', lambda : fetch_with_alpha_vantage( metal, alpha_vantage_key )) )

    if twelve_data_key :
        methods.append( ('Twelve Data', lambda : fetch_with_twelve_data( metal, twelve_data_key )) )

    # Try each method
    for method_name, method_func in methods :
        try :
            print( f"\nTrying {method_name}..." )
            df = method_func()

            if df is not None and not df.empty :
                print( f"✅ Successfully fetched data using {method_name}" )
                break

            # Wait between attempts
            time.sleep( 2 )

        except Exception as e :
            print( f"❌ {method_name} failed: {e}" )
            continue

    # Last resort: create sample data
    if df is None or df.empty :
        print( f"\n⚠️ All methods failed. Creating sample data for testing..." )
        df = create_sample_data( metal )

    # Save to CSV
    metal_dir = os.path.join( output_dir, metal )
    os.makedirs( metal_dir, exist_ok=True )

    output_file = os.path.join( metal_dir, f"{metal}.csv" )
    df.to_csv( output_file, index=False )

    print( f"\n✅ Saved {metal} data: {len( df )} records to {output_file}" )
    print( f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}" )
    print( f"   Price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}" )

    return True


def main () :
    """Fetch both gold and silver data"""

    # Configuration
    DATA_DIR = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/data"

    # Optional: Add your API keys here if you have them
    ALPHA_VANTAGE_KEY = None  # Get from https://www.alphavantage.co/support/#api-key
    TWELVE_DATA_KEY = None  # Get from https://twelvedata.com/

    print( "=" * 60 )
    print( "📊 FETCHING PRECIOUS METALS DATA" )
    print( "=" * 60 )
    print( "\nNote: If yfinance fails, we'll create sample data for testing." )
    print( "For production, consider getting free API keys from:" )
    print( "  • Alpha Vantage: https://www.alphavantage.co/support/#api-key" )
    print( "  • Twelve Data: https://twelvedata.com/" )

    # Fetch Gold
    save_metal_data( 'gold', DATA_DIR, ALPHA_VANTAGE_KEY, TWELVE_DATA_KEY )

    time.sleep( 2 )  # Pause between requests

    # Fetch Silver
    save_metal_data( 'silver', DATA_DIR, ALPHA_VANTAGE_KEY, TWELVE_DATA_KEY )

    print( "\n" + "=" * 60 )
    print( "✅ METALS DATA COLLECTION COMPLETE" )
    print( "=" * 60 )


if __name__ == "__main__" :
    main()