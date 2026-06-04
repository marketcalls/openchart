import requests
import pandas as pd
import time
from .utils import process_historical_data


class NSEData:
    """NSE India charting data API client."""

    # Valid segments for symbol search
    SEGMENTS = {
        'IDX': 'Index',      # Indices like NIFTY 50, NIFTY BANK
        'EQ': 'Equity',      # Equities like RELIANCE, TCS
        'FO': 'FO'           # Futures & Options
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Origin': 'https://charting.nseindia.com',
            'Referer': 'https://charting.nseindia.com/'
        })
        self.search_url = "https://charting.nseindia.com/v1/exchanges/symbolsDynamic"
        self.historical_url = "https://charting.nseindia.com/v1/charts/symbolHistoricalData"
        self._cookies_set = False

    def _ensure_cookies(self):
        """Ensure NSE cookies are set for API access."""
        if not self._cookies_set:
            try:
                self.session.get("https://www.nseindia.com", timeout=10)
                self._cookies_set = True
            except requests.exceptions.RequestException:
                pass

    def search(self, symbol, segment='EQ'):
        """Search for symbols using the dynamic search API.

        Args:
            symbol (str): The symbol or part of the symbol to search for.
            segment (str): Market segment:
                - 'IDX' for indices (NIFTY 50, NIFTY BANK, etc.)
                - 'EQ' for equities (RELIANCE, TCS, etc.)
                - 'FO' for futures and options

        Returns:
            pandas.DataFrame: A DataFrame containing matching symbols with columns:
                - symbol: Trading symbol
                - scripcode: Token for historical data
                - description: Full name/description
                - type: Instrument type (Index, Equity, Futures, Options)
                - exchange: Exchange name
        """
        self._ensure_cookies()

        segment = segment.upper()
        if segment not in self.SEGMENTS:
            print(f"Invalid segment '{segment}'. Use 'IDX', 'EQ', or 'FO'.")
            return pd.DataFrame()

        try:
            payload = {"symbol": symbol, "segment": segment}
            response = self.session.post(self.search_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()

            if not result.get('status') or not result.get('data'):
                print(f"No results found for '{symbol}' in segment '{segment}'.")
                return pd.DataFrame()

            df = pd.DataFrame(result['data'])
            return df[['symbol', 'scripcode', 'description', 'type', 'exchange']]

        except requests.exceptions.RequestException as e:
            print(f"Search failed: {e}")
            return pd.DataFrame()

    def historical(self, symbol, segment='EQ', start=None, end=None, interval='1d'):
        """Get historical OHLCV data for a symbol.

        Args:
            symbol (str): The symbol to fetch data for (e.g., 'RELIANCE', 'NIFTY 50').
            segment (str): Market segment:
                - 'IDX' for indices
                - 'EQ' for equities
                - 'FO' for futures/options
            start (datetime): Start date for historical data.
            end (datetime): End date for historical data.
            interval (str): Data interval ('1m', '3m', '5m', '10m', '15m', '30m', '1h', '1d', '1w', '1M').

        Returns:
            pandas.DataFrame: Historical OHLCV data indexed by timestamp.
        """
        self._ensure_cookies()

        search_results = self.search(symbol, segment)
        if search_results.empty:
            return pd.DataFrame()

        # Find exact match or use first result
        symbol_upper = symbol.upper()
        exact_match = search_results[search_results['symbol'].str.upper() == symbol_upper]

        if not exact_match.empty:
            symbol_info = exact_match.iloc[0].to_dict()
        else:
            # Try matching with -EQ suffix for equities
            if segment.upper() == 'EQ':
                eq_match = search_results[search_results['symbol'].str.upper() == f"{symbol_upper}-EQ"]
                if not eq_match.empty:
                    symbol_info = eq_match.iloc[0].to_dict()
                else:
                    symbol_info = search_results.iloc[0].to_dict()
            else:
                symbol_info = search_results.iloc[0].to_dict()

        return self._fetch_historical(symbol_info, start, end, interval)

    def _fetch_historical(self, symbol_info, start, end, interval):
        """Internal method to fetch historical data."""
        interval_map = {
            '1m': (1, 'I'), '5m': (5, 'I'), '10m': (10, 'I'),
            '15m': (15, 'I'), '30m': (30, 'I'), '1h': (60, 'I'),
            '1d': (1, 'D'), '1w': (1, 'W'), '1M': (1, 'M')
        }

        time_interval, chart_type = interval_map.get(interval, (1, 'D'))

        params = {
            "token": str(symbol_info['scripcode']),
            "fromDate": int(start.timestamp()) if start else 0,
            "toDate": int(end.timestamp()) if end else int(time.time()),
            "symbol": symbol_info['symbol'],
            "symbolType": symbol_info['type'],
            "chartType": chart_type,
            "timeInterval": time_interval
        }

        try:
            response = self.session.post(self.historical_url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()

            if not result.get('status') or not result.get('data'):
                print("No data received from the API.")
                return pd.DataFrame()

            return process_historical_data(result['data'], interval)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching historical data: {e}")
            return pd.DataFrame()

    def historical_direct(self, token, symbol, symbol_type, start=None, end=None, interval='1d'):
        """Get historical data directly using token, symbol and symbolType.

        Use this method when you already know the token.

        Args:
            token (str): The token/scripcode for the symbol.
            symbol (str): The symbol name.
            symbol_type (str): The type of symbol ('Index', 'Equity', 'Futures', 'Options').
            start (datetime): Start date for historical data.
            end (datetime): End date for historical data.
            interval (str): Data interval ('1m', '5m', '1d', etc.).

        Returns:
            pandas.DataFrame: Historical OHLCV data.
        """
        symbol_info = {
            'scripcode': token,
            'symbol': symbol,
            'type': symbol_type
        }
        self._ensure_cookies()
        return self._fetch_historical(symbol_info, start, end, interval)

    def timeframes(self):
        """Return supported timeframes."""
        return ['1m', '5m', '10m', '15m', '30m', '1h', '1d', '1w', '1M']

    def segments(self):
        """Return supported market segments."""
        return list(self.SEGMENTS.keys())
