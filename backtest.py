import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from indicators import SupportResistanceTracker, add_indicators
from strategy import TradingStrategy
from config import (
    SYMBOL, TIMEFRAME,
    IN_SAMPLE_START, IN_SAMPLE_END,
    OUT_OF_SAMPLE_START, OUT_OF_SAMPLE_END,
    LEVERAGE, MAX_POSITIONS, MAX_CAPITAL_USAGE, RISK_PER_TRADE
)

class Backtester:
    def __init__(self, initial_balance=10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = []
        self.trades_history = []
        self.sr_tracker = SupportResistanceTracker()
        self.strategy = TradingStrategy(self.sr_tracker)
        
        # 거래소 관련 설정
        self.maker_fee = 0.0002  # Maker 수수료 0.02%
        self.taker_fee = 0.0004  # Taker 수수료 0.04%
        self.avg_slippage = 0.0005  # 평균 슬리피지 0.05%
        self.min_order_amount = 5  # 최소 주문 금액 (USDT)
        
        # 펀딩비 관련 설정
        self.funding_interval = timedelta(hours=8)  # 8시간마다 펀딩
        self.funding_rate = 0.01/100/3  # 일일 0.01% 기준, 8시간당
        self.last_funding_time = None
        
        # 결과 저장용
        self.equity_curve = []
        self.funding_history = []
    
    def load_data(self, csv_filename):
        """CSV 파일에서 데이터 로드"""
        print(f"Loading data from {csv_filename}")
        df = pd.read_csv(csv_filename)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def reset(self):
        """백테스터 상태 초기화"""
        self.balance = self.initial_balance
        self.positions = []
        self.trades_history = []
        self.sr_tracker = SupportResistanceTracker()
        self.strategy = TradingStrategy(self.sr_tracker)
        self.last_funding_time = None
        self.equity_curve = []
        self.funding_history = []
    
    def apply_slippage(self, price, order_type):
        """슬리피지 적용"""
        slippage = np.random.uniform(0, self.avg_slippage * 2)
        if order_type == 'buy':
            return price * (1 + slippage)
        else:
            return price * (1 - slippage)
    
    def calculate_fee(self, amount, is_maker=False):
        """거래 수수료 계산"""
        return amount * (self.maker_fee if is_maker else self.taker_fee)
    
    def apply_funding_fee(self, candle):
        """펀딩비 적용"""
        current_time = pd.to_datetime(candle['timestamp'])
        
        if self.last_funding_time is None:
            hours_since_midnight = current_time.hour
            last_funding_hour = (hours_since_midnight // 8) * 8
            self.last_funding_time = current_time.replace(
                hour=last_funding_hour,
                minute=0,
                second=0,
                microsecond=0
            )
            return
        
        while current_time >= self.last_funding_time + self.funding_interval:
            funding_time = self.last_funding_time + self.funding_interval
            
            for position in self.positions:
                position_value = position['size'] * float(candle['close'])
                funding_rate = self.funding_rate
                if position['type'] == 'sell':  # 숏 포지션
                    funding_rate = -funding_rate
                
                funding_fee = position_value * funding_rate
                self.balance -= funding_fee
                
                # 펀딩비 기록
                if 'funding_fees' not in position:
                    position['funding_fees'] = []
                position['funding_fees'].append({
                    'time': funding_time,
                    'fee': funding_fee
                })
                
                # 전체 펀딩비 히스토리에 추가
                self.funding_history.append({
                    'time': funding_time,
                    'position_id': id(position),
                    'position_type': position['type'],
                    'position_size': position['size'],
                    'funding_rate': funding_rate,
                    'funding_fee': funding_fee
                })
            
            self.last_funding_time = funding_time
    
    def check_positions(self, candle):
        """포지션 체크 및 청산"""
        closed_positions = []
        current_price = float(candle['close'])
        
        for position in self.positions:
            result = None
            
            if position['type'] == 'buy':
                actual_price = self.apply_slippage(current_price, 'sell')
                
                if actual_price >= position['take_profit']:
                    exit_price = position['take_profit']
                    status = 'take_profit'
                elif actual_price <= position['stop_loss']:
                    exit_price = position['stop_loss']
                    status = 'stop_loss'
                else:
                    continue
                
                exit_fee = self.calculate_fee(exit_price * position['size'])
                profit = (
                    (exit_price - position['entry_price']) * position['size'] * LEVERAGE
                    - position['entry_fee']
                    - exit_fee
                )
                
                result = {
                    'status': status,
                    'profit': profit,
                    'exit_price': exit_price,
                    'exit_fee': exit_fee
                }
                
            else:  # sell position
                actual_price = self.apply_slippage(current_price, 'buy')
                
                if actual_price <= position['take_profit']:
                    exit_price = position['take_profit']
                    status = 'take_profit'
                elif actual_price >= position['stop_loss']:
                    exit_price = position['stop_loss']
                    status = 'stop_loss'
                else:
                    continue
                
                exit_fee = self.calculate_fee(exit_price * position['size'])
                profit = (
                    (position['entry_price'] - exit_price) * position['size'] * LEVERAGE
                    - position['entry_fee']
                    - exit_fee
                )
                
                result = {
                    'status': status,
                    'profit': profit,
                    'exit_price': exit_price,
                    'exit_fee': exit_fee
                }
            
            if result:
                # 펀딩비 총합 계산 및 반영
                total_funding_fees = sum(f['fee'] for f in position.get('funding_fees', []))
                result['profit'] -= total_funding_fees
                
                trade = {
                    **position,
                    **result,
                    'exit_time': candle['timestamp'],
                    'holding_time': (pd.to_datetime(candle['timestamp']) - 
                                   pd.to_datetime(position['entry_time'])).total_seconds() / 3600,
                    'total_funding_fees': total_funding_fees,
                    'total_fees': position['entry_fee'] + exit_fee + total_funding_fees
                }
                
                self.trades_history.append(trade)
                closed_positions.append(position)
                self.balance += result['profit']
        
        for position in closed_positions:
            self.positions.remove(position)
    
    def process_signals(self, candle, signals):
        """시그널 처리 및 거래 실행"""
        for signal in signals:
            if len(self.positions) >= MAX_POSITIONS:
                continue
            
            entry_price = self.apply_slippage(float(candle['close']), signal['type'])
            stop_loss = self.strategy.calculate_stop_loss(candle, signal['type'])
            take_profit = self.strategy.calculate_take_profit(
                entry_price, stop_loss, signal['type']
            )
            
            # 포지션 크기 계산
            max_size = (self.initial_balance * MAX_CAPITAL_USAGE) / entry_price
            risk_based_size = self.strategy.calculate_position_size(
                entry_price, stop_loss, self.balance, self.initial_balance
            )
            position_size = min(max_size, risk_based_size)
            
            # 최소 주문 금액 체크
            if position_size * entry_price < self.min_order_amount:
                continue
            
            # 진입 수수료 계산 및 차감
            entry_fee = self.calculate_fee(entry_price * position_size)
            self.balance -= entry_fee
            
            position = {
                'type': signal['type'],
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'size': position_size,
                'entry_time': candle['timestamp'],
                'pattern': signal['pattern'],
                'entry_fee': entry_fee,
                'funding_fees': []
            }
            
            self.positions.append(position)
    
    def run_backtest(self, csv_filename):
        """백테스트 실행"""
        print(f"Starting backtest on {csv_filename}...")
        
        df = self.load_data(csv_filename)
        df = add_indicators(df)
        
        print(f"Processing {len(df)} candles...")
        
        for i, row in df.iterrows():
            # 잔고 기록
            self.equity_curve.append({
                'timestamp': row['timestamp'],
                'balance': self.balance
            })
            
            # 펀딩비 적용
            self.apply_funding_fee(row)
            
            # 포지션 체크
            self.check_positions(row)
            
            # 새로운 시그널 분석
            signals = self.strategy.analyze_candle(row, row['trend'])
            
            # 시그널 처리
            self.process_signals(row, signals)
            
            if i % 1000 == 0:
                print(f"Processed {i} candles...")
        
        print("\nBacktest completed.")
        return self.calculate_statistics()
    
    def calculate_statistics(self):
        """백테스팅 결과 통계 계산"""
        if not self.trades_history:
            return self._get_empty_stats()
        
        trades_df = pd.DataFrame(self.trades_history)
        
        # 시간 데이터 변환
        trades_df['entry_time'] = pd.to_datetime(trades_df['entry_time'])
        trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])
        trades_df['date'] = trades_df['exit_time'].dt.date
        
        # 일별 수익률 계산
        daily_returns = trades_df.groupby('date')['profit'].sum() / self.initial_balance
        
        # 샤프 비율 계산
        risk_free_rate = 0.02  # 2% 연간 무위험 수익률
        daily_rf_rate = (1 + risk_free_rate) ** (1/252) - 1
        excess_returns = daily_returns - daily_rf_rate
        sharpe_ratio = np.sqrt(252) * (excess_returns.mean() / excess_returns.std()) if len(excess_returns) > 1 else 0
        
        # 거래 통계
        total_trades = len(trades_df)
        profitable_trades = len(trades_df[trades_df['profit'] > 0])
        
        # 비용 분석
        total_entry_fees = trades_df['entry_fee'].sum()
        total_exit_fees = trades_df['exit_fee'].sum()
        total_funding_fees = trades_df['total_funding_fees'].sum()
        total_fees = total_entry_fees + total_exit_fees + total_funding_fees
        
        stats = {
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'total_return': ((self.balance - self.initial_balance) / self.initial_balance) * 100,
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': (profitable_trades / total_trades) * 100 if total_trades > 0 else 0,
            'average_profit': trades_df['profit'].mean(),
            'max_profit': trades_df['profit'].max(),
            'max_loss': trades_df['profit'].min(),
            'average_holding_time': trades_df['holding_time'].mean(),
            'profit_factor': abs(trades_df[trades_df['profit'] > 0]['profit'].sum() / 
                               trades_df[trades_df['profit'] < 0]['profit'].sum()) 
                               if len(trades_df[trades_df['profit'] < 0]) > 0 else float('inf'),
            'max_drawdown': self._calculate_max_drawdown(trades_df),
            'win_loss_ratio': (trades_df[trades_df['profit'] > 0]['profit'].mean() / 
                              abs(trades_df[trades_df['profit'] < 0]['profit'].mean()))
                              if len(trades_df[trades_df['profit'] < 0]) > 0 else float('inf'),
            'sharpe_ratio': sharpe_ratio,
            'annualized_return': ((1 + daily_returns.mean()) ** 252 - 1) * 100,
            'annualized_volatility': daily_returns.std() * np.sqrt(252) * 100,
            'total_fees': total_fees,
            'total_entry_fees': total_entry_fees,
            'total_exit_fees': total_exit_fees,
            'total_funding_fees': total_funding_fees,
            'fees_to_profit_ratio': (total_fees / trades_df['profit'].sum()) * 100 if trades_df['profit'].sum() != 0 else float('inf')
        }
        
        return stats
    
    def _calculate_max_drawdown(self, trades_df):
        """최대 낙폭 계산"""
        if trades_df.empty:
            return 0
        
        cumulative_returns = (trades_df['profit'] / self.initial_balance).cumsum()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns - rolling_max
        return abs(drawdowns.min()) * 100
    
    def _get_empty_stats(self):
        """거래가 없을 때의 빈 통계"""
        return {
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'total_return': 0,
            'total_trades': 0,
            'profitable_trades': 0,
            'win_rate': 0,
            'average_profit': 0,
            'max_profit': 0,
            'max_loss': 0,
            'average_holding_time': 0,
            'profit_factor': 0,
            'max_drawdown': 0,
            'win_loss_ratio': 0,
            'sharpe_ratio': 0,
            'annualized_return': 0,
            'annualized_volatility': 0,
            'total_fees': 0,
            'total_entry_fees': 0,
            'total_exit_fees': 0,
            'total_funding_fees': 0,
            'fees_to_profit_ratio': 0
        }

