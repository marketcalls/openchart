# OpenChart - NSE India Market Data

<table border=1 cellpadding=10><tr><td>

#### \*\*\* IMPORTANT LEGAL DISCLAIMER \*\*\*

---

OpenChart is **not** affiliated, endorsed, or vetted by NSE India. It's
an open-source tool that uses NSE India's publicly available APIs, and is
intended for research and educational purposes.

</td></tr></table>

## Overview

OpenChart is a Python library for downloading intraday and EOD (End of Day) historical data from NSE India's charting platform. It supports indices, equities, futures, and options.

## Features

- Search for symbols across indices, equities, and F&O segments
- Fetch historical OHLCV data
- Support for multiple timeframes from 1-minute to monthly
- No authentication required

## Installation

```bash
pip install openchart
```

Or install from this fork (includes live NSE API fixes - `GET` + `charting.nseindia.com`):

```bash
pip install git+https://github.com/unn-Known1/openchart.git
```

## Quick Start

```python
from openchart import NSEData
from datetime import datetime, timedelta

nse = NSEData()
end = datetime.now()
start = end - timedelta(days=30)

# Get NIFTY 50 daily data
data = nse.historical('NIFTY 50', 'IDX', start, end, '1d')
print(data)
```

## Market Segments

| Segment | Description | Examples |
|---------|-------------|----------|
| `IDX` | Indices | NIFTY 50, NIFTY BANK, NIFTY IT |
| `EQ` | Equities | RELIANCE-EQ, INFY-EQ, TCS-EQ |
| `FO` | Futures & Options | NIFTY26JANFUT, BANKNIFTY26JANFUT |

## Supported Timeframes

| Timeframe | Description |
|-----------|-------------|
| `1m` | 1 minute |
| `3m` | 3 minutes |
| `5m` | 5 minutes |
| `10m` | 10 minutes |
| `15m` | 15 minutes |
| `30m` | 30 minutes |
| `1h` | 1 hour |
| `1d` | 1 day |
| `1w` | 1 week |
| `1M` | 1 month |

## Usage Examples

### Search for Symbols

```python
from openchart import NSEData

nse = NSEData()

# Search indices
indices = nse.search('NIFTY', 'IDX')
print(indices)
```

Output:
```
             symbol scripcode       description   type exchange
0          NIFTY 50     26000          NIFTY 50  Index      NSE
1          NIFTY IT     26001          NIFTY IT  Index      NSE
2     NIFTY NEXT 50     26002     NIFTY NEXT 50  Index      NSE
3        NIFTY BANK     26004        NIFTY BANK  Index      NSE
4  NIFTY MIDCAP 100     26005  NIFTY MIDCAP 100  Index      NSE
```

```python
# Search equities
equities = nse.search('RELIANCE', 'EQ')
print(equities)
```

Output:
```
        symbol scripcode                description    type exchange
0      RCOM-BE     13188  RELIANCE COMMUNICATIONS L  Equity      NSE
1  RELCHEMQ-EQ      9652  RELIANCE CHEMOTEX IND LTD  Equity      NSE
2  RELIANCE-EQ      2885    RELIANCE INDUSTRIES LTD  Equity      NSE
3      RHFL-BZ    759204  RELIANCE HOME FINANCE LTD  Equity      NSE
4      RIIL-EQ      2912  RELIANCE INDUSTRIAL INFRA  Equity      NSE
5    RPOWER-EQ     15259        RELIANCE POWER LTD.  Equity      NSE
```

```python
# Search futures & options
fo = nse.search('NIFTY', 'FO')
print(fo)
```

Output:
```
               symbol scripcode             description     type exchange
0       NIFTY26FEBFUT     59182       NIFTY 24 FEB 2026  Futures      NSE
1       NIFTY26JANFUT     49229       NIFTY 27 JAN 2026  Futures      NSE
2       NIFTY26MARFUT     51714       NIFTY 30 MAR 2026  Futures      NSE
3  NIFTYNXT5026FEBFUT     59187  NIFTYNXT50 24 FEB 2026  Futures      NSE
4  NIFTYNXT5026JANFUT     49234  NIFTYNXT50 27 JAN 2026  Futures      NSE
...
6   NIFTY2612020400CE     38639  NIFTY 20 JAN 2026 CE 20400.00  Options      NSE
7   NIFTY2612020400PE     38640  NIFTY 20 JAN 2026 PE 20400.00  Options      NSE
```

