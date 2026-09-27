# main.py — runs both strategies each scan: Orion (existing tiered strategy)
# and Nova (prominence-engulfing), sharing the same fetched 1h candle data.

from config import SYMBOLS
from data_fetcher import fetch_all
from strategy import scan_all
from telegram_sender import send_all, send_engulf_signal
from positions import load_positions, save_positions, has_open_position, open_position

import engulf_strategy


def run():
    positions = load_positions()

    # Fetch once — both strategies read the same BTC/USDT 1h candle data
    data = fetch_all(SYMBOLS)
    if not data:
        print("No data fetched — exiting.")
        return

    # --- Orion: existing tiered strategy — untouched, works exactly as before ---
    if has_open_position(positions, "BTC/USDT"):
        print("Orion: BTC/USDT already has an open position — skipping.")
    else:
        signals = scan_all(data)
        if signals:
            print(f"Orion: found {len(signals)} setup(s). Sending to Telegram...")
            send_all(signals)
            for signal in signals:
                open_position(positions, signal)
        else:
            print("Orion: no setups found this scan.")

    # --- Nova: prominence-engulfing strategy ---
    df = data.get(engulf_strategy.MARKET_SYMBOL)
    if df is None or df.empty:
        print("Nova: no data available — skipping.")
    elif has_open_position(positions, engulf_strategy.POSITION_KEY):
        print("Nova: already has an open position — skipping.")
    else:
        nova_signal = engulf_strategy.scan(df)
        if not nova_signal:
            print("Nova: no setup found this scan.")
        else:
            existing = positions.get(engulf_strategy.POSITION_KEY)
            if existing and existing.get("last_signal_candle") == nova_signal["candle_time"]:
                print("Nova: already acted on this candle, skipping.")
            else:
                print(f"Nova: setup found — {nova_signal['direction']} at {nova_signal['entry']}")
                send_engulf_signal(nova_signal)
                open_position(positions, nova_signal)

    save_positions(positions)


if __name__ == "__main__":
    run()
