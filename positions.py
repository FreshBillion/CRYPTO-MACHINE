# positions.py — shared logic for tracking open signals and checking TP/SL hits
# by replaying candle history since the last check, not just the current price

import json
import os
from datetime import datetime, timedelta

from config import MOVE_SL_TO_BREAKEVEN_AFTER_TP2, POSITION_EXPIRY_HOURS

POSITIONS_FILE = "positions.json"


def load_positions() -> dict:
    if not os.path.exists(POSITIONS_FILE):
        return {}
    with open(POSITIONS_FILE, "r") as f:
        return json.load(f)


def save_positions(positions: dict) -> None:
    with open(POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=2, default=str)


def has_open_position(positions: dict, symbol: str) -> bool:
    return symbol in positions and positions[symbol].get("status") == "open"


def open_position(positions: dict, signal: dict) -> None:
    now = datetime.utcnow().isoformat()
    positions[signal["symbol"]] = {
        "status": "open",
        "direction": signal["direction"],
        "level": signal["level"],
        "entry": signal["entry"],
        "stop_loss": signal["stop_loss"],
        "tp1": signal["tp1"],
        "tp2": signal["tp2"],
        "tp3": signal["tp3"],
        "position_size": signal["position_size"],
        "risk_dollars": signal["risk_dollars"],
        "tp1_hit": False,
        "tp2_hit": False,
        "tp3_hit": False,
        "opened_at": now,
        "last_checked": now,
    }


def check_position(symbol: str, pos: dict, candles) -> list:
    """
    Replays every candle since the last check (oldest first), testing each one's
    high/low against the position's levels. This catches a TP or SL touch even
    if the check itself runs late and the price has since moved away again.
    Mutates pos in place. Returns a list of event dicts for anything that happened.
    """
    events = []
    is_buy = pos["direction"] == "BUY"

    for ts, candle in candles.iterrows():
        high, low = candle["high"], candle["low"]

        stopped = (low <= pos["stop_loss"]) if is_buy else (high >= pos["stop_loss"])
        if stopped:
            pos["status"] = "closed"
            pos["closed_reason"] = "breakeven" if pos.get("tp2_hit") else "stop_loss"
            events.append({"type": pos["closed_reason"], "symbol": symbol, "price": pos["stop_loss"]})
            pos["last_checked"] = ts.isoformat()
            return events

        if not pos["tp1_hit"]:
            touched = (high >= pos["tp1"]) if is_buy else (low <= pos["tp1"])
            if touched:
                pos["tp1_hit"] = True
                events.append({"type": "tp1_hit", "symbol": symbol, "price": pos["tp1"]})

        if not pos["tp2_hit"]:
            touched = (high >= pos["tp2"]) if is_buy else (low <= pos["tp2"])
            if touched:
                pos["tp2_hit"] = True
                events.append({"type": "tp2_hit", "symbol": symbol, "price": pos["tp2"]})
                if MOVE_SL_TO_BREAKEVEN_AFTER_TP2:
                    pos["stop_loss"] = pos["entry"]
                    events.append({"type": "breakeven_set", "symbol": symbol, "price": pos["entry"]})

        if not pos["tp3_hit"]:
            touched = (high >= pos["tp3"]) if is_buy else (low <= pos["tp3"])
            if touched:
                pos["tp3_hit"] = True
                pos["status"] = "closed"
                pos["closed_reason"] = "tp3_hit"
                events.append({"type": "tp3_hit", "symbol": symbol, "price": pos["tp3"]})
                pos["last_checked"] = ts.isoformat()
                return events

        pos["last_checked"] = ts.isoformat()

    opened_at = datetime.fromisoformat(pos["opened_at"])
    if datetime.utcnow() - opened_at > timedelta(hours=POSITION_EXPIRY_HOURS):
        last_price = candles.iloc[-1]["close"] if not candles.empty else pos["entry"]
        pos["status"] = "closed"
        pos["closed_reason"] = "expired"
        events.append({"type": "expired", "symbol": symbol, "price": last_price})

    return events
