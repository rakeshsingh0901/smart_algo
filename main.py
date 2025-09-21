import os
import logging
import time
import pytz
from datetime import datetime
from dotenv import load_dotenv
from broker.icici_breeze import IciciBreeze
from technical_analysis.strategy import Strategy

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")
api_session = os.getenv("API_SESSION")

# Check if all credentials are provided
if not all([api_key, secret_key, api_session]):
    logging.error("API_KEY, SECRET_KEY, or API_SESSION not found in .env file.")
    logging.error("Please create a .env file with your credentials (you can use .env.example as a template).")

# --- Stock Configuration ---
# You can change these values to fetch data for a different stock
STOCK_CODE = "NIFTY"
EXCHANGE_CODE = "NSE"
INTERVAL = "5minute"
# --- End of Configuration ---

# Initialize the Breeze API client
breeze = IciciBreeze(api_key=api_key, secret_key=secret_key, api_session=api_session)
strategy = Strategy(breeze, stock_code=STOCK_CODE, exchange_code=EXCHANGE_CODE, interval=INTERVAL)

# Connect to the API
if not breeze.connect():
    logging.error("Failed to connect to the Breeze API.")

breeze.start_websocket(strategy.handle_short_ticks, interval="1second")
def main():
    """
    Main function to run the 5 EMA trading strategy.
    """
    # --- State Machine ---
    state = "waiting_for_first"
    first_signal_candle = None
    second_signal_candle = None

    # Main loop to run the strategy every 5 minutes
    while True:
        # Get the current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        
        # Define market hours
        market_open = now_ist.replace(hour=9, minute=20, second=0, microsecond=0)
        market_close = now_ist.replace(hour=15, minute=31, second=0, microsecond=0)
        
        # Check if it's within market hours and at the right time
        if market_open < now_ist < market_close:
            if now_ist.minute % 5 == 0 and now_ist.second == 1:
                logging.info("--- Market is open and it's time to check for signals every 5 minute ---")

                # Update historical data
                if not strategy.update_data():
                    logging.error("Strategy cycle aborted due to data update failure.")
                
                time.sleep(1)
                if state == "waiting_for_first":
                    if strategy.check_first_signal():
                        first_signal_candle = strategy.first_signal_candle
                        state = "waiting_for_second"
                        logging.info(f"State changed to: {state}")
                elif state == "waiting_for_second":
                    strategy.first_signal_candle = first_signal_candle
                    if strategy.check_second_signal():
                        second_signal_candle = strategy.second_signal_candle
                        state = "waiting_for_final"
                        logging.info(f"State changed to: {state}")
            if state == "waiting_for_final":
                if strategy.check_final_signal():
                    logging.info(f"Take Entry =====================>")
                    # --- Calculate Stop Loss and Target ---
                    stop_loss = strategy.first_signal_candle['high'] + 3
                    target = 2 * (strategy.first_signal_candle['high'] - strategy.second_signal_candle['low'])
                    
                    logging.info(f"Stop Loss: {stop_loss}")
                    logging.info(f"Target: {target}")
                    # --- End of Calculation ---

                    # Reset state and candles for the next trade
                    state = "waiting_for_first"
                    first_signal_candle = None
                    second_signal_candle = None
                    strategy.first_signal_candle = None
                    strategy.second_signal_candle = None
        time.sleep(1)  # Wait for 1 second

if __name__ == "__main__":
    main()
