import os
import logging
import time
from datetime import datetime
import pytz
from dotenv import load_dotenv
from broker.icici_breeze import IciciBreeze
from technical_analysis.strategy import Strategy

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    """
    Main function to run the 5 EMA trading strategy.
    """
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
        return

    # --- Stock Configuration ---
    STOCK_CODE = "NIFTY"
    EXCHANGE_CODE = "NSE"
    INTERVAL = "5minute"
    # --- End of Configuration ---

    # Initialize the Breeze API client
    breeze = IciciBreeze(api_key=api_key, secret_key=secret_key, api_session=api_session)

    # Connect to the API
    if not breeze.connect():
        logging.error("Failed to connect to the Breeze API.")
        return

    # Initialize the strategy
    strategy = Strategy(breeze, stock_code=STOCK_CODE, exchange_code=EXCHANGE_CODE, interval=INTERVAL)

    # --- State Machine ---
    state = "waiting_for_first"
    first_signal_candle = None
    second_signal_candle = None

    # Main loop to run the strategy every 5 minutes
    while True:
        logging.info(f"--- Running Strategy Cycle (State: {state}) ---")

        # Get the current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)

        # Define market hours
        market_open = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)

        # Check if it's within market hours and at the right time
        if market_open <= now_ist <= market_close:
            if now_ist.minute % 5 == 0 and now_ist.second == 2:
                logging.info("--- Market is open and it's time to check for signals ---")

                # Update historical data
                if not strategy.update_data():
                    logging.error("Strategy cycle aborted due to data update failure.")
                    continue

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

                elif state == "waiting_for_final":
                    strategy.second_signal_candle = second_signal_candle
                    if strategy.check_final_signal():
                        logging.info("Final signal detected! Time to take action.")
                        state = "waiting_for_first"
                        first_signal_candle = None
                        second_signal_candle = None
                        logging.info(f"State reset to: {state}")

        # Run the loop every second
        time.sleep(1)

if __name__ == "__main__":
    main()
