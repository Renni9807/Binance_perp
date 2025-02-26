# config.py
from datetime import datetime, timezone

# Trading Parameters
SYMBOL = "BTCUSDT"
TIMEFRAME = "5m"

# Date Ranges
IN_SAMPLE_START = datetime(2025, 1, 1, tzinfo=timezone.utc)
IN_SAMPLE_END = datetime(2025, 2, 1, tzinfo=timezone.utc)
OUT_OF_SAMPLE_START = datetime(2025, 2, 1, tzinfo=timezone.utc)
OUT_OF_SAMPLE_END = datetime(2025, 2, 23, tzinfo=timezone.utc)

# Risk Management Parameters
LEVERAGE = 3
RISK_REWARD_RATIO = 5  # Risk:Reward = 1:5
MAX_CAPITAL_USAGE = 0.3  # Maximum 30% of initial capital can be used
RISK_PER_TRADE = 0.01  # Risk 1% of balance per trade
MAX_POSITIONS = 3  # Maximum number of concurrent positions

# Bollinger Bands Parameters
CLOSE_BB_PERIOD = 20
CLOSE_BB_STD = 2
OPEN_BB_PERIOD = 4
OPEN_BB_STD = 4

# Support/Resistance Parameters
DEQUE_MAX_LEN = 100  # Maximum length for support/resistance levels storage
MIN_PATTERN_BARS = 5  # Minimum bars between pattern points
PRICE_THRESHOLD = 0.002  # 0.2% threshold for price comparison

# Candlestick Pattern Parameters
BODY_TO_SHADOW_RATIO = 2  # Minimum ratio of shadow to body for hammer/shooting star
DOJI_THRESHOLD = 0.1  # Maximum body size relative to total range for doji