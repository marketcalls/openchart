import warnings
import pandas as pd
from openchart.utils import process_historical_data


def test_empty_data_returns_empty_df():
    df = process_historical_data([], '1d')
    assert df.empty
    assert list(df.columns) == ['Open', 'High', 'Low', 'Close', 'Volume']
    assert df.index.name == 'Timestamp'


def test_malformed_data_returns_empty():
    # Missing columns
    malformed = [{'time': 123, 'open': 1}]
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        df = process_historical_data(malformed, '1d')
    assert df.empty


def test_none_data_returns_empty():
    with warnings.catch_warnings(record=True):
        df = process_historical_data(None, '1d')
    assert df.empty


def test_duplicate_timestamps_deduped():
    data = [
        {'time': 1700000000000, 'open': 1, 'high': 2, 'low': 0, 'close': 1, 'volume': 100},
        {'time': 1700000000000, 'open': 1.1, 'high': 2.1, 'low': 0.1, 'close': 1.1, 'volume': 110},
        {'time': 1700000060000, 'open': 2, 'high': 3, 'low': 1, 'close': 2, 'volume': 200},
    ]
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        df = process_historical_data(data, '1d')
        assert any("duplicate" in str(x.message).lower() for x in w)
    assert len(df) == 2
    assert df.index.is_monotonic_increasing
    # last kept
    assert df.iloc[0]['Open'] == 1.1


def test_sorting():
    data = [
        {'time': 1700000060000, 'open': 2, 'high': 3, 'low': 1, 'close': 2, 'volume': 200},
        {'time': 1700000000000, 'open': 1, 'high': 2, 'low': 0, 'close': 1, 'volume': 100},
    ]
    df = process_historical_data(data, '1d')
    assert df.index.is_monotonic_increasing


def test_intraday_filter():
    # 09:00 should be dropped, 09:20 kept, 12:00 kept, 16:00 dropped
    from datetime import datetime
    data = [
        {'time': int(datetime(2026, 1, 2, 9, 0).timestamp() * 1000), 'open': 1, 'high': 1, 'low': 1, 'close': 1, 'volume': 1},
        {'time': int(datetime(2026, 1, 2, 9, 20).timestamp() * 1000), 'open': 1, 'high': 1, 'low': 1, 'close': 1, 'volume': 1},
        {'time': int(datetime(2026, 1, 2, 12, 0).timestamp() * 1000), 'open': 1, 'high': 1, 'low': 1, 'close': 1, 'volume': 1},
        {'time': int(datetime(2026, 1, 2, 16, 0).timestamp() * 1000), 'open': 1, 'high': 1, 'low': 1, 'close': 1, 'volume': 1},
    ]
    df = process_historical_data(data, '5m')
    assert len(df) == 2
    df_daily = process_historical_data(data, '1d')
    assert len(df_daily) == 4  # no filter for daily


def test_numeric_coercion():
    data = [{'time': 1700000000000, 'open': '1.5', 'high': '2', 'low': '0', 'close': '1', 'volume': '100.0'}]
    df = process_historical_data(data, '1d')
    assert df['Open'].dtype == float
    assert df['Volume'].dtype == 'int64'


def test_timestamp_parsing():
    data = [{'time': 1700000000000, 'open': 1, 'high': 1, 'low': 1, 'close': 1, 'volume': 1}]
    df = process_historical_data(data, '1d')
    assert isinstance(df.index[0], pd.Timestamp)
    assert df.index.tz is None  # naive
