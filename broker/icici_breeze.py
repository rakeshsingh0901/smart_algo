import logging
from breeze_connect import BreezeConnect

class IciciBreeze:
    """
    A wrapper for the ICICI Direct Breeze API.
    """

    def __init__(self, api_key: str, secret_key: str, api_session: str):
        """
        Initializes the Breeze API client.

        Args:
            api_key: The API key obtained from the Breeze API portal.
            secret_key: The secret key obtained from the Breeze API portal.
            api_session: The API session token obtained after a successful login.
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.api_session = api_session
        self.breeze = None

    def connect(self):
        """
        Establishes a connection to the Breeze API.
        """
        try:
            self.breeze = BreezeConnect(api_key=self.api_key)
            self.breeze.generate_session(api_secret=self.secret_key, session_token=self.api_session)
            logging.info("Successfully connected to Breeze API.")
            return True
        except Exception as e:
            logging.error(f"Error connecting to Breeze API: {e}")
            return False

    def get_historical_data(self, interval: str, from_date: str, to_date: str, stock_code: str, exchange_code: str, product_type: str):
        """
        Fetches historical data for a given stock.

        Args:
            interval: The interval of the data (e.g., "1minute", "5minute", "1day").
            from_date: The start date of the data in "YYYY-MM-DDTHH:MM:SS.sssZ" format.
            to_date: The end date of the data in "YYYY-MM-DDTHH:MM:SS.sssZ" format.
            stock_code: The stock code (e.g., "ITC").
            exchange_code: The exchange code (e.g., "NSE").
            product_type: The product type (e.g., "cash").

        Returns:
            A list of historical data points, or None if an error occurs.
        """
        if not self.breeze:
            logging.error("Not connected to Breeze API. Call connect() first.")
            return None
        try:
            historical_data = self.breeze.get_historical_data(
                interval=interval,
                from_date=from_date,
                to_date=to_date,
                stock_code=stock_code,
                exchange_code=exchange_code,
                product_type=product_type
            )
            return historical_data
        except Exception as e:
            logging.error(f"Error fetching historical data: {e}")
            return None

    def get_cash_ltp(self, stock_code: str, exchange_code: str):
        """
        Gets the last traded price for a cash instrument.

        Args:
            stock_code: The stock code (e.g., "ITC").
            exchange_code: The exchange code (e.g., "NSE").

        Returns:
            The last traded price, or None if an error occurs.
        """
        if not self.breeze:
            logging.error("Not connected to Breeze API. Call connect() first.")
            return None
        try:
            # For cash products, expiry_date, right, and strike_price are not needed.
            quote = self.breeze.get_quotes(
                stock_code=stock_code,
                exchange_code=exchange_code,
                product_type="cash",
                expiry_date="",
                right="",
                strike_price=""
            )
            if quote and quote.get('Success'):
                return quote['Success'][0].get('ltp')
            else:
                logging.error(f"Error getting LTP: {quote.get('Error')}")
                return None
        except Exception as e:
            logging.error(f"Error getting LTP: {e}")
            return None

    def start_websocket(self, on_ticks):
        """
        Starts the WebSocket for real-time data.

        Args:
            on_ticks: The callback function to handle incoming ticks.
        """
        if not self.breeze:
            logging.error("Not connected to Breeze API. Call connect() first.")
            return
        try:
            self.breeze.ws_connect()
            self.breeze.on_ticks = on_ticks
            logging.info("WebSocket connected.")
        except Exception as e:
            logging.error(f"Error starting WebSocket: {e}")

    def stop_websocket(self):
        """
        Stops the WebSocket connection.
        """
        if not self.breeze:
            logging.error("Not connected to Breeze API.")
            return
        try:
            self.breeze.ws_disconnect()
            logging.info("WebSocket disconnected.")
        except Exception as e:
            logging.error(f"Error stopping WebSocket: {e}")

    def subscribe_feeds(self, stock_token: str):
        """
        Subscribes to real-time feeds for a given stock token.

        Args:
            stock_token: The stock token to subscribe to (e.g., "4.1!2885").
        """
        if not self.breeze:
            logging.error("Not connected to Breeze API.")
            return
        try:
            self.breeze.subscribe_feeds(stock_token)
            logging.info(f"Subscribed to feeds for {stock_token}")
        except Exception as e:
            logging.error(f"Error subscribing to feeds: {e}")

    def unsubscribe_feeds(self, stock_token: str):
        """
        Unsubscribes from real-time feeds for a given stock token.

        Args:
            stock_token: The stock token to unsubscribe from (e.g., "4.1!2885").
        """
        if not self.breeze:
            logging.error("Not connected to Breeze API.")
            return
        try:
            self.breeze.unsubscribe_feeds(stock_token)
            logging.info(f"Unsubscribed from feeds for {stock_token}")
        except Exception as e:
            logging.error(f"Error unsubscribing from feeds: {e}")
