import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# Markets to scan
SYMBOLS = ["BTC/USDT"]

# Timeframe
TIMEFRAME = "1h"
CANDLE_LIMIT = 250

# Timeframe used specifically for checking open positions
POSITION_CHECK_TIMEFRAME = "15m"

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

# Stop-loss distance is ATR-based, but floored and capped as a % of price so it
# can't collapse to noise-level in quiet markets or blow out in wild ones
ATR_PERIOD = 14
ATR_SL_MULTIPLIER = 1.5
MIN_SL_PERCENT = 0.0015   # 0.15% of entry price
MAX_SL_PERCENT = 0.015    # 1.5% of entry price

# Take-profit targets, as multiples of the stop-loss distance (R) — these now
# scale with volatility the same way the stop does
TP1_R = 1.0
TP2_R = 2.0
TP3_R = 3.0

# Dollar risk per trade, based on signal strength — the bot sizes the position
# so the stop-loss distance above equals exactly this many dollars
RISK_DOLLARS_BY_LEVEL = {
    "A+": 7,
    "A": 6,
    "B": 5,
}

# Signal tiers — how many of the 4 conditions (trend, MACD, RSI, volume) must align
LEVEL_LABELS = {
    4: "A+",
    3: "A",
    2: "B",
}
MIN_CONDITIONS_TO_SIGNAL = 2

# After TP2 hits, move the stop-loss to entry (breakeven)
MOVE_SL_TO_BREAKEVEN_AFTER_TP2 = True

# Auto-close a signal as "expired" if neither a TP nor the SL is hit within this window
POSITION_EXPIRY_HOURS = 48
