# config.py — all settings in one place, edit these before running

# Telegram
TELEGRAM_BOT_TOKEN = "8997923326:AAG8z6UbVmfqzbfBiFftgBwAa9_j8vjtosY"   # get from @BotFather on Telegram
TELEGRAM_CHANNEL_ID = "-1004473205109" # or numeric chat id like -1001234567890

# Markets to scan (Binance symbols)
SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

# Timeframe
TIMEFRAME = "1h"        # candle size
CANDLE_LIMIT = 250      # how many candles to pull each scan (need 200+ for EMA200)

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
VOLUME_MULTIPLIER = 1.5   # current volume must be 1.5x the 20-period average

# Risk management
ATR_PERIOD = 14
ATR_SL_MULTIPLIER = 1.5   # stop loss = entry ± 1.5x ATR
ATR_TP_MULTIPLIER = 3.0   # take profit = entry ± 3x ATR (2:1 reward:risk)
