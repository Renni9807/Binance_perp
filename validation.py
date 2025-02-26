from datetime import datetime, timedelta
import numpy as np

def split_data_train_test(df, train_ratio=0.7):
    """Split data into training and testing sets."""
    train_size = int(len(df) * train_ratio)
    train_data = df.iloc[:train_size]
    test_data = df.iloc[train_size:]
    return train_data, test_data

def create_walk_forward_periods(df, window_size_days=30, step_size_days=7):
    """Create walk-forward optimization periods."""
    periods = []
    start_date = df.index[0]
    end_date = df.index[-1]
    
    while start_date < end_date:
        period_end = start_date + timedelta(days=window_size_days)
        if period_end > end_date:
            period_end = end_date
            
        periods.append({
            'train_start': start_date,
            'train_end': period_end - timedelta(days=step_size_days),
            'test_start': period_end - timedelta(days=step_size_days),
            'test_end': period_end
        })
        
        start_date += timedelta(days=step_size_days)
        
    return periods

def calculate_forward_returns(df, periods=[1, 5, 10, 20]):
    """Calculate forward returns to avoid look-ahead bias."""
    for period in periods:
        df[f'forward_return_{period}'] = df['close'].pct_change(period).shift(-period)
    return df