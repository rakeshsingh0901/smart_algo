# Algorithmic Trading Bot Framework - AGENTS.md

This document provides an overview of the algorithmic trading bot framework, its structure, and how to work with it.

## 1. Project Overview

This project is the foundation for an algorithmic trading bot. It provides a modular structure for interacting with a broker's API, calculating technical indicators, and building trading strategies.

The initial version supports:
-   ICICI Direct's Breeze API for brokerage services.
-   Technical analysis using the `talib` library.

## 2. Directory Structure

The project is organized into the following modules:

-   `broker/`: This directory contains modules related to broker integrations.
    -   `icici_breeze.py`: Contains the `IciciBreeze` class, which is a client for the ICICI Direct Breeze API. It handles connection, data fetching, and WebSocket communication.

-   `technical_analysis/`: This directory contains modules for technical analysis.
    -   `indicators.py`: Contains the `Indicators` class, which is used to calculate technical indicators like EMA and RSI on historical data.

-   `requirements.txt`: This file lists all the Python dependencies required for the project.

## 3. Key Classes and Usage

### `broker.icici_breeze.IciciBreeze`

This class is a wrapper around the `breeze-connect` library and provides a simplified interface to the ICICI Direct Breeze API.

**How to use:**
1.  **Initialization:**
    ```python
    from broker.icici_breeze import IciciBreeze

    # You need to provide your API key, secret key, and a valid API session token.
    breeze = IciciBreeze(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY", api_session="YOUR_API_SESSION")
    ```
2.  **Connection:**
    ```python
    breeze.connect()
    ```
3.  **Fetching Data:**
    ```python
    historical_data = breeze.get_historical_data(...)
    ltp = breeze.get_cash_ltp(...)
    ```
4.  **WebSocket:**
    ```python
    def on_ticks(ticks):
        print(ticks)

    breeze.start_websocket(on_ticks=on_ticks)
    breeze.subscribe_feeds(stock_token="4.1!2885")
    # ...
    breeze.stop_websocket()
    ```

### `technical_analysis.indicators.Indicators`

This class is used to perform technical analysis on a given set of historical data.

**How to use:**
1.  **Initialization:**
    ```python
    from technical_analysis.indicators import Indicators

    # Initialize with historical data (e.g., from the broker)
    indicators = Indicators(historical_data)
    ```
2.  **Updating Data:**
    ```python
    indicators.update_data(new_historical_data)
    ```
3.  **Calculating Indicators:**
    ```python
    ema_values = indicators.ema(period=14)
    rsi_values = indicators.rsi(period=14)
    ```

## 4. How to Get Started

1.  **Install Dependencies:**
    -   Make sure you have the TA-Lib C library installed on your system.
    -   Install the Python packages using pip:
        ```bash
        pip install -r requirements.txt
        ```

2.  **Provide Credentials:**
    -   You will need an API key, secret key, and a temporary API session token from the ICICI Direct Breeze API portal.

## 5. Future Development

-   **Adding a new indicator:** Add a new method to the `Indicators` class in `technical_analysis/indicators.py`.
-   **Adding a new broker:** Create a new client class in the `broker/` directory that follows a similar interface to `IciciBreeze`.
