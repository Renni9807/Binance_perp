### Following rigorous methodologies to avoid Look Ahead bias & Data Snooping bias 
(based on principles from "Algorithmic Trading: Winning Strategies and Their Rationale" by Dr. Ernest P. Chan)

## 🚨 Comprehensive Risk Management (Detailed)

### 📌 Position sizing logic
Positions are strictly sized based on two constraints (using the smaller value):
- **Maximum capital usage per trade**: Limited to **30% of initial capital**.

Final position size = **min(Risk-based size, Capital limit size)**

### 📌 Stop-loss & take-profit calculation
- **Stop-loss**: 
- Long: 0.5% below recent candle low  
- Short: 0.5% above recent candle high
- **Take-profit**: 
- Fixed Risk-Reward ratio of **1:5**.

### 📌 Leverage & concurrent positions
- Fixed leverage at **3×**
- Maximum **3 concurrent positions** at any time.

### 📌 Realistic trading costs & conditions
- **Slippage** simulated at an average of **0.05% per trade**
- **Exchange fees**: Maker (**0.02%**), Taker (**0.04%**)
- **Funding fees** applied every **8 hours** at **0.00333%** per interval (daily rate 0.01%)

---

## 📊 Realistic Backtesting & Performance Analysis
- Accurate historical data fetched from real exchanges (Binance via CCXT)
- Detailed metrics including Sharpe Ratio, Profit Factor, Max Drawdown, and more
- Visualization of equity curves, cumulative returns, fees analysis, and pattern-based performance

---

- **Risk per trade**: Limited to **1% of current account balance** per trade.

## ⚙️ Simplified Strategy Description

The strategy systematically identifies trading opportunities based on:

- Automated identification of critical support and resistance price levels.
- Candlestick pattern analysis for precise entry signals.
- Trend detection using customized Bollinger Bands parameters.

(**Detailed proprietary strategy logic intentionally omitted.**)

2025 1/1 ~ 2025 1/31 (in-sample data period)

