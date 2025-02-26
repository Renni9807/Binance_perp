# patterns.py
from config import BODY_TO_SHADOW_RATIO, DOJI_THRESHOLD

def calculate_candle_properties(candle):
    """Calculate basic properties of a candlestick."""
    open_price = float(candle['open'])
    high_price = float(candle['high'])
    low_price = float(candle['low'])
    close_price = float(candle['close'])
    
    body_size = abs(close_price - open_price)
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    total_range = high_price - low_price
    
    is_bullish = close_price > open_price
    
    return {
        'body_size': body_size,
        'upper_shadow': upper_shadow,
        'lower_shadow': lower_shadow,
        'total_range': total_range,
        'is_bullish': is_bullish
    }

def is_hammer(candle, trend='down'):
    """Identify hammer pattern (including hanging man in uptrend)."""
    props = calculate_candle_properties(candle)
    
    if props['total_range'] == 0:
        return False
    
    body_ratio = props['body_size'] / props['total_range']
    
    # Check for hammer characteristics
    is_hammer = (
        props['lower_shadow'] > props['body_size'] * BODY_TO_SHADOW_RATIO and
        props['upper_shadow'] < props['body_size'] and
        body_ratio < 0.5
    )
    
    if trend == 'down':
        # In downtrend, hammer is bullish signal
        return is_hammer
    else:
        # In uptrend, hammer becomes hanging man (bearish signal)
        return is_hammer

def is_shooting_star(candle, trend='up'):
    """Identify shooting star pattern (including inverted hammer in downtrend)."""
    props = calculate_candle_properties(candle)
    
    if props['total_range'] == 0:
        return False
    
    body_ratio = props['body_size'] / props['total_range']
    
    # Check for shooting star characteristics
    is_star = (
        props['upper_shadow'] > props['body_size'] * BODY_TO_SHADOW_RATIO and
        props['lower_shadow'] < props['body_size'] and
        body_ratio < 0.5
    )
    
    if trend == 'up':
        # In uptrend, shooting star is bearish signal
        return is_star and not props['is_bullish']
    else:
        # In downtrend, inverted hammer can be bullish signal
        return is_star and props['is_bullish']

def detect_double_top(resistance_levels, current_high, price_threshold):
    """Detect double top pattern using resistance levels."""
    if len(resistance_levels) < 2:
        return False
    
    recent_resistance = resistance_levels[-1]
    previous_resistance = resistance_levels[-2]
    
    price_diff = abs(current_high - previous_resistance) / previous_resistance
    
    return price_diff <= price_threshold

def detect_double_bottom(support_levels, current_low, price_threshold):
    """Detect double bottom pattern using support levels."""
    if len(support_levels) < 2:
        return False
    
    recent_support = support_levels[-1]
    previous_support = support_levels[-2]
    
    price_diff = abs(current_low - previous_support) / previous_support
    
    return price_diff <= price_threshold