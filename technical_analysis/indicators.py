import pandas as pd
import talib
import numpy as np

class Indicators:
    """
    A class to calculate technical indicators on a given dataset.
    """

    def __init__(self, historical_data=None):
        """
        Initializes the Indicators class.

        Args:
            historical_data: A list of historical data points from the broker.
        """
        self.data = None
        if historical_data:
            self.update_data(historical_data)

    def _sanitize_data(self, historical_data):
        """
        Sanitizes historical data from the broker for use with talib.
        This is a private method.

        Args:
            historical_data: A list of historical data points from the broker.

        Returns:
            A pandas DataFrame with columns 'open', 'high', 'low', 'close', 'volume'.
            Returns None if the input data is invalid.
        """
        if not historical_data or 'Success' not in historical_data:
            return None

        data = historical_data['Success']
        if not data:
            return None

        df = pd.DataFrame(data)
        if 'datetime' not in df.columns:
            return None

        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        # Convert columns to numeric types
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                # If a required column is missing, we can't proceed.
                return None

        return df

    def update_data(self, historical_data):
        """
        Updates the historical data in the instance.

        Args:
            historical_data: A list of historical data points from the broker.
        """
        self.data = self._sanitize_data(historical_data)
        #  If data is valid, calculate RSI and add it as a column
        if self.data is not None:
            self.data['rsi'] = self.rsi(period=14)

    def ema(self, period=14):
        """
        Calculates the Exponential Moving Average (EMA).

        Args:
            period: The time period for the EMA.

        Returns:
            A pandas Series with the EMA values, or None if data is not available.
        """
        if self.data is None or 'close' not in self.data.columns:
            return None

        close_prices = self.data['close'].values.astype(float)
        ema_values = talib.EMA(close_prices, timeperiod=period)
        return ema_values

    def rsi(self, period=14):
        """
        Calculates the Relative Strength Index (RSI).

        Args:
            period: The time period for the RSI.

        Returns:
            A pandas Series with the RSI values, or None if data is not available.
        """
        if self.data is None or 'close' not in self.data.columns:
            return None

        close_prices = self.data['close'].values.astype(float)
        rsi_values = talib.RSI(close_prices, timeperiod=period)
        return rsi_values