def print_comparison(metric, in_sample_value, out_sample_value, format_str='.2f'):
    """인샘플과 아웃샘플 결과 비교 출력"""
    print(f"{metric.replace('_', ' ').title():20} | "
          f"In-Sample: {in_sample_value:{format_str}} | "
          f"Out-of-Sample: {out_sample_value:{format_str}}")

def main():
    # 백테스터 초기화
    backtester = Backtester(initial_balance=10000)
    
    # 인샘플 백테스트 실행
    print("\nRunning In-Sample Backtest:")
    print("==========================")
    in_sample_file = f"{SYMBOL}_{TIMEFRAME}_{IN_SAMPLE_START.strftime('%Y%m%d')}_{IN_SAMPLE_END.strftime('%Y%m%d')}_UTC_in_sample.csv"
    in_sample_stats = backtester.run_backtest(in_sample_file)
    
    # 인샘플 결과 저장
    in_sample_backtester = backtester
    
    # 아웃샘플 테스트를 위한 초기화
    backtester = Backtester(initial_balance=10000)
    
    # 아웃샘플 백테스트 실행
    print("\nRunning Out-of-Sample Backtest:")
    print("==============================")
    out_sample_file = f"{SYMBOL}_{TIMEFRAME}_{OUT_OF_SAMPLE_START.strftime('%Y%m%d')}_{OUT_OF_SAMPLE_END.strftime('%Y%m%d')}_UTC_out_of_sample.csv"
    out_sample_stats = backtester.run_backtest(out_sample_file)
    
    # 아웃샘플 결과 저장
    out_sample_backtester = backtester
    
    # 결과 비교 출력
    print("\nBacktest Results Comparison:")
    print("===========================")
    
    # 성과 지표
    print("\nPerformance Metrics:")
    print_comparison('total_return', in_sample_stats['total_return'], out_sample_stats['total_return'])
    print_comparison('annualized_return', in_sample_stats['annualized_return'], out_sample_stats['annualized_return'])
    print_comparison('annualized_volatility', in_sample_stats['annualized_volatility'], out_sample_stats['annualized_volatility'])
    print_comparison('sharpe_ratio', in_sample_stats['sharpe_ratio'], out_sample_stats['sharpe_ratio'])
    print_comparison('max_drawdown', in_sample_stats['max_drawdown'], out_sample_stats['max_drawdown'])
    
    # 거래 통계
    print("\nTrading Statistics:")
    print_comparison('total_trades', in_sample_stats['total_trades'], out_sample_stats['total_trades'], 'd')
    print_comparison('win_rate', in_sample_stats['win_rate'], out_sample_stats['win_rate'])
    print_comparison('average_profit', in_sample_stats['average_profit'], out_sample_stats['average_profit'])
    print_comparison('profit_factor', in_sample_stats['profit_factor'], out_sample_stats['profit_factor'])
    print_comparison('win_loss_ratio', in_sample_stats['win_loss_ratio'], out_sample_stats['win_loss_ratio'])
    print_comparison('average_holding_time', in_sample_stats['average_holding_time'], out_sample_stats['average_holding_time'])
    
    # 비용 분석
    print("\nCost Analysis:")
    print_comparison('total_fees', in_sample_stats['total_fees'], out_sample_stats['total_fees'])
    print_comparison('total_entry_fees', in_sample_stats['total_entry_fees'], out_sample_stats['total_entry_fees'])
    print_comparison('total_exit_fees', in_sample_stats['total_exit_fees'], out_sample_stats['total_exit_fees'])
    print_comparison('total_funding_fees', in_sample_stats['total_funding_fees'], out_sample_stats['total_funding_fees'])
    print_comparison('fees_to_profit_ratio', in_sample_stats['fees_to_profit_ratio'], out_sample_stats['fees_to_profit_ratio'])
    
    # 상세 결과 저장
    results = pd.DataFrame([{
        'metric': metric,
        'in_sample': in_sample_stats[metric],
        'out_of_sample': out_sample_stats[metric]
    } for metric in in_sample_stats.keys()])
    
    results.to_csv('backtest_comparison.csv', index=False)
    print("\nDetailed comparison saved to 'backtest_comparison.csv'")
    
    # 시각화 모듈 사용
    try:
        from visualizer import visualize_all_results
        visualize_all_results(in_sample_backtester, out_sample_backtester)
        print("\nVisualization completed. Check the 'results' directory for images.")
    except ImportError:
        print("\nVisualization module not found. Save the visualizer.py file and try again.")
        
if __name__ == "__main__":
    main()