![backtest_comparison](https://github.com/user-attachments/assets/0d0cd9eb-de11-4c1b-9c30-dd6601610e7f)

![BTCUSDT_5m_20250101_20250131_UTC_in_sample_chart](https://github.com/user-attachments/assets/15de9183-b3c7-4c59-95be-48a79a911bdc)
![in_sample_trade_results](https://github.com/user-attachments/assets/1065efce-5927-47ba-9cb1-5447086cb46e)

2025 2/1 ~ 2025 2/22 (out-sample data period)
![BTCUSDT_5m_20250201_20250222_UTC_out_of_sample_chart](https://github.com/user-attachments/assets/f75906ab-afa9-440c-b1c5-806303ae5305)
![out_of_sample_trade_results](https://github.com/user-attachments/assets/e387a38c-c565-4d74-ac00-6066d09dc5ff)


# Backtest Visualization Module

This module provides various functions for visualizing backtest results.

## Installation

1. Save the `visualizer.py` file in the same directory as your backtest code.
2. Update the `main` function in your `backtest.py` file with the provided code, or add only the necessary sections.

## Key Features

### 1. Equity Curve Visualization
```python
visualize_equity_curve(backtester, title="Equity Curve", save_path=None)
```
- Displays a graph showing account balance changes during the backtest period.
- Saves the image file if `save_path` is set.

### 2. Trade Results Visualization
```python
visualize_trade_results(backtester, title="Trade Results", save_path=None)
```
- Displays cumulative profits and individual trade profits/losses as a graph.
- Profitable trades are shown in green, losses in red.

### 3. Trade Pattern Analysis
```python
visualize_trade_patterns(backtester, title="Trade Patterns Analysis", save_path=None)
```
- Analyzes and displays average profit and win rate by pattern.
- Helps identify which patterns are most effective.

### 4. Backtest Results Comparison
```python
compare_backtest_results(in_sample_stats, out_sample_stats, metrics=None, title="Backtest Results Comparison", save_path=None)
```
- Creates bar graphs comparing in-sample and out-of-sample results side by side.
- Allows selecting which metrics to compare with the `metrics` parameter.

### 5. Complete Results Visualization
```python
visualize_all_results(backtester1, backtester2=None, period1_name="In-Sample", period2_name="Out-of-Sample", output_dir="./results")
```
- Runs all visualizations at once and saves the results.
- Includes comparative analysis for comprehensive results.

## Current System Implementation

### Stop Loss Mechanism
The current system implements a fixed-percentage stop loss strategy:

```python
def calculate_stop_loss(self, candle, position_type):
    """Calculate stop loss level based on candle properties."""
    if position_type == 'buy':
        return float(candle['low']) * 0.995  # 0.5% below low
    else:
        return float(candle['high']) * 1.005  # 0.5% above high
```

**Key points about the current approach:**
- For long positions: Stop loss is set at 0.5% below the candle's low price
- For short positions: Stop loss is set at 0.5% above the candle's high price
- Once price hits this level, the position is automatically liquidated to limit losses
- This provides a simple yet effective risk management method by establishing a maximum potential loss for each trade
- The fixed percentage approach is applied regardless of market volatility

### Insights from Results Analysis

One key insight from analyzing the backtest results is that trading strategies may perform differently across various market conditions. The notable performance difference between in-sample and out-of-sample periods suggests that market regimes significantly impact strategy effectiveness.

Multiple Strategy Ensemble Approach
To consistently generate higher alpha across changing market conditions, we could implement a multiple strategy ensemble approach:

Market Pattern Recognition: Develop a system to identify different chart patterns and market regimes (trending, ranging, volatile)
Possible implementation using Convolutional Neural Networks (CNN) to classify chart patterns automatically
NLP may analyze the news data 
Reinforcement Learning may be in use to keep fitting the model in desirable way
Strategy Mapping: Create a 1:1 mapping between identified market conditions and optimal strategies
Each market pattern would trigger the most suitable trading algorithm from a library of strategies
Dynamic Switching: Automatically shift between strategies as market conditions evolve
This creates adaptability without requiring constant manual intervention
Performance Tracking: Continuously monitor the effectiveness of each strategy in real-time
Periodically update the mapping based on recent performance data

## Future Improvements

### 1. Dynamic Stop Loss Enhancement
While the current fixed-percentage stop loss works as a basic risk management tool, it could be enhanced with:

- **Volatility-adjusted stop loss**: Calculate stop loss distances based on recent market volatility (e.g., ATR - Average True Range)
- **Adaptive positioning**: Adjust position size inversely to stop loss distance to maintain consistent risk per trade
- **Trailing stop mechanisms**: Move stop loss levels to lock in profits as the trade moves favorably
- **Time-based stop loss**: Exit trades that haven't performed as expected within a certain timeframe

Example implementation concept for volatility-adjusted stops:
```python
def calculate_dynamic_stop_loss(self, candle, position_type, atr_periods=14, atr_multiplier=2.0):
    # Calculate ATR
    atr_value = self.calculate_atr(atr_periods)
    
    if position_type == 'buy':
        return float(candle['close']) - (atr_value * atr_multiplier)
    else:
        return float(candle['close']) + (atr_value * atr_multiplier)
```

### 2. Daily Candle-Based Market Direction Analysis
A promising enhancement would be integrating daily timeframe analysis to determine market bias. By analyzing daily candles in real-time, the system could identify whether the market is bullish or bearish, which could significantly improve trading direction selection (long vs. short positions).

This approach would:
- Align short-term trading strategies with the broader market trend
- Filter out potential false signals that go against the dominant trend
- Optimize entry points by considering higher timeframe support/resistance levels
- Potentially reduce drawdowns by avoiding countertrend trades

### 3. Additional Enhancement Ideas

#### Advanced Market Analysis
- Multi-timeframe analysis to strengthen signal validation
- Volume profile analysis to identify key price levels
- Market regime detection (trending vs. ranging)
- Volatility filtering to adapt to changing market conditions

#### Performance Optimization
- Dynamic position sizing based on volatility and conviction
- Adaptive parameter optimization based on market conditions
- Machine learning models for pattern recognition and prediction
- Integration with market sentiment analysis from external sources

## Important Notes

- All visualization functions use `matplotlib`. This library must be installed.
- You need write permissions in the directory to save visualization results.
- Be mindful of memory usage when visualizing large amounts of data.


venvwoosangwon@Woos-MacBook-Air Binance_perp % python backtest.py

Running In-Sample Backtest:
==========================
Starting backtest on BTCUSDT_5m_20250101_20250201_UTC_in_sample.csv...
Loading data from BTCUSDT_5m_20250101_20250201_UTC_in_sample.csv
Processing 8928 candles...
Processed 0 candles...
Processed 1000 candles...
Processed 2000 candles...
Processed 3000 candles...
Processed 4000 candles...
Processed 5000 candles...
Processed 6000 candles...
Processed 7000 candles...
Processed 8000 candles...

Backtest completed.

Running Out-of-Sample Backtest:
==============================
Starting backtest on BTCUSDT_5m_20250201_20250223_UTC_out_of_sample.csv...
Loading data from BTCUSDT_5m_20250201_20250223_UTC_out_of_sample.csv
Processing 6336 candles...
Processed 0 candles...
Processed 1000 candles...
Processed 2000 candles...
Processed 3000 candles...
Processed 4000 candles...
Processed 5000 candles...
Processed 6000 candles...

Backtest completed.

Backtest Results Comparison:
===========================

Performance Metrics:
Total Return         | In-Sample: 2.08 | Out-of-Sample: 17.57
Annualized Return    | In-Sample: 45.40 | Out-of-Sample: 1706.62
Annualized Volatility | In-Sample: 85.67 | Out-of-Sample: 61.86
Sharpe Ratio         | In-Sample: 0.41 | Out-of-Sample: 4.67
Max Drawdown         | In-Sample: 22.10 | Out-of-Sample: 8.21

Trading Statistics:
Total Trades         | In-Sample: 122 | Out-of-Sample: 63
Win Rate             | In-Sample: 17.21 | Out-of-Sample: 25.40
Average Profit       | In-Sample: 2.92 | Out-of-Sample: 29.33
Profit Factor        | In-Sample: 1.05 | Out-of-Sample: 1.57
Win Loss Ratio       | In-Sample: 5.06 | Out-of-Sample: 4.62
Average Holding Time | In-Sample: 13.88 | Out-of-Sample: 21.15

Cost Analysis:
Total Fees           | In-Sample: 291.75 | Out-of-Sample: 162.31
Total Entry Fees     | In-Sample: 146.40 | Out-of-Sample: 75.60
Total Exit Fees      | In-Sample: 146.63 | Out-of-Sample: 75.32
Total Funding Fees   | In-Sample: -1.28 | Out-of-Sample: 11.39
Fees To Profit Ratio | In-Sample: 81.78 | Out-of-Sample: 8.78

Detailed comparison saved to 'backtest_comparison.csv'
