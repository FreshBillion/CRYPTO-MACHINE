# telegram_sender.py — formats and sends signals + follow-up updates to Telegram

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID


def _send(message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Telegram send failed: {response.text}")
    return response.status_code == 200


def format_signal(signal: dict) -> str:
    emoji = "🟢" if signal["direction"] == "BUY" else "🔴"
    conditions = ", ".join(signal["conditions_met"])
    return (
        f"{emoji} *{signal['level']} SETUP — {signal['direction']}* — {signal['symbol']}\n\n"
        f"Entry: `{signal['entry']}`\n"
        f"Stop Loss: `{signal['stop_loss']}`\n"
        f"TP1: `{signal['tp1']}`\n"
        f"TP2: `{signal['tp2']}`\n"
        f"TP3: `{signal['tp3']}`\n\n"
        f"RSI: {signal['rsi']}\n"
        f"Conditions met: {conditions}\n\n"
        f"_Not financial advice. Trade at your own risk._"
    )


def send_signal(signal: dict) -> bool:
    return _send(format_signal(signal))


def send_all(signals: list) -> None:
    for signal in signals:
        send_signal(signal)


EVENT_MESSAGES = {
    "tp1_hit": "🎯 *TP1 HIT*",
    "tp2_hit": "🎯 *TP2 HIT* — stop moved to breakeven",
    "tp3_hit": "🏁 *TP3 HIT — Trade closed, full target reached*",
    "stop_loss": "🛑 *STOP LOSS HIT — Trade closed*",
    "breakeven": "⚪ *Stopped at breakeven — Trade closed, no loss*",
    "expired": "⌛ *Signal expired — closed with no TP or SL hit*",
    "breakeven_set": None,   # informational only, folded into the tp2_hit message, not sent separately
}


def send_update(event: dict, pos: dict) -> bool:
    if EVENT_MESSAGES.get(event["type"]) is None:
        return True   # skip silent/internal events

    header = EVENT_MESSAGES[event["type"]]
    message = (
        f"{header}\n\n"
        f"{event['symbol']} — {pos['level']} setup — {pos['direction']}\n"
        f"Entry: `{pos['entry']}`\n"
        f"Price now: `{round(event['price'], 4)}`"
    )
    return _send(message)
