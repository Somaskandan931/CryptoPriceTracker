import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import time
import yfinance as yf


def fetch_with_yfinance ( symbol, name, days=1825 ) :
    """
    Fetch Indian market data using yfinance

    Args:
        symbol: Yahoo Finance symbol (e.g., 'RELIANCE.NS')
        name: Display name for the asset
        days: Number of days of historical data
    """
    try :
        print( f"Fetching {name} data using yfinance..." )

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta( days=days )

        # Download data
        ticker = yf.Ticker( symbol )
        df = ticker.history( start=start_date, end=end_date )

        if df.empty :
            print( f"No data returned for {name}" )
            return None

        # Reset index to get Date as column
        df = df.reset_index()

        # Rename columns
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

        print( f"✅ Fetched {len( df )} records for {name}" )
        return df

    except Exception as e :
        print( f"Error fetching {name}: {e}" )
        return None


def save_asset_data ( symbol, name, output_dir='data' ) :
    """
    Fetch and save Indian market asset data

    Args:
        symbol: Yahoo Finance symbol
        name: Asset identifier for file naming
        output_dir: Base directory for data storage
    """
    print( f"\n{'=' * 60}" )
    print( f"📊 FETCHING {name.upper()} DATA" )
    print( f"{'=' * 60}" )

    df = fetch_with_yfinance( symbol, name )

    if df is None or df.empty :
        print( f"⚠️ Failed to fetch data for {name}" )
        return False

    # Save to CSV
    asset_dir = os.path.join( output_dir, name )
    os.makedirs( asset_dir, exist_ok=True )

    output_file = os.path.join( asset_dir, f"{name}.csv" )
    df.to_csv( output_file, index=False )

    print( f"\n✅ Saved {name} data: {len( df )} records to {output_file}" )
    print( f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}" )
    print( f"   Price range: ₹{df['Close'].min():.2f} - ₹{df['Close'].max():.2f}" )

    return True


