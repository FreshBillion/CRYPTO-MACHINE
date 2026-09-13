# data_fetcher.py — pulls candle (OHLCV) data from Bybit

import ccxt
import pandas as pd
from config import CANDLE_LIMIT, TIMEFRAME

# Bybit public endpoints don't require an API key for market data
exchange = ccxt.bybit({
    "enableRateLimit": True,   # avoids getting temporarily blocked for too many requests
})

def fetch_candles(symbol: str) -> pd.DataFrame:
    """
    Fetches recent OHLCV candles for a symbol and returns them as a DataFrame.
    Columns: timestamp, open, high, low, close, volume
    """
    raw = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=CANDLE_LIMIT)

    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)

    return df


def fetch_all(symbols: list) -> dict:
    """
    Fetches candle data for a list of symbols.
    Returns a dict: {symbol: DataFrame}
    """
    data = {}
    for symbol in symbols:
        try:
            data[symbol] = fetch_candles(symbol)
        except Exception as e:
            print(f"Failed to fetch {symbol}: {e}")
    return data
