# telegram_sender.py — formats and sends signals + follow-up updates to Telegram

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, TP1_R, TP2_R, TP3_R


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
    risk = signal["risk_dollars"]

    tp1_dollars = round(risk * TP1_R, 2)
    tp2_dollars = round(risk * TP2_R, 2)
    tp3_dollars = round(risk * TP3_R, 2)

    return (
        f"{emoji} *{signal['level']} SETUP — {signal['direction']}* — {signal['symbol']}\n\n"
        f"Entry: `{signal['entry']}`\n"
        f"Stop Loss: `{signal['stop_loss']}`  (risk: ${risk})\n"
        f"Position size: `{signal['position_size']}` BTC\n\n"
        f"TP1: `{signal['tp1']}`  (+${tp1_dollars})\n"
        f"TP2: `{signal['tp2']}`  (+${tp2_dollars})\n"
        f"TP3: `{signal['tp3']}`  (+${tp3_dollars})\n\n"
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
    "breakeven_set": None,   # informational only, folded into the tp2_hit message
}

EVENT_R_MULTIPLES = {
    "tp1_hit": TP1_R,
    "tp2_hit": TP2_R,
    "tp3_hit": TP3_R,
}


def send_update(event: dict, pos: dict) -> bool:
    if EVENT_MESSAGES.get(event["type"]) is None:
        return True

    header = EVENT_MESSAGES[event["type"]]
    risk = pos.get("risk_dollars", 0)

    extra = ""
    if event["type"] in EVENT_R_MULTIPLES:
        dollars = round(risk * EVENT_R_MULTIPLES[event["type"]], 2)
        extra = f"  (+${dollars})"
    elif event["type"] == "stop_loss":
        extra = f"  (-${risk})"

    message = (
        f"{header}{extra}\n\n"
        f"{event['symbol']} — {pos['level']} setup — {pos['direction']}\n"
        f"Entry: `{pos['entry']}`\n"
        f"Price now: `{round(event['price'], 4)}`"
    )
    return _send(message)
