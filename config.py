import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# Markets to scan (Binance-style symbols, fetched via Kraken)
SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

# Timeframe
TIMEFRAME = "1h"
CANDLE_LIMIT = 250

# Strategy thresholds
EMA_FAST = 50
EMA_SLOW = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
VOLUME_MA_PERIOD = 20
VOLUME_MULTIPLIER = 1.5

# Risk management
ATR_PERIOD = 14
ATR_SL_MULTIPLIER = 1.5   # stop-loss distance = 1.5x ATR (this defines "1R")

# Take-profit targets, as multiples of R (R = the stop-loss distance)
TP1_R = 1.0
TP2_R = 2.0
TP3_R = 3.0

# Signal tiers — how many of the 4 conditions (trend, MACD, RSI, volume) must align
LEVEL_LABELS = {
    4: "A+",   # all 4 conditions
    3: "A",    # 3 of 4
    2: "B",    # 2 of 4
}
MIN_CONDITIONS_TO_SIGNAL = 2   # below this, stay silent

# After TP1 hits, move the stop-loss to entry (breakeven) to protect the trade
MOVE_SL_TO_BREAKEVEN_AFTER_TP2 = True

# Auto-close a signal as "expired" if neither a TP nor the SL is hit within this window
POSITION_EXPIRY_HOURS = 48
