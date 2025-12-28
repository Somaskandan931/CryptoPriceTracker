import requests
import pandas as pd
import os
import time
from tqdm import tqdm
from datetime import datetime

BASE_URL = "https://api.coingecko.com/api/v3"
DATA_DIR = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/data"
DAYS = 90
REQUEST_DELAY = 2.5  # 30 calls/min = 1 call per 2 seconds (adding buffer)
MAX_RETRIES = 3
RATE_LIMIT_WAIT = 70

# ⭐ GET YOUR FREE API KEY: https://www.coingecko.com/en/api/pricing
# Sign up for Demo plan (free) and paste your key here
API_KEY = "CG-kMFg1WnxXhmw1Wvk68MdR78V"  # Replace with your actual key

# ⭐ CONFIGURATION: Change this to control how many coins to fetch
TOP_N_COINS = 50  # Start with 50 to stay under monthly limit


def get_headers () :
    """Return headers with API key if provided."""
    if API_KEY and API_KEY != "YOUR_API_KEY_HERE" :
        return {"x-cg-demo-api-key" : API_KEY}
    return {}


def get_top_coins_by_market_cap ( limit=50 ) :
    """Fetch top N coins by market capitalization."""
    print( f"🔍 Fetching top {limit} coins by market cap..." )

    try :
        url = f"{BASE_URL}/coins/markets"
        params = {
            "vs_currency" : "usd",
            "order" : "market_cap_desc",
            "per_page" : limit,
            "page" : 1,
            "sparkline" : False
        }

        res = requests.get( url, params=params, headers=get_headers(), timeout=15 )
        res.raise_for_status()

        coins = [coin["id"] for coin in res.json()]
        print( f"✅ Found {len( coins )} top coins" )
        print( f"📊 Preview: {', '.join( coins[:10] )}..." )

        return coins

    except Exception as e :
        print( f"❌ Failed to fetch coin list: {e}" )
        if "401" in str( e ) or "Unauthorized" in str( e ) :
            print( "⚠️ AUTHENTICATION ERROR: Please add your CoinGecko API key!" )
            print( "Get free key at: https://www.coingecko.com/en/api/pricing" )
        return []


def fetch_crypto_history ( coin, days=DAYS ) :
    """Fetch historical price data for a single cryptocurrency."""
    url = f"{BASE_URL}/coins/{coin}/market_chart"
    params = {"vs_currency" : "usd", "days" : days}

    for attempt in range( MAX_RETRIES ) :
        try :
            res = requests.get( url, params=params, headers=get_headers(), timeout=15 )

            # Handle rate limiting
            if res.status_code == 429 :
                print( f"\n⚠️ Rate limit hit ({coin}). Waiting {RATE_LIMIT_WAIT}s..." )
                time.sleep( RATE_LIMIT_WAIT )
                continue

            # Handle authentication errors
            if res.status_code == 401 :
                print( f"\n❌ Authentication failed! Please set your API key." )
                return False

            res.raise_for_status()
            data = res.json()

            if "prices" not in data or len( data["prices"] ) < 10 :
                print( f"\n⚠️ Not enough data for {coin}" )
                return False

            prices = [p[1] for p in data["prices"]]
            df = pd.DataFrame( prices, columns=["Close"] )

            coin_dir = os.path.join( DATA_DIR, coin )
            os.makedirs( coin_dir, exist_ok=True )
            df.to_csv( f"{coin_dir}/{coin}.csv", index=False )

            return True

        except requests.exceptions.RequestException as e :
            if attempt < MAX_RETRIES - 1 :
                wait_time = 10 * (attempt + 1)
                print( f"\n⚠️ Retry {attempt + 1}/{MAX_RETRIES} for {coin} (waiting {wait_time}s)" )
                time.sleep( wait_time )
            else :
                print( f"\n❌ Failed {coin} after {MAX_RETRIES} attempts: {e}" )
                return False
        except Exception as e :
            print( f"\n❌ Unexpected error for {coin}: {e}" )
            return False


def calculate_api_usage ( num_coins ) :
    """Calculate expected API usage."""
    # 1 call for coin list + num_coins calls for history
    total_calls = 1 + num_coins
    monthly_limit = 10000
    remaining = monthly_limit - total_calls

    print( f"\n📊 API Usage Estimate:" )
    print( f"   • This session: {total_calls} calls" )
    print( f"   • Monthly limit: {monthly_limit} calls" )
    print( f"   • Remaining: {remaining} calls" )
    print( f"   • You can fetch ~{remaining // 2} more coins this month" )


if __name__ == "__main__" :
    print( "=" * 60 )
    print( "🚀 CoinGecko Data Fetcher (2025)" )
    print( "=" * 60 )

    # Check API key
    if API_KEY == "YOUR_API_KEY_HERE" :
        print( "\n⚠️ WARNING: No API key set!" )
        print( "📝 Steps to get your FREE API key:" )
        print( "   1. Visit: https://www.coingecko.com/en/api/pricing" )
        print( "   2. Sign up for Demo plan (FREE)" )
        print( "   3. Get your API key from dashboard" )
        print( "   4. Paste it in this script: API_KEY = 'your-key-here'" )
        print( "\n❌ Exiting... Please add your API key first.\n" )
        exit( 1 )

    os.makedirs( DATA_DIR, exist_ok=True )

    # Get top coins
    coins = get_top_coins_by_market_cap( limit=TOP_N_COINS )

    if not coins :
        print( "❌ No coins to fetch. Exiting." )
        exit( 1 )

    # Calculate usage
    calculate_api_usage( len( coins ) )

    # Calculate time
    estimated_time = (len( coins ) * REQUEST_DELAY) / 60
    print( f"\n⏱️ Estimated time: ~{estimated_time:.1f} minutes" )
    print( f"🕐 Start time: {datetime.now().strftime( '%H:%M:%S' )}" )

    # Confirm
    response = input( f"\n▶️ Fetch {len( coins )} coins? (y/n): " )
    if response.lower() != 'y' :
        print( "❌ Cancelled by user" )
        exit( 0 )

    print( f"\n🚀 Starting data fetch...\n" )

    successful = 0
    failed = 0
    failed_coins = []

    for coin in tqdm( coins, desc="Fetching data", unit="coin" ) :
        if fetch_crypto_history( coin ) :
            successful += 1
        else :
            failed += 1
            failed_coins.append( coin )

        time.sleep( REQUEST_DELAY )

    print( "\n" + "=" * 60 )
    print( "✅ Data fetching complete!" )
    print( f"🕐 End time: {datetime.now().strftime( '%H:%M:%S' )}" )
    print( f"📊 Success: {successful} | Failed: {failed} | Total: {len( coins )}" )

    if failed_coins :
        print( f"\n❌ Failed coins: {', '.join( failed_coins[:10] )}" )
        if len( failed_coins ) > 10 :
            print( f"   ... and {len( failed_coins ) - 10} more" )

    print( f"\n💾 Data saved to: {DATA_DIR}/" )
    print( "=" * 60 )

    # Attribution (required by CoinGecko)
    print( "\n📄 Data provided by CoinGecko API" )