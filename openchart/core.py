import requests
import json
import pandas as pd
from datetime import datetime
import time
from .utils import process_historical_data

class NSEData:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            'Content-Type': 'application/json',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate'
        })
        self.nse_url = "https://charting.nseindia.com/Charts/GetEQMasters"
        self.nfo_url = "https://charting.nseindia.com/Charts/GetFOMasters"
        self.historical_url = "https://charting.nseindia.com//Charts/symbolhistoricaldata/"
        self.nse_data = None
        self.nfo_data = None

    def download(self):
        """Download NSE and NFO master data."""
        self.nse_data = self._fetch_master_data(self.nse_url)
        self.nfo_data = self._fetch_master_data(self.nfo_url)
        print(f"NSE data shape: {self.nse_data.shape}")
        print(f"NFO data shape: {self.nfo_data.shape}")
        print("NSE and NFO data downloaded successfully.")

    def _fetch_master_data(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.text.splitlines()
            columns = ['ScripCode', 'Symbol', 'Name', 'Type']
            return pd.DataFrame([line.split('|') for line in data], columns=columns)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download data from {url}: {e}")
            return pd.DataFrame()

    def symbolsearch(self, symbol, exchange):
        """Search for a symbol in the specified exchange and return exact match."""
        df = self.nse_data if exchange.upper() == 'NSE' else self.nfo_data
        if df is None:
            print(f"Data for {exchange} not downloaded. Please run download() first.")
            return None
        result = df[df['Symbol'].str.upper() == symbol.upper()]
        if result.empty:
            print(f"No matching result found for symbol '{symbol}' in {exchange}.")
            return None
        return result.iloc[0]

    def search(self, symbol, exchange, exact_match=False):
        """Search for symbols in the specified exchange.

        Args:
            symbol (str): The symbol or part of the symbol to search for.
            exchange (str): The exchange to search in ('NSE' or 'NFO').
            exact_match (bool): If True, performs an exact match. If False, searches for symbols containing the input.

        Returns:
            pandas.DataFrame: A DataFrame containing all matching symbols.
        """
        exchange = exchange.upper()
        if exchange == 'NSE':
            df = self.nse_data
        elif exchange == 'NFO':
            df = self.nfo_data
        else:
            print(f"Invalid exchange '{exchange}'. Please choose 'NSE' or 'NFO'.")
            return pd.DataFrame()

        if df is None:
            print(f"Data for {exchange} not downloaded. Please run download() first.")
            return pd.DataFrame()

        if exact_match:
            result = df[df['Symbol'].str.upper() == symbol.upper()]
        else:
            result = df[df['Symbol'].str.contains(symbol, case=False, na=False)]

        if result.empty:
            print(f"No matching result found for symbol '{symbol}' in {exchange}.")
            return pd.DataFrame()

        return result.reset_index(drop=True)

    def historical(self, symbol="Nifty 50", exchange="NSE", start=None, end=None, interval='1d'):
        """Get historical data for a symbol."""
        symbol_info = self.symbolsearch(symbol, exchange)
        if symbol_info is None:
            return pd.DataFrame()

        interval_map = {
            '1m': ('1', 'I'), '3m': ('3', 'I'), '5m': ('5', 'I'), '10m': ('10', 'I'),
            '15m': ('15', 'I'), '30m': ('30', 'I'), '1h': ('60', 'I'),
            '1d': ('1', 'D'), '1w': ('1', 'W'), '1M': ('1', 'M')
        }

        time_interval, chart_period = interval_map.get(interval, ('1', 'D'))

        payload = {
            "exch": "N" if exchange.upper() == "NSE" else "D",
            "instrType": "C" if exchange.upper() == "NSE" else "D",
            "scripCode": int(symbol_info['ScripCode']),
            "ulToken": int(symbol_info['ScripCode']),
            "fromDate": int(start.timestamp()) if start else 0,
            "toDate": int(end.timestamp()) if end else int(time.time()),
            "timeInterval": time_interval,
            "chartPeriod": chart_period,
            "chartStart": 0
        }

        try:
            # Ensure necessary cookies are set
            self.session.get("https://www.nseindia.com", timeout=5)
            response = self.session.post(self.historical_url, data=json.dumps(payload), timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                print("No data received from the API.")
                return pd.DataFrame()

            return process_historical_data(data, interval)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching historical data: {e}")
            return pd.DataFrame()

    def timeframes(self):
        """Return supported timeframes."""
        return ['1m', '3m', '5m', '10m', '15m', '30m', '1h', '1d', '1w', '1M']