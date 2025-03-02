Following Look Ahead bias & Data Snooping bias 

![backtest_comparison](https://github.com/user-attachments/assets/0d0cd9eb-de11-4c1b-9c30-dd6601610e7f)
![in_sample_trade_results](https://github.com/user-attachments/assets/1065efce-5927-47ba-9cb1-5447086cb46e)
![out_of_sample_trade_results](https://github.com/user-attachments/assets/e387a38c-c565-4d74-ac00-6066d09dc5ff)


Enhancement Ideas
Advanced Market Analysis

Multi-timeframe analysis to strengthen signal validation
Volume profile analysis to identify key price levels
Market regime detection (trending vs. ranging)
Volatility filtering to adapt to changing market conditions

Performance Optimization

Dynamic position sizing based on volatility and conviction
Adaptive parameter optimization based on market conditions
Machine learning models for pattern recognition and prediction
Integration with market sentiment analysis from external sources

Risk Management Enhancements

Dynamic stop-loss placement based on recent volatility
Trailing stop mechanisms to protect profits
Time-based exit strategies for trades without clear direction
Portfolio-level risk constraints and correlation analysis

/Users/woosangwon/Desktop/Binance_perp/results/backtest_comparison.png
/Users/woosangwon/Desktop/Binance_perp/results/in_sample_trade_results.png
/Users/woosangwon/Desktop/Binance_perp/results/out_of_sample_trade_results.png
venv) woosangwon@Woos-MacBook-Air Binance_perp % python backtest.py

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
Total Return         | In-Sample: -2.02 | Out-of-Sample: 7.32
Annualized Return    | In-Sample: -4.64 | Out-of-Sample: 300.85
Annualized Volatility | In-Sample: 81.58 | Out-of-Sample: 64.74
Sharpe Ratio         | In-Sample: -0.08 | Out-of-Sample: 2.12
Max Drawdown         | In-Sample: 18.29 | Out-of-Sample: 10.53

Trading Statistics:
Total Trades         | In-Sample: 126 | Out-of-Sample: 67
Win Rate             | In-Sample: 16.67 | Out-of-Sample: 20.90
Average Profit       | In-Sample: -0.37 | Out-of-Sample: 12.37
Profit Factor        | In-Sample: 0.99 | Out-of-Sample: 1.23
Win Loss Ratio       | In-Sample: 4.97 | Out-of-Sample: 4.67
Average Holding Time | In-Sample: 13.09 | Out-of-Sample: 19.59

Cost Analysis:
Total Fees           | In-Sample: 302.68 | Out-of-Sample: 173.73
Total Entry Fees     | In-Sample: 151.20 | Out-of-Sample: 80.40
Total Exit Fees      | In-Sample: 151.56 | Out-of-Sample: 80.14
Total Funding Fees   | In-Sample: -0.08 | Out-of-Sample: 13.19
Fees To Profit Ratio | In-Sample: -642.79 | Out-of-Sample: 20.96

Detailed comparison saved to 'backtest_comparison.csv'
(venv) woosangwon@Woos-MacBook-Air Binance_perp % python backtest.py

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
Total Return         | In-Sample: -2.90 | Out-of-Sample: 11.80
Annualized Return    | In-Sample: -13.77 | Out-of-Sample: 738.33
Annualized Volatility | In-Sample: 80.52 | Out-of-Sample: 67.41
Sharpe Ratio         | In-Sample: -0.21 | Out-of-Sample: 3.14
Max Drawdown         | In-Sample: 20.16 | Out-of-Sample: 10.00

Trading Statistics:
Total Trades         | In-Sample: 122 | Out-of-Sample: 62
Win Rate             | In-Sample: 16.39 | Out-of-Sample: 22.58
Average Profit       | In-Sample: -1.16 | Out-of-Sample: 20.50
Profit Factor        | In-Sample: 0.98 | Out-of-Sample: 1.39
Win Loss Ratio       | In-Sample: 5.00 | Out-of-Sample: 4.77
Average Holding Time | In-Sample: 13.51 | Out-of-Sample: 21.27

Cost Analysis:
Total Fees           | In-Sample: 292.03 | Out-of-Sample: 161.75
Total Entry Fees     | In-Sample: 146.40 | Out-of-Sample: 74.40
Total Exit Fees      | In-Sample: 146.71 | Out-of-Sample: 74.16
Total Funding Fees   | In-Sample: -1.08 | Out-of-Sample: 13.19
Fees To Profit Ratio | In-Sample: -206.97 | Out-of-Sample: 12.73

Detailed comparison saved to 'backtest_comparison.csv'
