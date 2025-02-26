# indicators.py
import pandas as pd
import numpy as np
from collections import deque
from config import (
    CLOSE_BB_PERIOD, CLOSE_BB_STD,
    OPEN_BB_PERIOD, OPEN_BB_STD,
    DEQUE_MAX_LEN
)

def calculate_bollinger_bands(data, column, period, std_dev):
    """Calculate Bollinger Bands without look-ahead bias."""
    # Use expanding window instead of rolling to avoid look-ahead bias
    expanding_mean = data[column].expanding(min_periods=period).mean()
    expanding_std = data[column].expanding(min_periods=period).std()
    
    sma = expanding_mean.shift(1)  # Shift to avoid look-ahead bias
    std = expanding_std.shift(1)   # Shift to avoid look-ahead bias
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return sma, upper_band, lower_band

class SupportResistanceTracker:
    def __init__(self, max_len=DEQUE_MAX_LEN, lookback_period=20):
        self.support_levels = deque(maxlen=max_len)
        self.resistance_levels = deque(maxlen=max_len)
        self.lookback_period = lookback_period
        self.price_history = deque(maxlen=lookback_period)
        self.support_touches = {}
        self.resistance_touches = {}
    
    def update_levels(self, candle):
        """Update support and resistance levels using only past data."""
        high = float(candle['high'])
        low = float(candle['low'])
        timestamp = pd.to_datetime(candle['timestamp'])
        
        # Add current prices to history but don't use them for level identification
        self.price_history.append({
            'high': high,
            'low': low,
            'timestamp': timestamp
        })
        
        if len(self.price_history) < 3:  # Need at least 3 candles for pattern
            return
        
        # Use only past data for level identification
        past_highs = [p['high'] for p in list(self.price_history)[:-1]]
        past_lows = [p['low'] for p in list(self.price_history)[:-1]]
        
        # Look for local maxima and minima in past data
        if len(past_highs) >= 3:
            # Check if second-to-last point is a local maximum
            if past_highs[-2] > past_highs[-3] and past_highs[-2] > past_highs[-1]:
                level = past_highs[-2]
                if not self._is_level_exists(level, self.resistance_levels):
                    self.resistance_levels.append(level)
                    self.resistance_touches[level] = 1
            
            # Check if second-to-last point is a local minimum
            if past_lows[-2] < past_lows[-3] and past_lows[-2] < past_lows[-1]:
                level = past_lows[-2]
                if not self._is_level_exists(level, self.support_levels):
                    self.support_levels.append(level)
                    self.support_touches[level] = 1
        
        # Update level touches using current candle
        self._update_level_touches(high, low, timestamp)
        
        # Remove weak levels
        self._remove_weak_levels(timestamp)
    
    def _identify_new_levels(self):
        """Identify new support and resistance levels."""
        highs = [p['high'] for p in self.price_history]
        lows = [p['low'] for p in self.price_history]
        
        # Look for local maxima and minima
        for i in range(1, len(self.price_history) - 1):
            # Potential resistance level
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                level = highs[i]
                if not self._is_level_exists(level, self.resistance_levels):
                    self.resistance_levels.append(level)
                    self.resistance_touches[level] = 1
            
            # Potential support level
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                level = lows[i]
                if not self._is_level_exists(level, self.support_levels):
                    self.support_levels.append(level)
                    self.support_touches[level] = 1
    
    def _update_level_touches(self, high, low, timestamp):
        """Update the number of times price touches each level."""
        touch_threshold = 0.001  # 0.1% threshold for level touch
        
        # Check resistance touches
        for level in list(self.resistance_levels):
            if abs(high - level) / level <= touch_threshold:
                self.resistance_touches[level] = self.resistance_touches.get(level, 0) + 1
        
        # Check support touches
        for level in list(self.support_levels):
            if abs(low - level) / level <= touch_threshold:
                self.support_touches[level] = self.support_touches.get(level, 0) + 1
    
    def _remove_weak_levels(self, current_time):
        """Remove levels that haven't been touched recently."""
        min_touches = 2  # Minimum number of touches required
        
        # Remove weak resistance levels
        for level in list(self.resistance_levels):
            if self.resistance_touches.get(level, 0) < min_touches:
                self.resistance_levels.remove(level)
                self.resistance_touches.pop(level, None)
        
        # Remove weak support levels
        for level in list(self.support_levels):
            if self.support_touches.get(level, 0) < min_touches:
                self.support_levels.remove(level)
                self.support_touches.pop(level, None)
    
    def _is_level_exists(self, new_level, levels, threshold=0.001):
        """Check if a similar price level already exists."""
        for level in levels:
            if abs(new_level - level) / level <= threshold:
                return True
        return False
    
    def get_nearest_levels(self, price):
        """Get nearest support and resistance levels."""
        support = None
        resistance = None
        
        # Find nearest support
        supports_below = [s for s in self.support_levels if s < price]
        if supports_below:
            support = max(supports_below)
        
        # Find nearest resistance
        resistances_above = [r for r in self.resistance_levels if r > price]
        if resistances_above:
            resistance = min(resistances_above)
        
        return support, resistance

def add_indicators(df):
    """Add all technical indicators to the dataframe."""
    # Calculate Bollinger Bands for close prices
    df['close_sma'], df['close_upper_band'], df['close_lower_band'] = \
        calculate_bollinger_bands(df, 'close', CLOSE_BB_PERIOD, CLOSE_BB_STD)
    
    # Calculate Bollinger Bands for open prices
    df['open_sma'], df['open_upper_band'], df['open_lower_band'] = \
        calculate_bollinger_bands(df, 'open', OPEN_BB_PERIOD, OPEN_BB_STD)
    
    # Calculate trend based on close SMA
    df['trend'] = np.where(
        df['close'] > df['close_sma'].shift(1),  # Use shifted SMA to avoid look-ahead bias
        'up',
        'down'
    )
    
    return df