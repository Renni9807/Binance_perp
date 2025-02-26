# strategy.py
from patterns import (
    is_hammer, is_shooting_star,
    detect_double_top, detect_double_bottom
)
from config import MAX_CAPITAL_USAGE, PRICE_THRESHOLD, RISK_PER_TRADE, RISK_REWARD_RATIO, LEVERAGE

class TradingStrategy:
    def __init__(self, sr_tracker):
        self.sr_tracker = sr_tracker
        self.current_positions = []
    
    def analyze_candle(self, candle, trend):
        """Analyze current candle for trading signals."""
        signals = []
        
        # Update support/resistance levels
        self.sr_tracker.update_levels(candle)
        
        # Check for hammer in downtrend
        if trend == 'down' and is_hammer(candle, 'down'):
            signals.append({
                'type': 'buy',
                'pattern': 'hammer',
                'strength': 1
            })
        
        # Check for shooting star in uptrend
        if trend == 'up' and is_shooting_star(candle, 'up'):
            signals.append({
                'type': 'sell',
                'pattern': 'shooting_star',
                'strength': 1
            })
        
        # Check for double top with shooting star
        if detect_double_top(
            self.sr_tracker.resistance_levels,
            float(candle['high']),
            PRICE_THRESHOLD
        ) and is_shooting_star(candle, 'up'):
            signals.append({
                'type': 'sell',
                'pattern': 'double_top_shooting_star',
                'strength': 2
            })
        
        # Check for double bottom with hammer
        if detect_double_bottom(
            self.sr_tracker.support_levels,
            float(candle['low']),
            PRICE_THRESHOLD
        ) and is_hammer(candle, 'down'):
            signals.append({
                'type': 'buy',
                'pattern': 'double_bottom_hammer',
                'strength': 2
            })
        
        return signals
    
    def calculate_position_size(self, entry_price, stop_loss, balance, initial_balance):
        """Calculate position size based on risk management rules."""
        # Calculate maximum allowed capital based on initial balance
        max_allowed_capital = initial_balance * MAX_CAPITAL_USAGE
        
        # Calculate position size based on risk
        risk_amount = balance * RISK_PER_TRADE
        price_difference = abs(entry_price - stop_loss)
        position_size = (risk_amount / price_difference) * LEVERAGE
        
        # Calculate notional value of the position
        notional_value = position_size * entry_price
        
        # If notional value exceeds max allowed capital, reduce position size
        if notional_value > max_allowed_capital:
            position_size = max_allowed_capital / entry_price
            
        return position_size
    
    def calculate_take_profit(self, entry_price, stop_loss, position_type):
        """Calculate take profit level based on risk:reward ratio."""
        price_difference = abs(entry_price - stop_loss)
        
        if position_type == 'buy':
            return entry_price + (price_difference * RISK_REWARD_RATIO)
        else:
            return entry_price - (price_difference * RISK_REWARD_RATIO)
    
    def calculate_stop_loss(self, candle, position_type):
        """Calculate stop loss level based on candle properties."""
        if position_type == 'buy':
            return float(candle['low']) * 0.995  # 0.5% below low
        else:
            return float(candle['high']) * 1.005  # 0.5% above high