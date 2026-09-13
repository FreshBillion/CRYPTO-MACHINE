# positions.py — shared logic for tracking open signals and checking TP/SL hits

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
    positions[signal["symbol"]] = {
        "status": "open",
        "direction": signal["direction"],
        "level": signal["level"],
        "entry": signal["entry"],
        "stop_loss": signal["stop_loss"],
        "tp1": signal["tp1"],
        "tp2": signal["tp2"],
        "tp3": signal["tp3"],
        "tp1_hit": False,
        "tp2_hit": False,
        "tp3_hit": False,
        "opened_at": datetime.utcnow().isoformat(),
    }


def check_position(symbol: str, pos: dict, current_price: float) -> list:
    """
    Compares current_price against a position's levels.
    Returns a list of event dicts for anything that just happened
    (tp1_hit, tp2_hit, tp3_hit, stop_loss, breakeven, expired).
    Mutates pos in place.
    """
    events = []
    is_buy = pos["direction"] == "BUY"

    def hit(target):
        return current_price >= target if is_buy else current_price <= target

    def stopped():
        return current_price <= pos["stop_loss"] if is_buy else current_price >= pos["stop_loss"]

    if stopped():
        pos["status"] = "closed"
        pos["closed_reason"] = "breakeven" if pos.get("tp2_hit") else "stop_loss"
        events.append({"type": pos["closed_reason"], "symbol": symbol, "price": current_price})
        return events

    if not pos["tp1_hit"] and hit(pos["tp1"]):
        pos["tp1_hit"] = True
        events.append({"type": "tp1_hit", "symbol": symbol, "price": current_price})

    if not pos["tp2_hit"] and hit(pos["tp2"]):
        pos["tp2_hit"] = True
        events.append({"type": "tp2_hit", "symbol": symbol, "price": current_price})
        if MOVE_SL_TO_BREAKEVEN_AFTER_TP2:
            pos["stop_loss"] = pos["entry"]
            events.append({"type": "breakeven_set", "symbol": symbol, "price": pos["entry"]})

    if not pos["tp3_hit"] and hit(pos["tp3"]):
        pos["tp3_hit"] = True
        pos["status"] = "closed"
        pos["closed_reason"] = "tp3_hit"
        events.append({"type": "tp3_hit", "symbol": symbol, "price": current_price})
        return events

    opened_at = datetime.fromisoformat(pos["opened_at"])
    if datetime.utcnow() - opened_at > timedelta(hours=POSITION_EXPIRY_HOURS):
        pos["status"] = "closed"
        pos["closed_reason"] = "expired"
        events.append({"type": "expired", "symbol": symbol, "price": current_price})

    return events