### Fetch Historical Data

#### Index Data (NIFTY 50)

```python
from openchart import NSEData
from datetime import datetime, timedelta

nse = NSEData()
end = datetime.now()
start = end - timedelta(days=30)

# Daily data
data = nse.historical('NIFTY 50', 'IDX', start, end, '1d')
print(data)
```

Output:
```
                Open      High       Low     Close     Volume
Timestamp
2025-12-18  25764.70  25902.35  25726.30  25815.55  197553755
2025-12-19  25911.50  25993.35  25880.45  25966.40  382927284
2025-12-22  26055.85  26180.70  26047.80  26172.40  252990050
...
```

#### Equity Data (RELIANCE)

```python
# Daily data for RELIANCE
data = nse.historical('RELIANCE-EQ', 'EQ', start, end, '1d')
print(data)
```

Output:
```
              Open    High     Low   Close    Volume
Timestamp
2026-01-09  1465.0  1479.9  1465.0  1475.3   8335311
2026-01-12  1475.3  1485.3  1451.0  1484.0   8877273
2026-01-13  1485.0  1485.8  1444.7  1456.9  13498784
2026-01-14  1444.0  1467.0  1440.2  1458.8   8320926
2026-01-16  1458.8  1480.0  1455.3  1455.8  10959650
```

#### Equity Data (INFY)

```python
# Daily data for INFOSYS
data = nse.historical('INFY-EQ', 'EQ', start, end, '1d')
print(data)
```

Output:
```
              Open    High     Low   Close    Volume
Timestamp
2026-01-09  1610.0  1631.3  1607.0  1616.9   6816214
2026-01-12  1610.1  1613.3  1592.6  1597.6   6984534
2026-01-13  1618.0  1618.0  1586.4  1600.0   8080368
2026-01-14  1588.0  1617.0  1583.1  1599.8   7554679
2026-01-16  1663.7  1693.0  1653.4  1686.3  14395786
```

#### Futures Data

```python
# NIFTY Futures
data = nse.historical('NIFTY26JANFUT', 'FO', start, end, '1d')
print(data)
```

Output:
```
               Open     High      Low    Close   Volume
Timestamp
2026-01-09  25966.0  26031.6  25725.0  25810.8  5830435
2026-01-12  25770.0  25899.0  25573.2  25876.0   121833
2026-01-13  25911.0  25934.8  25661.1  25790.8    87482
2026-01-14  25750.1  25850.0  25670.0  25719.0    70661
2026-01-16  25784.0  25958.0  25752.0  25787.0  4309695
```

```python
# BANKNIFTY Futures
data = nse.historical('BANKNIFTY26JANFUT', 'FO', start, end, '1d')
print(data)
```

Output:
```
               Open     High      Low    Close  Volume
Timestamp
2026-01-09  59890.0  59930.4  59441.0  59525.0  871110
2026-01-12  59600.0  59812.6  59127.6  59730.4   31441
2026-01-13  59880.0  59930.0  59450.0  59755.2   24419
2026-01-14  59690.0  59950.0  59580.2  59780.6   20723
2026-01-16  59833.0  60280.0  59800.0  60085.2  674130
```

#### Intraday Data

```python
# 5-minute data
start_intra = end - timedelta(days=5)
data = nse.historical('NIFTY 50', 'IDX', start_intra, end, '5m')
print(data)
```

Output:
```
                         Open      High       Low     Close  Volume
Timestamp
2026-01-14 15:09:59  25686.25  25694.10  25655.05  25673.10       0
2026-01-14 15:14:59  25673.45  25676.40  25650.80  25652.85       0
2026-01-14 15:19:59  25655.25  25662.00  25648.30  25660.15       0
2026-01-14 15:24:59  25660.75  25675.95  25654.85  25675.55       0
2026-01-14 15:29:59  25675.80  25677.40  25662.60  25669.10       0
```

