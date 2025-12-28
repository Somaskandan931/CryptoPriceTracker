"""
Automated script to run the complete fix for gold/silver predictions.
This runs all steps in the correct order with proper error handling.
"""

import subprocess
import sys
import os
import time


def run_command ( description, command, check_success=True ) :
    """
    Run a command and handle errors.

    Args:
        description: What this step does
        command: Command to run (as list)
        check_success: Whether to check if command succeeded
    """
    print( "\n" + "=" * 60 )
    print( f"🔄 {description}" )
    print( "=" * 60 )

    try :
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check_success
        )

        print( result.stdout )

        if result.stderr :
            print( "Warnings/Errors:" )
            print( result.stderr )

        if check_success and result.returncode != 0 :
            print( f"❌ Command failed with return code {result.returncode}" )
            return False

        print( f"✅ {description} completed" )
        return True

    except subprocess.CalledProcessError as e :
        print( f"❌ Error running command: {e}" )
        print( f"Output: {e.stdout}" )
        print( f"Error: {e.stderr}" )
        return False
    except Exception as e :
        print( f"❌ Unexpected error: {e}" )
        return False


def confirm ( message ) :
    """Ask user for confirmation."""
    while True :
        response = input( f"\n{message} (y/n): " ).lower().strip()
        if response in ['y', 'yes'] :
            return True
        elif response in ['n', 'no'] :
            return False
        else :
            print( "Please enter 'y' or 'n'" )


def main () :
    print( "=" * 60 )
    print( "🚀 AUTOMATED FIX FOR GOLD/SILVER PREDICTIONS" )
    print( "=" * 60 )
    print( "\nThis script will:" )
    print( "1. Verify your current data has up-to-date prices" )
    print( "2. Re-fetch metals data if needed" )
    print( "3. Retrain the model with coin-specific scalers" )
    print( "4. Test predictions" )
    print( "5. Optionally start the API" )

    if not confirm( "\nDo you want to continue?" ) :
        print( "❌ Aborted by user" )
        return

    # Step 1: Verify data
    print( "\n" + "=" * 60 )
    print( "STEP 1: VERIFYING DATA" )
    print( "=" * 60 )

    verification_passed = run_command(
        "Verifying data has current prices",
        [sys.executable, "verify_data.py"],
        check_success=False  # We'll check manually
    )

    # Check if we need to re-fetch
    if not verification_passed or not confirm( "\nDid all data verification checks PASS?" ) :
        print( "\n⚠️ Data needs to be refreshed" )

        if confirm( "Re-fetch metals data now? (Recommended)" ) :
            # Step 2a: Fetch metals
            if not run_command(
                    "Fetching fresh gold/silver data",
                    [sys.executable, "fetch_metals_data.py"]
            ) :
                print( "❌ Failed to fetch metals data" )
                print( "Please run manually: python fetch_metals_data.py" )
                return

            time.sleep( 2 )

            # Step 2b: Update encoder
            if not run_command(
                    "Updating encoder with metals",
                    [sys.executable, "add_metals_to_encoder.py"]
            ) :
                print( "❌ Failed to update encoder" )
                print( "Please run manually: python add_metals_to_encoder.py" )
                return

            time.sleep( 2 )

            # Step 2c: Verify again
            print( "\n🔍 Verifying data again after re-fetch..." )
            run_command(
                "Final data verification",
                [sys.executable, "verify_data.py"],
                check_success=False
            )

            if not confirm( "\nDid verification PASS this time?" ) :
                print( "❌ Data still has issues. Please check manually." )
                return

    # Step 3: Retrain model
    print( "\n" + "=" * 60 )
    print( "STEP 2: RETRAINING MODEL" )
    print( "=" * 60 )
    print( "\n⚠️ This may take 5-15 minutes depending on your hardware" )

    if not confirm( "Start training now?" ) :
        print( "❌ Aborted. Please run manually: python train_model.py" )
        return

    if not run_command(
            "Training model with coin-specific scalers",
            [sys.executable, "train_model.py"]
    ) :
        print( "❌ Training failed" )
        print( "\nTroubleshooting:" )
        print( "1. Check you have enough RAM (needs ~4GB)" )
        print( "2. Check all dependencies installed: pip install -r requirements.txt" )
        print( "3. Try running manually: python train_model.py" )
        return

    time.sleep( 2 )

    # Step 4: Test predictions
    print( "\n" + "=" * 60 )
    print( "STEP 3: TESTING PREDICTIONS" )
    print( "=" * 60 )

    run_command(
        "Testing predictions for gold, silver, bitcoin",
        [sys.executable, "predictor.py"],
        check_success=False
    )

    # Final summary
    print( "\n" + "=" * 60 )
    print( "🎉 COMPLETE!" )
    print( "=" * 60 )

    print( "\n📋 What was done:" )
    print( "✅ Data verified/refreshed" )
    print( "✅ Model retrained with coin-specific scalers" )
    print( "✅ Predictions tested" )

    print( "\n🎯 Expected Results:" )
    print( "   Gold predictions: $4,400 - $4,700" )
    print( "   Silver predictions: $76 - $82" )
    print( "   Bitcoin predictions: $83k - $94k" )

    print( "\n📝 Next Steps:" )
    print( "1. Check prediction outputs above match expected ranges" )
    print( "2. Start API: python main.py" )
    print( "3. Test via API:" )
    print( "   curl http://localhost:8000/predict/gold" )
    print( "   curl http://localhost:8000/predict/silver" )

    if confirm( "\nWould you like to start the API now?" ) :
        print( "\n🌐 Starting API server..." )
        print( "API will be available at: http://localhost:8000" )
        print( "Press Ctrl+C to stop" )
        print( "\nDocs at: http://localhost:8000/docs" )

        try :
            subprocess.run( [sys.executable, "main.py"] )
        except KeyboardInterrupt :
            print( "\n\n👋 API server stopped" )


if __name__ == "__main__" :
    # Check we're in the right directory
    if not os.path.exists( "dataset.py" ) :
        print( "❌ Error: Must run from the model directory" )
        print( "Current directory:", os.getcwd() )
        print( "\nPlease cd to: C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model" )
        sys.exit( 1 )

    try :
        main()
    except KeyboardInterrupt :
        print( "\n\n❌ Interrupted by user" )
    except Exception as e :
        print( f"\n❌ Unexpected error: {e}" )
        import traceback

        traceback.print_exc()