# strategy.py — scores each symbol against 4 confluence conditions and grades a tiered signal

import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from config import (
    EMA_FAST, EMA_SLOW, RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL, VOLUME_MA_PERIOD, VOLUME_MULTIPLIER,
    ATR_PERIOD, ATR_SL_MULTIPLIER, TP1_R, TP2_R, TP3_R,
    LEVEL_LABELS, MIN_CONDITIONS_TO_SIGNAL
)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df["ema_fast"] = EMAIndicator(df["close"], window=EMA_FAST).ema_indicator()
    df["ema_slow"] = EMAIndicator(df["close"], window=EMA_SLOW).ema_indicator()

    df["rsi"] = RSIIndicator(df["close"], window=RSI_PERIOD).rsi()

    macd = MACD(df["close"], window_fast=MACD_FAST, window_slow=MACD_SLOW, window_sign=MACD_SIGNAL)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    df["volume_ma"] = df["volume"].rolling(VOLUME_MA_PERIOD).mean()

    df["atr"] = AverageTrueRange(df["high"], df["low"], df["close"], window=ATR_PERIOD).average_true_range()

    return df


def score_direction(last, direction: str) -> tuple:
    """
    Checks all 4 conditions against one direction ("bull" or "bear").
    Returns (score, list_of_matched_condition_names).
    """
    matched = []

    if direction == "bull":
        if last["ema_fast"] > last["ema_slow"]:
            matched.append("Trend")
        if last["macd"] > last["macd_signal"]:
            matched.append("MACD")
        if 50 < last["rsi"] < RSI_OVERBOUGHT:
            matched.append("RSI")
    else:
        if last["ema_fast"] < last["ema_slow"]:
            matched.append("Trend")
        if last["macd"] < last["macd_signal"]:
            matched.append("MACD")
        if RSI_OVERSOLD < last["rsi"] < 50:
            matched.append("RSI")

    if last["volume"] > (last["volume_ma"] * VOLUME_MULTIPLIER):
        matched.append("Volume")

    return len(matched), matched


def check_setup(symbol: str, df: pd.DataFrame) -> dict | None:
    """
    Scores the most recent candle against both directions and returns
    the strongest tiered signal, or None if nothing meets the minimum bar.
    """
    df = add_indicators(df)
    df.dropna(inplace=True)
    if df.empty:
        return None

    last = df.iloc[-1]

    bull_score, bull_matched = score_direction(last, "bull")
    bear_score, bear_matched = score_direction(last, "bear")

    if bull_score == bear_score or max(bull_score, bear_score) < MIN_CONDITIONS_TO_SIGNAL:
        return None

    if bull_score > bear_score:
        direction, score, matched = "BUY", bull_score, bull_matched
    else:
        direction, score, matched = "SELL", bear_score, bear_matched

    entry = last["close"]
    atr = last["atr"]
    risk = atr * ATR_SL_MULTIPLIER  # this is "1R"

    if direction == "BUY":
        stop_loss = entry - risk
        tp1 = entry + (risk * TP1_R)
        tp2 = entry + (risk * TP2_R)
        tp3 = entry + (risk * TP3_R)
    else:
        stop_loss = entry + risk
        tp1 = entry - (risk * TP1_R)
        tp2 = entry - (risk * TP2_R)
        tp3 = entry - (risk * TP3_R)

    return {
        "symbol": symbol,
        "direction": direction,
        "level": LEVEL_LABELS.get(score, "B"),
        "conditions_met": matched,
        "entry": round(entry, 4),
        "stop_loss": round(stop_loss, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "tp3": round(tp3, 4),
        "rsi": round(last["rsi"], 1),
    }


def scan_all(data: dict) -> list:
    """
    Runs check_setup on every symbol's DataFrame.
    Returns a list of signal dicts (empty if nothing found this scan).
    """
    signals = []
    for symbol, df in data.items():
        result = check_setup(symbol, df)
        if result:
            signals.append(result)
    return signals
