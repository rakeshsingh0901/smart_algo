import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from broker.icici_breeze import IciciBreeze

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    """
    Main function to fetch historical stock data.
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
    PRODUCT_TYPE = "cash"
    INTERVAL = "5minute"
    # --- End of Configuration ---

    # Calculate date range for the last 5 days
    to_date = datetime.now()
    from_date = to_date - timedelta(days=5)

    # Format dates for the API
    to_date_str = to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    from_date_str = from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    logging.info(f"Fetching data for {STOCK_CODE} from {from_date_str} to {to_date_str}")

    # Initialize the Breeze API client
    breeze = IciciBreeze(api_key=api_key, secret_key=secret_key, api_session=api_session)

    # Connect to the API
    if not breeze.connect():
        logging.error("Failed to connect to the Breeze API.")
        return

    # Fetch historical data
    historical_data = breeze.get_historical_data(
        interval=INTERVAL,
        from_date=from_date_str,
        to_date=to_date_str,
        stock_code=STOCK_CODE,
        exchange_code=EXCHANGE_CODE,
        product_type=PRODUCT_TYPE
    )

    # Print the fetched data
    if historical_data and historical_data.get('Success'):
        logging.info("Successfully fetched historical data:")
        # Pretty print the success data
        import pprint
        pprint.pprint(historical_data['Success'])
    elif historical_data and historical_data.get('Error'):
        logging.error(f"Error fetching data: {historical_data['Error']}")
    else:
        logging.error("Failed to fetch historical data. The response was empty or invalid.")

if __name__ == "__main__":
    main()