#### Long-term Daily Data (10 years - e.g., ADANIGREEN)

```python
from openchart import NSEData
from datetime import datetime

nse = NSEData()
start = datetime(2016, 9, 1)  # clamped to listing date
end = datetime.now()

# ADANIGREEN listed 2018-06-18 - 10yr request returns 2032 rows from listing
data = nse.historical('ADANIGREEN-EQ', 'EQ', start, end, '1d')
print(data.head())  # 2018-06-18  30.00  31.50  28.50  31.50
print(data.tail())  # 2026-09-01  1220.00 1271.20 1217.00 1254.80
print(f"Rows: {len(data)}")  # 2032
data.to_csv('ADANIGREEN_10y_1d.csv')
```

### Direct Historical Access

If you already know the token (scripcode), you can fetch data directly:

```python
# Using historical_direct with known token
data = nse.historical_direct(
    token='26000',
    symbol='NIFTY 50',
    symbol_type='Index',
    start=start,
    end=end,
    interval='1d'
)
```

### Utility Methods

```python
# Get supported timeframes
print(nse.timeframes())
# Output: ['1m', '3m', '5m', '10m', '15m', '30m', '1h', '1d', '1w', '1M']

# Get supported segments
print(nse.segments())
# Output: ['IDX', 'EQ', 'FO']
```

## API Reference

### `NSEData()`

Initialize the NSE data client.

### `search(symbol, segment='EQ')`

Search for symbols in a market segment.

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol or partial symbol to search |
| `segment` | str | Market segment: 'IDX', 'EQ', or 'FO' |

**Returns:** pandas DataFrame with columns: `symbol`, `scripcode`, `description`, `type`, `exchange`

### `historical(symbol, segment='EQ', start=None, end=None, interval='1d')`

Fetch historical OHLCV data for a symbol.

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol to fetch data for |
| `segment` | str | Market segment: 'IDX', 'EQ', or 'FO' |
| `start` | datetime | Start date |
| `end` | datetime | End date |
| `interval` | str | Data interval (see supported timeframes) |

**Returns:** pandas DataFrame with OHLCV data indexed by timestamp

### `historical_direct(token, symbol, symbol_type, start=None, end=None, interval='1d')`

Fetch historical data using known token.

| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | str | The scripcode/token for the symbol |
| `symbol` | str | Symbol name |
| `symbol_type` | str | Type: 'Index', 'Equity', 'Futures', 'Options' |
| `start` | datetime | Start date |
| `end` | datetime | End date |
| `interval` | str | Data interval |

### `timeframes()`

Returns list of supported timeframes.

### `segments()`

Returns list of supported market segments.

## Notes

- Ensure you have a stable internet connection
- Intraday data is filtered to market hours (`09:15` to `15:30`) - see `openchart/utils.py:108`; indices have `Volume 0` on intraday by NSE design
- Historical data availability depends on NSE's servers **and listing date**: e.g., `ADANIGREEN-EQ` listed `2018-06-18`, so a 10-year `1d` request (`2016-09-01` to `2026-09-01`) returns `2031` rows from `2018-06-18` (verified live), not a full 10 calendar years
- `start`/`end` are `datetime` objects converted to UNIX timestamps (`openchart/core.py:76`); if omitted, defaults to epoch → now. Raises `ValueError` if `start > end` or `TypeError` for non-datetime
- `interval` is validated: invalid values raise `InvalidIntervalError` (e.g., `'2m'`), includes `3m` (see `openchart/core.py:22`). Large intraday ranges (>180 days) warn about possible truncation
- Errors use `warnings` + `logging` + custom exceptions (`InvalidIntervalError`, `InvalidSegmentError`, `SymbolNotFoundError`) instead of silent `print`
- Use as context manager: `with NSEData() as nse: ...` or `nse.close()`; `timeout` and `max_retries` configurable via `NSEData(timeout=10, max_retries=3)`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Author

Rajandran R
