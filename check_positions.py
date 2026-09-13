# check_positions.py — runs every 5 minutes, checks open signals against live prices

from data_fetcher import fetch_candles
from positions import load_positions, save_positions, check_position
from telegram_sender import send_update


def run():
    positions = load_positions()
    open_symbols = [s for s, p in positions.items() if p.get("status") == "open"]

    if not open_symbols:
        print("No open positions to check.")
        return

    for symbol in open_symbols:
        df = fetch_candles(symbol)
        current_price = df.iloc[-1]["close"]

        events = check_position(symbol, positions[symbol], current_price)
        for event in events:
            send_update(event, positions[symbol])

    save_positions(positions)


if __name__ == "__main__":
    run()
