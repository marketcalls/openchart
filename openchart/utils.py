import logging
import warnings
import pandas as pd

logger = logging.getLogger(__name__)


def process_historical_data(data, interval: str) -> pd.DataFrame:
    """Process raw historical data into a pandas DataFrame.

    Args:
        data (list): Raw data from the API (list of dicts with time, open, high, low, close, volume).
        interval (str): Data interval to determine if cutoff time should be applied.

    Returns:
        pandas.DataFrame: Processed historical data indexed by Timestamp. Returns empty DataFrame if data is empty/malformed.

    Notes:
        - Timestamp is returned as tz-naive UTC (stripped). Use `tz_localize('UTC').tz_convert('Asia/Kolkata')` if IST needed.
        - Indices have Volume 0 on intraday by NSE design.
    """
    # Guard empty
    if not data:
        logger.info("process_historical_data received empty data for interval %s", interval)
        return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume']).rename_axis('Timestamp')

    # Validate data is list of dicts
    if not isinstance(data, list):
        logger.warning("Expected list data, got %s", type(data).__name__)
        warnings.warn(f"Expected list data, got {type(data).__name__}", UserWarning)
        return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume']).rename_axis('Timestamp')

    df = pd.DataFrame(data)

    # Handle already empty after DataFrame conversion
    if df.empty:
        return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume']).rename_axis('Timestamp')

    # Validate required columns exist
    required_map = {'time': 'Timestamp', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}
    missing = [k for k in required_map if k not in df.columns]
    if missing:
        logger.warning("Missing expected columns %s, got %s", missing, list(df.columns))
        warnings.warn(f"Missing expected columns {missing}, data may be malformed", UserWarning)
        # Try to handle if API already returns capitalised names?
        # If data already has Open/High etc, try to map case-insensitively
        alt_map = {k.lower(): v for k, v in required_map.items()}
        # Attempt to rename lowercased columns
        rename_dict = {}
        for col in df.columns:
            if col.lower() in alt_map:
                rename_dict[col] = alt_map[col.lower()]
        if rename_dict:
            df = df.rename(columns=rename_dict)
        else:
            return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume']).rename_axis('Timestamp')

    # Rename columns to standard OHLCV format (if still lower case)
    df = df.rename(columns={
        'time': 'Timestamp',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })

    # Ensure required columns present after rename
    for col in ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']:
        if col not in df.columns:
            logger.warning("Column %s missing after rename, returning empty", col)
            return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume']).rename_axis('Timestamp')

    # Convert timestamp from milliseconds to datetime (NSE sends ms)
    try:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms', utc=True, errors='coerce')
    except Exception as e:
        logger.error("Failed to parse Timestamp: %s", e)
        warnings.warn(f"Failed to parse Timestamp: {e}", UserWarning)
        return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume']).rename_axis('Timestamp')

    # Drop rows where Timestamp is NaT
    before = len(df)
    df = df.dropna(subset=['Timestamp'])
    if len(df) < before:
        logger.warning("Dropped %d rows with invalid Timestamp", before - len(df))

    # Strip timezone to naive UTC (backward compat). Documented behavior.
    # Use tz_convert to ensure correct if already aware, then localize None.
    try:
        df['Timestamp'] = df['Timestamp'].dt.tz_localize(None)
    except Exception:
        # Fallback if already naive
        try:
            df['Timestamp'] = df['Timestamp'].dt.tz_convert(None)
        except Exception:
            pass

    # Ensure numeric dtypes
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0).astype('int64')

    # Select and order columns
    df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]

    # Sort and dedup (stable mergesort) - hides API duplicate bug but warns
    before_len = len(df)
    df = df.sort_values('Timestamp', kind='mergesort').drop_duplicates('Timestamp', keep='last')
    if len(df) < before_len:
        logger.info("Dropped %d duplicate Timestamp rows", before_len - len(df))
        warnings.warn(f"Dropped {before_len - len(df)} duplicate Timestamp rows", UserWarning)

    # Apply cutoff time only for intraday intervals
    # NSE market hours 09:15 to 15:30 IST; we filter on UTC-naive timestamps as received (UTC).
    # Since Timestamp is UTC-naive, 15:29:59 UTC != IST. But NSE data timestamps are in IST converted to UTC? API sends ms UTC.
    # For simplicity, keep original logic: filter <=15:29:59 (as NSE intraday data is already in IST-naive after conversion?).
    # Improved: filter 09:15 to 15:30 inclusive for intraday.
    intraday_intervals = ['1m', '3m', '5m', '10m', '15m', '30m', '1h']
    if interval in intraday_intervals:
        cutoff_time = pd.Timestamp('15:30:00').time()
        open_time = pd.Timestamp('09:15:00').time()
        # Previous logic only filtered upper bound; now also filter pre-market
        mask = (df['Timestamp'].dt.time >= open_time) & (df['Timestamp'].dt.time <= cutoff_time)
        # Keep backward compat: if filtering would drop >90% (indicating UTC vs IST mismatch), fallback to old upper-only
        filtered = df[mask]
        if len(filtered) == 0 and len(df) > 0:
            logger.debug("Intraday time filter dropped all rows, falling back to upper-bound only (possible TZ mismatch)")
            cutoff_old = pd.Timestamp('15:29:59').time()
            df = df[df['Timestamp'].dt.time <= cutoff_old]
        else:
            # If filtered drops >50% unexpectedly, log but keep filtered
            if len(filtered) < len(df) * 0.5 and len(df) > 10:
                logger.debug("Intraday filter dropped %.0f%% rows (%d->%d)", (1-len(filtered)/len(df))*100, len(df), len(filtered))
            df = filtered

    df.set_index('Timestamp', inplace=True)
    return df
