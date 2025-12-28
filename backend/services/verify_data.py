"""
Script to verify that gold and silver data has current prices.
Run this BEFORE retraining to ensure data is up-to-date.
"""

import pandas as pd
import os
from datetime import datetime, timedelta

DATA_DIR = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/data"

def verify_asset_data(asset_name):
    """
    Verify that an asset has recent data with reasonable prices.

    Args:
        asset_name: Name of the asset (e.g., 'gold', 'silver', 'bitcoin')
    """
    print(f"\n{'='*60}")
    print(f"📊 VERIFYING {asset_name.upper()} DATA")
    print('='*60)

    path = os.path.join(DATA_DIR, asset_name, f"{asset_name}.csv")

    if not os.path.exists(path):
        print(f"❌ Data file not found: {path}")
        return False

    try:
        df = pd.read_csv(path)

        print(f"\n📈 Data Overview:")
        print(f"   Total rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")

        # Check if we have Close prices
        if 'Close' not in df.columns:
            print(f"❌ 'Close' column not found!")
            return False

        prices = df['Close'].values

        # Price statistics
        print(f"\n💰 Price Statistics:")
        print(f"   Minimum: ${prices.min():.2f}")
        print(f"   Maximum: ${prices.max():.2f}")
        print(f"   Average: ${prices.mean():.2f}")
        print(f"   Current (last): ${prices[-1]:.2f}")

        # Check timestamp if available
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            oldest = df['timestamp'].min()
            newest = df['timestamp'].max()

            print(f"\n📅 Date Range:")
            print(f"   Oldest: {oldest.strftime('%Y-%m-%d')}")
            print(f"   Newest: {newest.strftime('%Y-%m-%d')}")

            # Make datetime.now() timezone-aware for comparison
            from datetime import timezone
            now_utc = datetime.now(timezone.utc)
            days_old = (now_utc - newest).days
            print(f"   Data age: {days_old} days old")

            if days_old > 7:
                print(f"   ⚠️ WARNING: Data is {days_old} days old! Consider refreshing.")
            else:
                print(f"   ✅ Data is recent (within last week)")

        # Asset-specific validation
        if asset_name == 'gold':
            print(f"\n🔍 Gold-Specific Validation:")
            if prices[-1] < 1000:
                print(f"   ❌ ERROR: Current gold price ${prices[-1]:.2f} is too low!")
                print(f"   Gold should be $4000+ as of December 2024")
                print(f"   🔄 Please re-fetch gold data!")
                return False
            elif prices[-1] < 4000:
                print(f"   ⚠️ WARNING: Gold price ${prices[-1]:.2f} seems outdated")
                print(f"   Current gold should be around $4500-4600")
                print(f"   🔄 Consider re-fetching gold data")
            else:
                print(f"   ✅ Gold price ${prices[-1]:.2f} looks reasonable")

        elif asset_name == 'silver':
            print(f"\n🔍 Silver-Specific Validation:")
            if prices[-1] < 15:
                print(f"   ❌ ERROR: Current silver price ${prices[-1]:.2f} is too low!")
                print(f"   Silver should be $70+ as of December 2024")
                print(f"   🔄 Please re-fetch silver data!")
                return False
            elif prices[-1] < 70:
                print(f"   ⚠️ WARNING: Silver price ${prices[-1]:.2f} seems outdated")
                print(f"   Current silver should be around $77-79")
                print(f"   🔄 Consider re-fetching silver data")
            else:
                print(f"   ✅ Silver price ${prices[-1]:.2f} looks reasonable")

        elif asset_name == 'bitcoin':
            print(f"\n🔍 Bitcoin-Specific Validation:")
            if prices[-1] < 50000:
                print(f"   ⚠️ WARNING: Bitcoin price ${prices[-1]:.2f} seems low")
            elif prices[-1] > 200000:
                print(f"   ⚠️ WARNING: Bitcoin price ${prices[-1]:.2f} seems very high")
            else:
                print(f"   ✅ Bitcoin price ${prices[-1]:.2f} looks reasonable")

        print(f"\n✅ {asset_name.upper()} data verification complete")
        return True

    except Exception as e:
        print(f"❌ Error reading {asset_name} data: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("🔍 DATA VERIFICATION SCRIPT")
    print("="*60)
    print("\nThis script checks if your data has current prices.")
    print("Run this BEFORE retraining your model!\n")

    assets_to_check = ['gold', 'silver', 'bitcoin']
    results = {}

    for asset in assets_to_check:
        results[asset] = verify_asset_data(asset)

    # Summary
    print("\n" + "="*60)
    print("📋 VERIFICATION SUMMARY")
    print("="*60)

    all_good = True
    for asset, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{asset.upper():15s}: {status}")
        if not passed:
            all_good = False

    print("\n" + "="*60)
    if all_good:
        print("✅ ALL DATA VERIFIED - Safe to retrain model")
        print("\nNext steps:")
        print("1. Run: python train_model.py")
        print("2. Wait for training to complete")
        print("3. Test predictions")
    else:
        print("❌ DATA ISSUES FOUND - DO NOT RETRAIN YET")
        print("\nNext steps:")
        print("1. Run: python fetch_metals_data.py")
        print("2. Wait for data fetch to complete")
        print("3. Run this script again to verify")
        print("4. Then run: python train_model.py")
    print("="*60)


if __name__ == "__main__":
    main()