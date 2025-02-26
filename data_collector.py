# data_collector.py
import ccxt
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta
import time
from config import (
    SYMBOL, TIMEFRAME,
    IN_SAMPLE_START, IN_SAMPLE_END,
    OUT_OF_SAMPLE_START, OUT_OF_SAMPLE_END
)

def fetch_data_in_batches(exchange, symbol, timeframe, start_date, end_date, batch_size=1000):
    """Fetch historical data in batches."""
    all_candles = []
    current_date = start_date
    
    while current_date < end_date:
        try:
            print(f"Fetching batch from {current_date}")
            
            # Fetch batch of candles
            candles = exchange.fetch_ohlcv(
                symbol,
                timeframe,
                int(current_date.timestamp() * 1000),
                limit=batch_size
            )
            
            if not candles:
                break
                
            all_candles.extend(candles)
            
            # Update current_date to the timestamp of the last candle plus one timeframe
            last_candle_time = pd.to_datetime(candles[-1][0], unit='ms', utc=True)
            current_date = last_candle_time + timedelta(minutes=5)  # Assuming 5m timeframe
            
            # Add small delay to avoid rate limits
            time.sleep(exchange.rateLimit / 1000)  # Convert milliseconds to seconds
            
        except Exception as e:
            print(f"Error fetching batch: {e}")
            time.sleep(exchange.rateLimit / 1000)  # Wait before retrying
            continue
    
    return all_candles

def fetch_and_save_data(start_date, end_date, period_name=""):
    """Fetch historical data from Binance and save to CSV."""
    print(f"Fetching {SYMBOL} data from {start_date} to {end_date} (UTC)")
    
    # Initialize Binance client
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })
    
    # Fetch all data in batches
    all_candles = fetch_data_in_batches(
        exchange, SYMBOL, TIMEFRAME, start_date, end_date
    )
    
    # Convert to DataFrame
    df = pd.DataFrame(
        all_candles,
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )
    
    # Convert timestamp to datetime in UTC
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    
    # Remove duplicates and sort
    df = df.drop_duplicates(subset=['timestamp'])
    df = df.sort_values('timestamp')
    
    # Filter to exact date range
    df = df[
        (df['timestamp'] >= start_date) &
        (df['timestamp'] < end_date)
    ]
    
    # Save to CSV
    filename = f"{SYMBOL}_{TIMEFRAME}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_UTC{period_name}.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    print(f"Total candles: {len(df)}")
    
    return df, filename

def create_chart(df, suffix=""):
    """Create and save candlestick chart as PNG."""
    # Set the timestamp as index
    df_plot = df.copy()
    df_plot.set_index('timestamp', inplace=True)

    # Create figure with custom style
    mc = mpf.make_marketcolors(
        up='red',
        down='blue',
        edge='inherit',
        wick='inherit',
        volume='in'
    )
    
    s = mpf.make_mpf_style(
        marketcolors=mc,
        figcolor='white',
        facecolor='white',
        edgecolor='black',
        gridcolor='gray',
        gridstyle=':',
        rc={'font.size': 10}
    )
    
    # Set figure size and title
    kwargs = dict(
        type='candle',
        volume=True,
        title=f'\n{SYMBOL} {TIMEFRAME} Chart (UTC){suffix}',
        style=s,
        figsize=(15, 10),
        panel_ratios=(3, 1),  # ratio between price and volume panels
        tight_layout=True
    )
    
    # Create and save chart
    period_start = df_plot.index[0].strftime('%Y%m%d')
    period_end = df_plot.index[-1].strftime('%Y%m%d')
    chart_filename = f"{SYMBOL}_{TIMEFRAME}_{period_start}_{period_end}_UTC{suffix}_chart.png"
    mpf.plot(df_plot, **kwargs, savefig=chart_filename)
    
    print(f"Chart saved as {chart_filename}")

def print_data_summary(df):
    """Print summary statistics for the data."""
    print(f"Time Period (UTC): {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Number of candles: {len(df)}")
    print(f"Opening price: {df.iloc[0]['open']:.2f} USDT")
    print(f"Closing price: {df.iloc[-1]['close']:.2f} USDT")
    print(f"Lowest price: {df['low'].min():.2f} USDT")
    print(f"Highest price: {df['high'].max():.2f} USDT")
    print(f"Total volume: {df['volume'].sum():,.2f}")
    
    # Calculate expected number of candles
    time_diff = df['timestamp'].max() - df['timestamp'].min()
    expected_candles = time_diff.total_seconds() / 300  # 300 seconds = 5 minutes
    print(f"\nExpected number of candles: {int(expected_candles)}")
    print(f"Actual number of candles: {len(df)}")
    print(f"Coverage: {(len(df) / expected_candles) * 100:.2f}%")

def main():
    # Fetch in-sample data
    print("\nFetching In-Sample Data:")
    print("=======================")
    df_in_sample, in_sample_file = fetch_and_save_data(
        IN_SAMPLE_START, 
        IN_SAMPLE_END, 
        "_in_sample"
    )
    create_chart(df_in_sample, "_in_sample")
    
    # Fetch out-of-sample data
    print("\nFetching Out-of-Sample Data:")
    print("===========================")
    df_out_sample, out_sample_file = fetch_and_save_data(
        OUT_OF_SAMPLE_START, 
        OUT_OF_SAMPLE_END, 
        "_out_of_sample"
    )
    create_chart(df_out_sample, "_out_of_sample")
    
    # Print data summary for both periods
    print("\nIn-Sample Data Summary:")
    print("=====================")
    print_data_summary(df_in_sample)
    
    print("\nOut-of-Sample Data Summary:")
    print("=========================")
    print_data_summary(df_out_sample)

if __name__ == "__main__":
    main()