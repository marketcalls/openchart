import warnings
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pandas as pd

from openchart.core import NSEData, InvalidIntervalError, InvalidSymbolTypeError


def test_timeframes_includes_3m():
    nse = NSEData()
    assert '3m' in nse.timeframes()
    assert '1m' in nse.timeframes()
    assert '1M' in nse.timeframes()
    nse.close()


def test_segments():
    nse = NSEData()
    assert set(nse.segments()) == {'IDX', 'EQ', 'FO'}
    assert nse.SEGMENTS['FO'] == 'Futures & Options'
    nse.close()


def test_search_invalid_symbol_type():
    nse = NSEData()
    with pytest.raises(TypeError):
        nse.search(None, 'EQ')
    with pytest.raises(ValueError):
        nse.search('', 'EQ')
    with pytest.raises(TypeError):
        nse.search(123, 'EQ')
    nse.close()


def test_search_invalid_segment_warns():
    nse = NSEData()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        df = nse.search('RELIANCE', 'INVALID')
        assert df.empty
        assert any("Invalid segment" in str(x.message) for x in w)
    nse.close()


def test_search_invalid_segment_type():
    nse = NSEData()
    with pytest.raises(TypeError):
        nse.search('RELIANCE', 123)
    nse.close()


def test_invalid_interval_raises():
    nse = NSEData()
    end = datetime.now()
    start = end - timedelta(days=5)
    with patch.object(nse, 'search', return_value=pd.DataFrame([{'symbol': 'RELIANCE-EQ', 'scripcode': '2885', 'description': 'x', 'type': 'Equity', 'exchange': 'NSE'}])):
        with pytest.raises(InvalidIntervalError):
            nse.historical('RELIANCE-EQ', 'EQ', start, end, '2m')
        with pytest.raises(InvalidIntervalError):
            nse.historical('RELIANCE-EQ', 'EQ', start, end, 'invalid')
        # case-insensitive 1d should work
        with patch.object(nse, '_fetch_historical', return_value=pd.DataFrame()) as mock_fetch:
            nse.historical('RELIANCE-EQ', 'EQ', start, end, '1D')
            mock_fetch.assert_called_once()
    nse.close()


def test_historical_start_greater_than_end_raises():
    nse = NSEData()
    end = datetime.now()
    start = end - timedelta(days=5)
    with pytest.raises(ValueError):
        nse.historical('RELIANCE-EQ', 'EQ', end, start, '1d')
    nse.close()


def test_historical_invalid_symbol_raises():
    nse = NSEData()
    with pytest.raises(TypeError):
        nse.historical(None, 'EQ')
    with pytest.raises(ValueError):
        nse.historical('', 'EQ')
    nse.close()


def test_historical_invalid_datetime_type():
    nse = NSEData()
    with pytest.raises(TypeError):
        nse.historical('RELIANCE-EQ', 'EQ', start="2024-01-01", end=datetime.now(), interval='1d')
    nse.close()


def test_historical_direct_invalid_symbol_type():
    nse = NSEData()
    end = datetime.now()
    start = end - timedelta(days=5)
    with pytest.raises(InvalidSymbolTypeError):
        nse.historical_direct(token='2885', symbol='RELIANCE-EQ', symbol_type='BAD', start=start, end=end)
    with pytest.raises(TypeError):
        nse.historical_direct(token=None, symbol='RELIANCE-EQ', symbol_type='Equity')
    with pytest.raises(ValueError):
        nse.historical_direct(token='', symbol='RELIANCE-EQ', symbol_type='Equity')
    nse.close()


def test_historical_direct_case_insensitive_symbol_type():
    nse = NSEData()
    with patch.object(nse, '_fetch_historical', return_value=pd.DataFrame()) as mock_fetch:
        nse.historical_direct(token='2885', symbol='RELIANCE-EQ', symbol_type='equity', start=None, end=None)
        args, kwargs = mock_fetch.call_args
        assert args[0]['type'] == 'Equity'
    nse.close()


def test_search_no_results_warns():
    nse = NSEData()
    mock_resp = Mock()
    mock_resp.json.return_value = {'status': False, 'data': None}
    mock_resp.raise_for_status = Mock()
    with patch.object(nse.session, 'get', return_value=mock_resp):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            df = nse.search('NONEXISTENT', 'EQ')
            assert df.empty
    nse.close()


def test_search_json_decode_error_handled():
    nse = NSEData()
    mock_resp = Mock()
    mock_resp.json.side_effect = ValueError("No JSON")
    mock_resp.text = "<html>403</html>"
    mock_resp.raise_for_status = Mock()
    with patch.object(nse.session, 'get', return_value=mock_resp):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            df = nse.search('RELIANCE', 'EQ')
            assert df.empty
    nse.close()


def test_fetch_historical_json_error_handled():
    nse = NSEData()
    mock_resp = Mock()
    mock_resp.json.side_effect = ValueError("bad json")
    mock_resp.text = "not json"
    mock_resp.raise_for_status = Mock()
    with patch.object(nse.session, 'get', return_value=mock_resp):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            df = nse._fetch_historical({'scripcode': '2885', 'symbol': 'RELIANCE-EQ', 'type': 'Equity'}, None, None, '1d')
            assert df.empty
    nse.close()


def test_symbol_resolution_warning_on_ambiguous():
    nse = NSEData()
    # Mock search to return 3 matches, no exact
    mock_df = pd.DataFrame([
        {'symbol': 'RCOM-BE', 'scripcode': '1', 'description': 'x', 'type': 'Equity', 'exchange': 'NSE'},
        {'symbol': 'RELCHEMQ-EQ', 'scripcode': '2', 'description': 'y', 'type': 'Equity', 'exchange': 'NSE'},
        {'symbol': 'RELIANCE-EQ', 'scripcode': '2885', 'description': 'z', 'type': 'Equity', 'exchange': 'NSE'},
    ])
    with patch.object(nse, 'search', return_value=mock_df):
        with patch.object(nse, '_fetch_historical', return_value=pd.DataFrame()) as mock_fetch:
            # Exact match should not warn
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                nse.historical('RELIANCE-EQ', 'EQ', interval='1d')
                assert not any("No exact match" in str(x.message) for x in w)
            # Non-exact with no -EQ fallback should warn
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                nse.historical('RELI', 'EQ', interval='1d')
                assert any("No exact match" in str(x.message) for x in w)
    nse.close()


def test_context_manager():
    with NSEData() as nse:
        assert nse.session is not None
    # after exit, session closed (no error on second close)
    nse.close()


def test_configurable_timeout_and_urls():
    nse = NSEData(timeout=5, search_url="https://example.com/search", historical_url="https://example.com/hist")
    assert nse.timeout == 5
    assert nse.search_url == "https://example.com/search"
    nse.close()


def test_large_intraday_range_warns():
    nse = NSEData()
    end = datetime.now()
    start = end - timedelta(days=200)
    mock_df = pd.DataFrame([{'symbol': 'RELIANCE-EQ', 'scripcode': '2885', 'description': 'x', 'type': 'Equity', 'exchange': 'NSE'}])
    with patch.object(nse, 'search', return_value=mock_df):
        with patch.object(nse, '_fetch_historical', return_value=pd.DataFrame()):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                nse.historical('RELIANCE-EQ', 'EQ', start, end, '5m')
                assert any("Large intraday range" in str(x.message) for x in w)
    nse.close()
