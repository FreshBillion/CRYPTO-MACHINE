# main.py — the entry point. GitHub Actions runs this file on a schedule.

from config import SYMBOLS
from data_fetcher import fetch_all
from strategy import scan_all
from telegram_sender import send_all


def run():
    print(f"Scanning {len(SYMBOLS)} symbols: {', '.join(SYMBOLS)}")

    data = fetch_all(SYMBOLS)
    if not data:
        print("No data fetched — exiting.")
        return

    signals = scan_all(data)

    if signals:
        print(f"Found {len(signals)} setup(s). Sending to Telegram...")
        send_all(signals)
    else:
        print("No setups found this scan.")


if __name__ == "__main__":
    run()
