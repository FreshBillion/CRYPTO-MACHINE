import requests
from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, TELEGRAM_PERSONAL_CHAT_ID,
    TP1_R, TP2_R, TP3_R
)


def _send(message: str, chat_id: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Telegram send failed ({chat_id}): {response.text}")
    return response.status_code == 200


def format_signal_public(signal: dict) -> str:
    emoji = "🟢" if signal["direction"] == "BUY" else "🔴"
    risk = signal["risk_dollars"]
    tp1_dollars = round(risk * TP1_R, 2)
    tp2_dollars = round(risk * TP2_R, 2)
    tp3_dollars = round(risk * TP3_R, 2)

    return (
        f"{emoji} *{signal['level']} SETUP — {signal['direction']}* — {signal['symbol']}\n\n"
        f"Entry: `{signal['entry']}`\n"
        f"Stop Loss: `{signal['stop_loss']}`  (risk: ${risk})\n"
        f"Position size: `{signal['position_size']}` {signal['symbol'].split('/')[0]}\n\n"
        f"TP1: `{signal['tp1']}`  (+${tp1_dollars})\n"
        f"TP2: `{signal['tp2']}`  (+${tp2_dollars})\n"
        f"TP3: `{signal['tp3']}`  (+${tp3_dollars})\n\n"
        f"RSI: {signal['rsi']}\n\n"
        f"_Not financial advice. Trade at your own risk._"
    )


def format_signal_private(signal: dict) -> str:
    conditions = ", ".join(signal["conditions_met"])
    return format_signal_public(signal) + f"\n\nConditions met: {conditions}"


def send_signal(signal: dict) -> bool:
    public_ok = _send(format_signal_public(signal), TELEGRAM_CHANNEL_ID)
    if TELEGRAM_PERSONAL_CHAT_ID:
        _send(format_signal_private(signal), TELEGRAM_PERSONAL_CHAT_ID)
    return public_ok


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
    "breakeven_set": None,
}

EVENT_R_MULTIPLES = {"tp1_hit": TP1_R, "tp2_hit": TP2_R, "tp3_hit": TP3_R}


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
    return _send(message, TELEGRAM_CHANNEL_ID)
