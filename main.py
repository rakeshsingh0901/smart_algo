import os
import logging
import time
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
    # You can change these values to fetch data for a different stock
    STOCK_CODE = "ITC"
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

        # Update historical data
        if not strategy.update_data():
            logging.error("Strategy cycle aborted due to data update failure.")
            time.sleep(300)  # Wait for 5 minutes before retrying
            continue

        if state == "waiting_for_first":
            if strategy.check_first_signal():
                first_signal_candle = strategy.first_signal_candle
                state = "waiting_for_second"
                logging.info(f"State changed to: {state}")

        elif state == "waiting_for_second":
            # Pass the first signal candle to the check method
            strategy.first_signal_candle = first_signal_candle
            if strategy.check_second_signal():
                second_signal_candle = strategy.second_signal_candle
                state = "waiting_for_final"
                logging.info(f"State changed to: {state}")
            # Optional: Add logic to invalidate the first signal after some time

        elif state == "waiting_for_final":
            # Pass the second signal candle to the check method
            strategy.second_signal_candle = second_signal_candle
            if strategy.check_final_signal():
                logging.info("Final signal detected! Time to take action.")
                # Reset the state machine
                state = "waiting_for_first"
                first_signal_candle = None
                second_signal_candle = None
                logging.info(f"State reset to: {state}")
            # Optional: Add logic to invalidate the second signal after some time

        logging.info("Strategy cycle finished. Waiting for the next 5-minute interval...")
        time.sleep(300)  # Wait for 5 minutes

if __name__ == "__main__":
    main()
