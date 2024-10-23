# Download market data from NSEIndia's API

<table border=1 cellpadding=10><tr><td>

#### \*\*\* IMPORTANT LEGAL DISCLAIMER \*\*\*

---

openchart is **not** affiliated, endorsed, or vetted by NSEIndia. It's
an open-source tool that uses NseIndia's publicly available APIs, and is
intended for research and educational purposes.


# OpenChart

OpenChart is a Python library for downloading intraday and EOD (End of Day) historical data from the NSE (National Stock Exchange of India) and NFO (NSE Futures and Options) exchanges.

## Features

- Download NSE and NFO master data.
- Search for symbols in NSE and NFO exchanges.
- Fetch historical data for equities and derivatives.
- Supports various timeframes: `1m`, `3m`, `5m`, `10m`, `15m`, `30m`, `1h`, `1d`, `1w`, `1M`.

## Installation

You can install the library directly from the GitHub repository:

```bash
pip install openchart
```

or from the GitHub repository:

```bash
pip install git+https://github.com/marketcalls/openchart.git
```

## Usage

### Import the Library

```python
from openchart import NSEData
```

### Initialize the NSEData Class

```python
nse = NSEData()
```

### Download Master Data

Before fetching historical data or searching for symbols, download the master data:

```python
nse.download()
```

### Download Market Watch Indicies

Fetches the Market watch indicies of NSE

```python
import pandas as pd 
df = nse_data.fetch_available_mw_indices() # Returns a dataframe

print(df.tail())

```

### Download the Equity Market Watch for a given index

Once the available market watch indices are downloaded, you can separately get the market watch for the index along with its associated equities.

``` python

df1 = nse_data.fetch_equity_market_index_data('NIFTY 50')
df2 = nse_data.fetch_equity_market_index_data('NIFTY 500')

print(df1.head())

```


### Fetch Historical Data

To fetch historical data for a symbol, use the `historical` method. **Always specify `start` and `end` dates**. You can use `datetime` and `timedelta` to get data from 30 days back.

#### Intraday Data

Fetch intraday data for **TCS** with a 5-minute interval, from 30 days ago until today:

```python
import datetime

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=30)

data = nse.historical(
    symbol='TCS',
    exchange='NSE',
    start=start_date,
    end=end_date,
    interval='5m'
)
print(data)
```

#### EOD Data

Fetch end-of-day data for **Nifty 50**, from 365 days ago until today:

```python
import datetime

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=365)

data = nse.historical(
    symbol='Nifty 50',
    exchange='NSE',
    start=start_date,
    end=end_date,
    interval='1d'
)
print(data)
```

#### NFO Data

Fetch historical data for a futures contract of 15min data, from 30 days ago until today:

```python
import datetime

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=30)

data = nse.historical(
    symbol='BANKNIFTY24OCTFUT',
    exchange='NFO',
    start=start_date,
    end=end_date,
    interval='15m'
)
print(data)
```

### Search for Symbols

#### NSE Exchange

Search for symbols like **Nifty 50**, **TCS**, **RELIANCE** in the NSE exchange.

```python
symbols = nse.search('RELIANCE', exchange='NSE')
print(symbols)
```

#### NFO Exchange

Search for symbols like **NIFTY24OCTFUT**, **BANKNIFTY24OCTFUT**, **NIFTY24N2124800CE**, **NIFTY24N2124800PE** in the NFO exchange.

- **NIFTY24N2124800CE** corresponds to **NIFTY 21 Nov 2024 CE 24800.00**.
- **NIFTY24N2124800PE** corresponds to **NIFTY 21 Nov 2024 PE 24800.00**.

```python
symbols = nse.search('24OCTFUT', exchange='NFO')
print(symbols)
```

Output
```bash
    ScripCode              Symbol                    Name Type
0       35006   BANKNIFTY24OCTFUT   BANKNIFTY 30 Oct 2024    1
1       35007  NIFTYNXT5024OCTFUT  NIFTYNXT50 25 Oct 2024    1
2       35012    FINNIFTY24OCTFUT    FINNIFTY 29 Oct 2024    1
3       35239  MIDCPNIFTY24OCTFUT  MIDCPNIFTY 28 Oct 2024    1
4       35382       NIFTY24OCTFUT       NIFTY 31 Oct 2024    1
..        ...                 ...                     ...  ...
179     48598         UPL24OCTFUT         UPL 31 Oct 2024    3
180     48601        VEDL24OCTFUT        VEDL 31 Oct 2024    3
181     48602      VOLTAS24OCTFUT      VOLTAS 31 Oct 2024    3
182     48603       WIPRO24OCTFUT       WIPRO 31 Oct 2024    3
183     48604   ZYDUSLIFE24OCTFUT   ZYDUSLIFE 31 Oct 2024    3

[184 rows x 4 columns]

```

#### Exact Match Search

If you want to perform an exact match search, you can set `exact_match=True`.

```python
symbol_info = nse.search('BANKNIFTY24OCTFUT', exchange='NFO', exact_match=True)
print(symbol_info)
```

### Supported Timeframes

```python
print(nse.timeframes())
# Output: ['1m', '3m', '5m', '10m', '15m', '30m', '1h', '1d', '1w', '1M']
```

## Functions

- `download()`: Downloads NSE and NFO master data.
- `search(symbol, exchange, exact_match=False)`: Searches for symbols in the specified exchange (`'NSE'` or `'NFO'`).
  - Returns a pandas DataFrame containing all matching symbols.
- `symbolsearch(symbol, exchange)`: Searches for a symbol and returns the first match.
  - Used internally by the `historical` method.
- `historical(symbol, exchange, start, end, interval='1d')`: Fetches historical data for a symbol.
  - Uses the `symbolsearch` method to find the symbol, which returns the first match.
  - **Always specify `start` and `end` dates when fetching data**.
- `timeframes()`: Returns a list of supported timeframes.

## Notes

- Ensure that you have a stable internet connection.
- The `historical` method uses `symbolsearch`, which returns the first matching symbol. If multiple symbols match your query, consider using an exact symbol name or modifying the `historical` method to accept a symbol code directly.
- **When fetching historical data, always specify `start` and `end` dates. You can use `datetime` and `timedelta` to calculate these dates.**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any questions or support, please open an issue on the GitHub repository 
