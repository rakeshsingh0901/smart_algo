import logging
from datetime import datetime, timedelta
from technical_analysis.indicators import Indicators

class Strategy:
    """
    Implements the 5 EMA trading strategy.
    """

    def __init__(self, breeze, stock_code="NIFTY", exchange_code="NSE", interval="5minute"):
        """
        Initializes the Strategy class.

        Args:
            breeze: An instance of the IciciBreeze class.
            stock_code: The stock code to trade.
            exchange_code: The exchange code for the stock.
            interval: The interval for historical data.
        """
        self.breeze = breeze
        self.stock_code = stock_code
        self.exchange_code = exchange_code
        self.interval = interval
        self.indicators = Indicators()
        self.historical_data = None
        self.first_signal_candle = None
        self.second_signal_candle = None

    def update_data(self):
        """
        Fetches and updates historical data for the last 5 days.

        Returns:
            True if data was updated successfully, False otherwise.
        """
        logging.info("Updating historical data...")
        to_date = datetime.now()
        from_date = to_date - timedelta(days=5)

        to_date_str = to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        from_date_str = from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        new_historical_data = self.breeze.get_historical_data(
            interval=self.interval,
            from_date=from_date_str,
            to_date=to_date_str,
            stock_code=self.stock_code,
            exchange_code=self.exchange_code,
            product_type="cash"  # Assuming cash product for NIFTY
        )

        if new_historical_data and new_historical_data.get('Success'):
            self.historical_data = new_historical_data
            self.indicators.update_data(self.historical_data)
            logging.info("Successfully updated historical data.")
            return True
        else:
            logging.error("Failed to update historical data.")
            return False

    def check_first_signal(self, ema_period=5, diff_threshold=2, buffer=3):
        """
        Checks for the first signal.
        The first signal occurs if the low of the latest candle (with a buffer) is greater than the 5-period EMA,
        and the difference between the low and the EMA is greater than a given threshold.

        Args:
            ema_period: The period for the Exponential Moving Average.
            diff_threshold: The minimum difference between the candle's low and the EMA.
            buffer: The buffer to subtract from the low price.

        Returns:
            True if the first signal is found, False otherwise.
        """
        if self.indicators.data is None:
            logging.error("Indicator data is not available.")
            return False

        # Calculate the 5-period EMA
        ema_values = self.indicators.ema(period=ema_period)
        if ema_values is None or len(ema_values) < 1:
            logging.warning("Not enough data to calculate EMA or EMA is empty.")
            return False

        # Get the latest EMA value and the latest candle
        latest_ema = ema_values[-1]
        latest_candle = self.indicators.data.iloc[-1]

        # Check for the first signal condition
        if (latest_candle['low'] - buffer) > latest_ema and (latest_candle['low'] - latest_ema) > diff_threshold:
            logging.info(f"First signal detected: low ({latest_candle['low']}) - buffer({buffer}) > EMA ({latest_ema}) and diff > {diff_threshold}")
            self.first_signal_candle = latest_candle
            return True
        else:
            return False

    def check_second_signal(self, buffer=3):
        """
        Checks for the second signal.
        The second signal occurs if the low of the candle following the first signal candle
        is lower than the low of the first signal candle (with a buffer).

        Args:
            buffer: The buffer to subtract from the low price of the first signal candle.

        Returns:
            True if the second signal is found, False otherwise.
        """
        if self.first_signal_candle is None:
            # No first signal, so no second signal
            return False

        if self.indicators.data is None or len(self.indicators.data) < 2:
            logging.warning("Not enough data to check for the second signal.")
            return False

        # Get the index of the first signal candle
        first_signal_candle_index = self.indicators.data.index.get_loc(self.first_signal_candle.name)

        # Check if there is a candle after the first signal candle
        if first_signal_candle_index + 1 < len(self.indicators.data):
            next_candle = self.indicators.data.iloc[first_signal_candle_index + 1]
            if next_candle['low'] < (self.first_signal_candle['low'] - buffer):
                logging.info(f"Second signal detected: next candle low ({next_candle['low']}) < first signal candle low ({self.first_signal_candle['low']}) - buffer({buffer})")
                self.second_signal_candle = next_candle
                return True

        return False

    def check_final_signal(self, buffer=3):
        """
        Checks for the final signal.
        The final signal occurs if the current price of the stock breaks the low
        of the second signal candle (with a buffer).

        Args:
            buffer: The buffer to subtract from the low price of the second signal candle.

        Returns:
            True if the final signal is found, False otherwise.
        """
        if self.second_signal_candle is None:
            # No second signal, so no final signal
            return False

        # Get the current price of the stock
        ltp = self.breeze.get_cash_ltp(stock_code=self.stock_code, exchange_code=self.exchange_code)

        if ltp is None:
            logging.error("Could not get the last traded price (LTP).")
            return False

        if ltp < (self.second_signal_candle['low'] - buffer):
            logging.info(f"Final signal detected: LTP ({ltp}) < second signal candle low ({self.second_signal_candle['low']}) - buffer({buffer})")
            return True
        else:
            return False
