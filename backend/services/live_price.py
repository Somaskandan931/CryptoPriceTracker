import yfinance as yf
from typing import Optional
import requests

REQUEST_TIMEOUT = 10

# Mapping of internal asset names to Yahoo Finance symbols
SYMBOL_MAP = {
    # Indices
    'nifty50' : '^NSEI',
    'banknifty' : '^NSEBANK',
    'sensex' : '^BSESN',

    # IT Sector
    'tcs' : 'TCS.NS',
    'infosys' : 'INFY.NS',
    'wipro' : 'WIPRO.NS',
    'hcltech' : 'HCLTECH.NS',
    'techm' : 'TECHM.NS',

    # Banking
    'hdfcbank' : 'HDFCBANK.NS',
    'icicibank' : 'ICICIBANK.NS',
    'sbi' : 'SBIN.NS',
    'kotakbank' : 'KOTAKBANK.NS',
    'axisbank' : 'AXISBANK.NS',
    'bajajfinance' : 'BAJFINANCE.NS',

    # Energy
    'reliance' : 'RELIANCE.NS',
    'ongc' : 'ONGC.NS',
    'bpcl' : 'BPCL.NS',
    'ioc' : 'IOC.NS',
    'adanigreen' : 'ADANIGREEN.NS',

    # Automobile
    'maruti' : 'MARUTI.NS',
    'tatamotors' : 'TATAMOTORS.NS',
    'mahindra' : 'M&M.NS',
    'bajajauto' : 'BAJAJ-AUTO.NS',
    'heromotoco' : 'HEROMOTOCO.NS',

    # Pharma
    'sunpharma' : 'SUNPHARMA.NS',
    'drreddy' : 'DRREDDY.NS',
    'cipla' : 'CIPLA.NS',
    'divislab' : 'DIVISLAB.NS',

    # FMCG
    'hul' : 'HINDUNILVR.NS',
    'itc' : 'ITC.NS',
    'nestle' : 'NESTLEIND.NS',
    'britannia' : 'BRITANNIA.NS',

    # Metals
    'tatasteel' : 'TATASTEEL.NS',
    'hindalco' : 'HINDALCO.NS',
    'coalindia' : 'COALINDIA.NS',
    'vedanta' : 'VEDL.NS',

    # Telecom
    'airtel' : 'BHARTIARTL.NS',

    # Cement
    'ultratech' : 'ULTRACEMCO.NS',
    'shreecem' : 'SHREECEM.NS',

    # Power
    'powergrid' : 'POWERGRID.NS',
    'ntpc' : 'NTPC.NS',

    # Adani Group
    'adanient' : 'ADANIENT.NS',
    'adaniports' : 'ADANIPORTS.NS',

    # Others
    'asianpaint' : 'ASIANPAINT.NS',
    'lt' : 'LT.NS',
    'titan' : 'TITAN.NS',

    # Currency
    'usdinr' : 'USDINR=X',
    'gbpinr' : 'GBPINR=X',
    'eurinr' : 'EURINR=X',

    # Commodities
    'gold' : 'GC=F',
    'silver' : 'SI=F',
    'crudeoil' : 'CL=F',
}


def get_live_price ( asset: str ) -> float :
    """
    Fetch the current live price for an Indian market asset.

    Args:
        asset: Asset identifier (e.g., 'nifty50', 'reliance', 'gold')

    Returns:
        float: Current price in INR (or USD for international commodities)

    Raises:
        ValueError: If asset not found or invalid response
    """
    if asset not in SYMBOL_MAP :
        raise ValueError( f"Asset '{asset}' not found. Available assets: {list( SYMBOL_MAP.keys() )[:10]}..." )

    symbol = SYMBOL_MAP[asset]

    try :
        ticker = yf.Ticker( symbol )

        # Try to get the most recent price
        # Method 1: Try fast_info (fastest)
        try :
            price = ticker.fast_info['lastPrice']
            if price and price > 0 :
                return float( price )
        except :
            pass

        # Method 2: Try info dict
        try :
            info = ticker.info
            if 'currentPrice' in info and info['currentPrice'] :
                return float( info['currentPrice'] )
            elif 'regularMarketPrice' in info and info['regularMarketPrice'] :
                return float( info['regularMarketPrice'] )
        except :
            pass

        # Method 3: Get latest data point from history
        hist = ticker.history( period='1d' )
        if not hist.empty :
            return float( hist['Close'].iloc[-1] )

        raise ValueError( f"Could not fetch price for '{asset}'" )

    except Exception as e :
        raise ValueError( f"Error fetching live price for '{asset}': {e}" )


def get_multiple_prices ( assets: list ) -> dict :
    """
    Fetch live prices for multiple Indian market assets.

    Args:
        assets: List of asset identifiers

    Returns:
        dict: Mapping of asset -> price
    """
    if not assets :
        return {}

    prices = {}
    for asset in assets :
        try :
            prices[asset] = get_live_price( asset )
        except Exception as e :
            print( f"Error fetching price for {asset}: {e}" )
            continue

    return prices


def get_market_status () -> dict :
    """
    Check if Indian markets are currently open.

    Returns:
        dict: Market status information
    """
    from datetime import datetime
    import pytz

    ist = pytz.timezone( 'Asia/Kolkata' )
    now = datetime.now( ist )

    # NSE trading hours: 9:15 AM to 3:30 PM IST on weekdays
    is_weekday = now.weekday() < 5  # Monday = 0, Sunday = 6

    market_open = now.time() >= datetime.strptime( "09:15", "%H:%M" ).time()
    market_close = now.time() <= datetime.strptime( "15:30", "%H:%M" ).time()

    is_open = is_weekday and market_open and market_close

    return {
        "is_open" : is_open,
        "current_time" : now.strftime( "%Y-%m-%d %H:%M:%S IST" ),
        "trading_hours" : "9:15 AM - 3:30 PM IST",
        "weekday" : is_weekday,
        "timezone" : "Asia/Kolkata"
    }