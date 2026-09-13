# telegram_sender.py — formats a signal and sends it to your Telegram channel

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID


def format_signal(signal: dict) -> str:
    emoji = "🟢" if signal["signal"] == "BUY" else "🔴"
    return (
        f"{emoji} *{signal['signal']} SIGNAL* — {signal['symbol']}\n\n"
        f"Entry: `{signal['entry']}`\n"
        f"Stop Loss: `{signal['stop_loss']}`\n"
        f"Take Profit: `{signal['take_profit']}`\n"
        f"RSI: {signal['rsi']}\n\n"
        f"_Not financial advice. Trade at your own risk._"
    )


def send_signal(signal: dict) -> bool:
    """
    Sends one formatted signal to the Telegram channel.
    Returns True if Telegram confirms it was sent, False otherwise.
    """
    message = format_signal(signal)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"Sent signal for {signal['symbol']}")
        return True
    else:
        print(f"Failed to send {signal['symbol']}: {response.text}")
        return False


def send_all(signals: list) -> None:
    for signal in signals:
        send_signal(signal)
