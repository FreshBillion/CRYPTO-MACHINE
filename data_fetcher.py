# data_fetcher.py — pulls candle (OHLCV) data from Kraken

import ccxt
import pandas as pd
from config import CANDLE_LIMIT, TIMEFRAME

exchange = ccxt.kraken({
    "enableRateLimit": True,
})

def fetch_candles(symbol: str) -> pd.DataFrame:
    """
    Fetches the most recent OHLCV candles for a symbol (used for finding new setups).
    """
    raw = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=CANDLE_LIMIT)

    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)

    return df


def fetch_since(symbol: str, since_ms: int, timeframe: str = "15m") -> pd.DataFrame:
    """
    Fetches ALL candles for a symbol from since_ms (inclusive) up to now.
    Used to replay price history a position may have moved through between
    infrequent checks, so no TP/SL touch gets missed even if a check runs late.
    """
    all_candles = []
    while True:
        batch = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=500)
        if not batch:
            break
        all_candles.extend(batch)
        last_ts = batch[-1][0]
        if last_ts == since_ms or len(batch) < 500:
            break
        since_ms = last_ts + 1

    if not all_candles:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

    df = pd.DataFrame(all_candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.drop_duplicates(subset="timestamp", inplace=True)
    df.set_index("timestamp", inplace=True)

    return df


def fetch_all(symbols: list) -> dict:
    """
    Fetches recent candle data for a list of symbols (used by main.py's scan).
    """
    data = {}
    for symbol in symbols:
        try:
            data[symbol] = fetch_candles(symbol)
        except Exception as e:
            print(f"Failed to fetch {symbol}: {e}")
    return data
