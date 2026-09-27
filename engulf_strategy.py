# engulf_strategy.py — "Nova": prominence-filtered engulfing pattern for BTC/USDT.
# Runs alongside the existing tiered strategy (strategy.py), sharing the same
# fetched candle data, but tracked as a fully separate, non-colliding position.

import numpy as np
from scipy.signal import find_peaks

from config import (
    ENGULF_PROMINENCE_THRESHOLD, ENGULF_MIN_ENGULF_RATIO, ENGULF_LOT_SIZE,
    ENGULF_SL_DOLLARS, ENGULF_TP1_DOLLARS, ENGULF_TP2_DOLLARS, ENGULF_TP3_DOLLARS,
    STRATEGY_NAME_ENGULF
)

POSITION_KEY = "BTC/USDT-NOVA"   # distinct tracking key — never collides with Orion's "BTC/USDT"
MARKET_SYMBOL = "BTC/USDT"       # the real symbol used for fetching data


def _compute_prominence(values):
    peaks, props = find_peaks(values, distance=1, prominence=0)
    prom = np.zeros(len(values))
    prom[peaks] = props["prominences"]
    return prom


def scan(df) -> dict | None:
    if len(df) < 10:
        return None

    high_prom = _compute_prominence(df["high"].values)
    low_prom = _compute_prominence(-df["low"].values)

    i = len(df) - 1
    c1_open, c1_close = df["open"].iloc[i], df["close"].iloc[i]
    c2_open, c2_close = df["open"].iloc[i - 1], df["close"].iloc[i - 1]
    c1_body = abs(c1_close - c1_open)
    c2_body = abs(c2_close - c2_open)

    if c2_body == 0 or c1_body < ENGULF_MIN_ENGULF_RATIO * c2_body:
        return None

    candle_time = df.index[i].isoformat()
    entry = c1_close

    sl_dist = ENGULF_SL_DOLLARS / ENGULF_LOT_SIZE
    tp1_dist = ENGULF_TP1_DOLLARS / ENGULF_LOT_SIZE
    tp2_dist = ENGULF_TP2_DOLLARS / ENGULF_LOT_SIZE
    tp3_dist = ENGULF_TP3_DOLLARS / ENGULF_LOT_SIZE

    direction = None
    if c2_close > c2_open and c1_close < c1_open:
        if c1_open >= c2_close and c1_close <= c2_open:
            if max(high_prom[i - 1], high_prom[i]) >= ENGULF_PROMINENCE_THRESHOLD:
                direction = "SELL"

    if direction is None and c2_close < c2_open and c1_close > c1_open:
        if c1_open <= c2_close and c1_close >= c2_open:
            if max(low_prom[i - 1], low_prom[i]) >= ENGULF_PROMINENCE_THRESHOLD:
                direction = "BUY"

    if direction is None:
        return None

    is_buy = direction == "BUY"
    stop_loss = entry - sl_dist if is_buy else entry + sl_dist
    tp1 = entry + tp1_dist if is_buy else entry - tp1_dist
    tp2 = entry + tp2_dist if is_buy else entry - tp2_dist
    tp3 = entry + tp3_dist if is_buy else entry - tp3_dist

    return {
        "symbol": POSITION_KEY,
        "market_symbol": MARKET_SYMBOL,
        "strategy_name": STRATEGY_NAME_ENGULF,
        "direction": direction,
        "entry": round(entry, 2),
        "stop_loss": round(stop_loss, 2),
        "tp1": round(tp1, 2),
        "tp2": round(tp2, 2),
        "tp3": round(tp3, 2),
        "candle_time": candle_time,
    }
