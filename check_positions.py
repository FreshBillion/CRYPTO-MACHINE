# check_positions.py — checks open positions by replaying candle history since the last check

from datetime import datetime

from data_fetcher import fetch_since
from positions import load_positions, save_positions, check_position
from telegram_sender import send_update
from config import POSITION_CHECK_TIMEFRAME


def run():
    positions = load_positions()
    open_symbols = [s for s, p in positions.items() if p.get("status") == "open"]

    if not open_symbols:
        print("No open positions to check.")
        return

    for symbol in open_symbols:
        pos = positions[symbol]
        last_checked = pos.get("last_checked", pos["opened_at"])
        since_ms = int(datetime.fromisoformat(last_checked).timestamp() * 1000) + 1

        candles = fetch_since(symbol, since_ms, timeframe=POSITION_CHECK_TIMEFRAME)
        if candles.empty:
            print(f"{symbol}: no new candles since last check.")
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
