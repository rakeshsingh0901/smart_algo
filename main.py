import os
import logging
import time
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
    # Initialize the strategy
    # strategy.update_data()
    # strategy.check_first_signal()
    # strategy.check_second_signal()
    # --- State Machine ---
    state = "waiting_for_first"
    first_signal_candle = None
    second_signal_candle = None

    # Main loop to run the strategy every 5 minutes
    while True:
        time.sleep(1)  # Wait for 1 second

if __name__ == "__main__":
    main()