def main () :
    """Fetch Indian market data"""

    # Configuration
    DATA_DIR = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/data"

    print( "=" * 60 )
    print( "🇮🇳 FETCHING INDIAN MARKET DATA" )
    print( "=" * 60 )

    # Indian Market Assets
    # Format: (Yahoo Symbol, Internal Name, Display Name)
    indian_assets = [
        # Major Indian Indices
        ('^NSEI', 'nifty50', 'Nifty 50'),
        ('^NSEBANK', 'banknifty', 'Bank Nifty'),
        ('^BSESN', 'sensex', 'BSE Sensex'),

        # Top Indian Stocks - IT Sector
        ('TCS.NS', 'tcs', 'TCS'),
        ('INFY.NS', 'infosys', 'Infosys'),
        ('WIPRO.NS', 'wipro', 'Wipro'),
        ('HCLTECH.NS', 'hcltech', 'HCL Technologies'),
        ('TECHM.NS', 'techm', 'Tech Mahindra'),

        # Banking & Financial Services
        ('HDFCBANK.NS', 'hdfcbank', 'HDFC Bank'),
        ('ICICIBANK.NS', 'icicibank', 'ICICI Bank'),
        ('SBIN.NS', 'sbi', 'State Bank of India'),
        ('KOTAKBANK.NS', 'kotakbank', 'Kotak Mahindra Bank'),
        ('AXISBANK.NS', 'axisbank', 'Axis Bank'),
        ('BAJFINANCE.NS', 'bajajfinance', 'Bajaj Finance'),

        # Energy & Oil
        ('RELIANCE.NS', 'reliance', 'Reliance Industries'),
        ('ONGC.NS', 'ongc', 'ONGC'),
        ('BPCL.NS', 'bpcl', 'BPCL'),
        ('IOC.NS', 'ioc', 'Indian Oil'),
        ('ADANIGREEN.NS', 'adanigreen', 'Adani Green Energy'),

        # Automobiles
        ('MARUTI.NS', 'maruti', 'Maruti Suzuki'),
        ('TATAMOTORS.NS', 'tatamotors', 'Tata Motors'),
        ('M&M.NS', 'mahindra', 'Mahindra & Mahindra'),
        ('BAJAJ-AUTO.NS', 'bajajauto', 'Bajaj Auto'),
        ('HEROMOTOCO.NS', 'heromotoco', 'Hero MotoCorp'),

        # Pharma
        ('SUNPHARMA.NS', 'sunpharma', 'Sun Pharma'),
        ('DRREDDY.NS', 'drreddy', 'Dr. Reddy\'s'),
        ('CIPLA.NS', 'cipla', 'Cipla'),
        ('DIVISLAB.NS', 'divislab', 'Divi\'s Laboratories'),

        # FMCG
        ('HINDUNILVR.NS', 'hul', 'Hindustan Unilever'),
        ('ITC.NS', 'itc', 'ITC'),
        ('NESTLEIND.NS', 'nestle', 'Nestle India'),
        ('BRITANNIA.NS', 'britannia', 'Britannia'),

        # Metals & Mining
        ('TATASTEEL.NS', 'tatasteel', 'Tata Steel'),
        ('HINDALCO.NS', 'hindalco', 'Hindalco'),
        ('COALINDIA.NS', 'coalindia', 'Coal India'),
        ('VEDL.NS', 'vedanta', 'Vedanta'),

        # Telecom
        ('BHARTIARTL.NS', 'airtel', 'Bharti Airtel'),

        # Cement
        ('ULTRACEMCO.NS', 'ultratech', 'UltraTech Cement'),
        ('SHREECEM.NS', 'shreecem', 'Shree Cement'),

        # Power
        ('POWERGRID.NS', 'powergrid', 'Power Grid'),
        ('NTPC.NS', 'ntpc', 'NTPC'),

        # Adani Group
        ('ADANIENT.NS', 'adanient', 'Adani Enterprises'),
        ('ADANIPORTS.NS', 'adaniports', 'Adani Ports'),

        # Others
        ('ASIANPAINT.NS', 'asianpaint', 'Asian Paints'),
        ('LT.NS', 'lt', 'Larsen & Toubro'),
        ('TITAN.NS', 'titan', 'Titan Company'),

        # Currency (INR pairs)
        ('USDINR=X', 'usdinr', 'USD/INR'),
        ('GBPINR=X', 'gbpinr', 'GBP/INR'),
        ('EURINR=X', 'eurinr', 'EUR/INR'),

        # Commodities (MCX equivalents via international markets)
        ('GC=F', 'gold', 'Gold'),
        ('SI=F', 'silver', 'Silver'),
        ('CL=F', 'crudeoil', 'Crude Oil'),
    ]

    print( f"\n📋 Total assets to fetch: {len( indian_assets )}" )
    print( f"⏱️ Estimated time: ~{len( indian_assets ) * 2 / 60:.1f} minutes\n" )

    successful = 0
    failed = 0
    failed_assets = []

    for symbol, name, display_name in indian_assets :
        try :
            if save_asset_data( symbol, name, DATA_DIR ) :
                successful += 1
            else :
                failed += 1
                failed_assets.append( display_name )

            time.sleep( 1 )  # Rate limiting

        except Exception as e :
            print( f"❌ Error with {display_name}: {e}" )
            failed += 1
            failed_assets.append( display_name )
            continue

    print( "\n" + "=" * 60 )
    print( "✅ DATA FETCHING COMPLETE!" )
    print( "=" * 60 )
    print( f"📊 Success: {successful} | Failed: {failed} | Total: {len( indian_assets )}" )

    if failed_assets :
        print( f"\n❌ Failed assets:" )
        for asset in failed_assets[:10] :
            print( f"   • {asset}" )
        if len( failed_assets ) > 10 :
            print( f"   ... and {len( failed_assets ) - 10} more" )

    print( f"\n💾 Data saved to: {DATA_DIR}/" )
    print( "=" * 60 )


if __name__ == "__main__" :
    main()