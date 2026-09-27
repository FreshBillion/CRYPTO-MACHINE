# check_positions.py — checks open positions by replaying candle history since the last
# confirmed checkpoint (strictly forward only). Uses each position's stored
# market_symbol (the real exchange pair) for fetching prices — the dict key itself
# may be a strategy-specific tracking key (e.g. Nova's "BTC/USDT-NOVA"), which isn't
# a real tradeable symbol on its own.

from datetime import datetime, timedelta

from data_fetcher import fetch_since
from positions import load_positions, save_positions, check_position
from telegram_sender import send_update
from config import POSITION_CHECK_TIMEFRAME


def _timeframe_to_timedelta(tf: str) -> timedelta:
    unit = tf[-1]
    value = int(tf[:-1])
    if unit == "h":
        return timedelta(hours=value)
    if unit == "d":
        return timedelta(days=value)
    return timedelta(minutes=value)


def _drop_forming_candle(candles, timeframe: str):
    if candles.empty:
        return candles
    duration = _timeframe_to_timedelta(timeframe)
    last_candle_end = candles.index[-1] + duration
    if datetime.utcnow() >= last_candle_end:
        return candles
    return candles.iloc[:-1]


def run():
    positions = load_positions()
    open_symbols = [s for s, p in positions.items() if p.get("status") == "open"]

    if not open_symbols:
        print("No open positions to check.")
        return

    for symbol in open_symbols:
        pos = positions[symbol]
        market_symbol = pos.get("market_symbol", symbol)

        last_checked_ms = int(datetime.fromisoformat(pos.get("last_checked", pos["opened_at"])).timestamp() * 1000)
        since_ms = last_checked_ms + 1

        candles = fetch_since(market_symbol, since_ms, timeframe=POSITION_CHECK_TIMEFRAME)
        candles = _drop_forming_candle(candles, POSITION_CHECK_TIMEFRAME)

        if candles.empty:
            print(f"{symbol}: no new closed candles since last check.")
            continue

        events = check_position(symbol, pos, candles)
        for event in events:
            send_update(event, pos)

        if events:
            print(f"{symbol}: {[e['type'] for e in events]}")
        else:
            print(f"{symbol}: no TP/SL touched in this window.")

    save_positions(positions)


if __name__ == "__main__":
    run()
