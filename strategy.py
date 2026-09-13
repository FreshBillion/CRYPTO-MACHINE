# strategy.py — checks each symbol's data for a valid trade setup

import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from config import (
    EMA_FAST, EMA_SLOW, RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL, VOLUME_MA_PERIOD, VOLUME_MULTIPLIER,
    ATR_PERIOD, ATR_SL_MULTIPLIER, ATR_TP_MULTIPLIER
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


def check_setup(symbol: str, df: pd.DataFrame) -> dict | None:
    """
    Looks at the most recent candle for a confluence setup:
    trend (EMA) + momentum (RSI) + confirmation (MACD crossover) + volume spike.
    Returns a signal dict if all conditions align, otherwise None.
    """
    df = add_indicators(df)
    df.dropna(inplace=True)
    if len(df) < 2:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    volume_spike = last["volume"] > (last["volume_ma"] * VOLUME_MULTIPLIER)
    macd_bull_cross = prev["macd"] <= prev["macd_signal"] and last["macd"] > last["macd_signal"]
    macd_bear_cross = prev["macd"] >= prev["macd_signal"] and last["macd"] < last["macd_signal"]

    uptrend = last["ema_fast"] > last["ema_slow"]
    downtrend = last["ema_fast"] < last["ema_slow"]

    entry = last["close"]
    atr = last["atr"]

    # BUY setup: uptrend + bullish MACD cross + RSI not overbought + volume confirms
    if uptrend and macd_bull_cross and last["rsi"] < RSI_OVERBOUGHT and volume_spike:
        return {
            "symbol": symbol,
            "signal": "BUY",
            "entry": round(entry, 4),
            "stop_loss": round(entry - (atr * ATR_SL_MULTIPLIER), 4),
            "take_profit": round(entry + (atr * ATR_TP_MULTIPLIER), 4),
            "rsi": round(last["rsi"], 1),
        }

    # SELL setup: downtrend + bearish MACD cross + RSI not oversold + volume confirms
    if downtrend and macd_bear_cross and last["rsi"] > RSI_OVERSOLD and volume_spike:
        return {
            "symbol": symbol,
            "signal": "SELL",
            "entry": round(entry, 4),
            "stop_loss": round(entry + (atr * ATR_SL_MULTIPLIER), 4),
            "take_profit": round(entry - (atr * ATR_TP_MULTIPLIER), 4),
            "rsi": round(last["rsi"], 1),
        }

    return None


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
