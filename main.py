# main.py — entry point for the 15-minute scan. Skips symbols with an open position.

from config import SYMBOLS
from data_fetcher import fetch_all
from strategy import scan_all
from telegram_sender import send_all
from positions import load_positions, save_positions, has_open_position, open_position


def run():
    positions = load_positions()
    symbols_to_scan = [s for s in SYMBOLS if not has_open_position(positions, s)]

    if not symbols_to_scan:
        print("All symbols already have an open position — skipping scan.")
        return

    print(f"Scanning {len(symbols_to_scan)} symbols: {', '.join(symbols_to_scan)}")

    data = fetch_all(symbols_to_scan)
    if not data:
        print("No data fetched — exiting.")
        return

    signals = scan_all(data)

    if signals:
        print(f"Found {len(signals)} setup(s). Sending to Telegram...")
        send_all(signals)
        for signal in signals:
            open_position(positions, signal)
        save_positions(positions)
    else:
        print("No setups found this scan.")


if __name__ == "__main__":
    run()
