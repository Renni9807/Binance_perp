import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.dates as mdates

def visualize_equity_curve(backtester, title="Equity Curve", save_path=None):
    """자산 곡선 시각화"""
    if not backtester.equity_curve:
        print("시각화할 데이터가 부족합니다.")
        return
    
    # 데이터 준비
    equity_df = pd.DataFrame(backtester.equity_curve)
    equity_df['timestamp'] = pd.to_datetime(equity_df['timestamp'])
    equity_df.set_index('timestamp', inplace=True)
    
    # 그래프 생성
    plt.figure(figsize=(12, 6))
    plt.plot(equity_df.index, equity_df['balance'], label='Balance', color='blue', linewidth=2)
    plt.axhline(y=backtester.initial_balance, color='gray', linestyle='--', alpha=0.7, label='Initial Balance')
    
    plt.title(title, fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.ylabel('Balance (USDT)', fontsize=12)
    plt.legend(loc='upper left')
    
    # x축 포맷 설정
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()
    
    if save_path:
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"자산 곡선이 저장되었습니다: {save_path}")
    else:
        plt.tight_layout()
        plt.show()

def visualize_trade_results(backtester, title="Trade Results", save_path=None):
    """거래 결과 시각화"""
    if not backtester.trades_history:
        print("시각화할 거래 기록이 없습니다.")
        return
    
    # 데이터 준비
    trades_df = pd.DataFrame(backtester.trades_history)
    trades_df['entry_time'] = pd.to_datetime(trades_df['entry_time'])
    trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])
    
    # 그래프 설정
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [1, 1]})
    
    # 누적 수익 그래프
    trades_df['cumulative_profit'] = trades_df['profit'].cumsum()
    axes[0].plot(trades_df['exit_time'], trades_df['cumulative_profit'], 
               color='green', linewidth=2)
    axes[0].axhline(y=0, color='gray', linestyle='-', alpha=0.5)
    axes[0].set_title("Cumulative Profit", fontsize=14)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylabel('Profit (USDT)', fontsize=12)
    
    # 개별 거래 수익 막대 그래프
    colors = ['green' if p > 0 else 'red' for p in trades_df['profit']]
    axes[1].bar(trades_df['exit_time'], trades_df['profit'], color=colors, width=0.7, alpha=0.7)
    axes[1].set_title("Individual Trade Profit/Loss", fontsize=14)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylabel('Profit/Loss (USDT)', fontsize=12)
    
    # x축 포맷 설정
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"거래 결과가 저장되었습니다: {save_path}")
    else:
        plt.show()

def visualize_trade_patterns(backtester, title="Trade Patterns Analysis", save_path=None):
    """거래 패턴별 성과 시각화"""
    if not backtester.trades_history:
        print("시각화할 거래 기록이 없습니다.")
        return
    
    # 데이터 준비
    trades_df = pd.DataFrame(backtester.trades_history)
    
    # 패턴별 성과 분석
    pattern_stats = trades_df.groupby('pattern').agg({
        'profit': ['sum', 'mean', 'count'],
        'type': lambda x: x.value_counts().index[0]  # 가장 많이 사용된 포지션 타입
    })
    
    # 컬럼명 변경
    pattern_stats.columns = ['total_profit', 'avg_profit', 'trades_count', 'main_position_type']
    pattern_stats = pattern_stats.reset_index()
    
    # 승률 계산
    for idx, pattern in enumerate(pattern_stats['pattern']):
        win_count = len(trades_df[(trades_df['pattern'] == pattern) & (trades_df['profit'] > 0)])
        total_count = len(trades_df[trades_df['pattern'] == pattern])
        pattern_stats.loc[idx, 'win_rate'] = (win_count / total_count) * 100 if total_count > 0 else 0
    
    # 그래프 생성
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    # 평균 수익 그래프
    pattern_stats = pattern_stats.sort_values('avg_profit', ascending=False)
    colors = ['green' if x >= 0 else 'red' for x in pattern_stats['avg_profit']]
    bars1 = ax1.bar(pattern_stats['pattern'], pattern_stats['avg_profit'], color=colors)
    ax1.set_title('Average Profit by Pattern', fontsize=12)
    ax1.set_ylabel('Average Profit (USDT)')
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_xticklabels(pattern_stats['pattern'], rotation=45, ha='right')
    
    # 값 표시
    for bar in bars1:
        height = bar.get_height()
        value_text = f"{height:.2f}" if abs(height) < 100 else f"{height:.1f}"
        ax1.text(bar.get_x() + bar.get_width()/2., height + (0.2 if height >= 0 else -8),
                f'{value_text}', ha='center', va='bottom', fontsize=9)
    
    # 승률 그래프
    pattern_stats = pattern_stats.sort_values('win_rate', ascending=False)
    bars2 = ax2.bar(pattern_stats['pattern'], pattern_stats['win_rate'], color='skyblue')
    ax2.set_title('Win Rate by Pattern', fontsize=12)
    ax2.set_ylabel('Win Rate (%)')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_xticklabels(pattern_stats['pattern'], rotation=45, ha='right')
    
    # 값 표시
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"패턴 분석이 저장되었습니다: {save_path}")
    else:
        plt.show()

def compare_backtest_results(in_sample_stats, out_sample_stats, metrics=None, title="Backtest Results Comparison", save_path=None):
    """인샘플과 아웃샘플 결과 비교 시각화"""
    if metrics is None:
        metrics = [
            'total_return', 'win_rate', 'profit_factor', 'max_drawdown', 
            'sharpe_ratio', 'average_profit'
        ]
    
    # 지표 표시 이름 설정
    metric_display_names = {
        'total_return': 'Total Return (%)',
        'win_rate': 'Win Rate (%)',
        'profit_factor': 'Profit Factor',
        'max_drawdown': 'Max Drawdown (%)',
        'sharpe_ratio': 'Sharpe Ratio',
        'average_profit': 'Avg Profit (USD)',
        'fees_to_profit_ratio': 'Fees to Profit Ratio (%)',
        'annualized_return': 'Annualized Return (%)',
        'annualized_volatility': 'Annualized Volatility (%)'
    }
    
    # 데이터 준비
    comparison_data = []
    for metric in metrics:
        if metric in in_sample_stats and metric in out_sample_stats:
            display_name = metric_display_names.get(metric, metric.replace('_', ' ').title())
            comparison_data.append({
                'Metric': display_name,
                'In-Sample': in_sample_stats[metric],
                'Out-of-Sample': out_sample_stats[metric]
            })
    
    if not comparison_data:
        print("비교할 데이터가 없습니다.")
        return
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # 그래프 생성
    plt.figure(figsize=(12, 8))
    
    # 막대 위치 설정
    x = np.arange(len(comparison_df))
    width = 0.35
    
    # 그래프 그리기
    rects1 = plt.bar(x - width/2, comparison_df['In-Sample'], width, label='In-Sample', color='royalblue', alpha=0.8)
    rects2 = plt.bar(x + width/2, comparison_df['Out-of-Sample'], width, label='Out-of-Sample', color='darkorange', alpha=0.8)
    
    # 그래프 스타일 설정
    plt.title(title, fontsize=16)
    plt.xticks(x, comparison_df['Metric'], rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 값 표시
    def add_labels(rects):
        for rect in rects:
            height = rect.get_height()
            
            # 값 포맷 조정
            if abs(height) < 0.01:
                label = f"{height:.4f}"
            elif abs(height) < 100:
                label = f"{height:.2f}"
            else:
                label = f"{height:.1f}"
                
            # 값 표시 위치 조정
            if height < 0:
                plt.annotate(label,
                           xy=(rect.get_x() + rect.get_width() / 2, 0),
                           xytext=(0, -20),
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=9)
            else:
                plt.annotate(label,
                           xy=(rect.get_x() + rect.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=9)
    
    add_labels(rects1)
    add_labels(rects2)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"비교 차트가 저장되었습니다: {save_path}")
    else:
        plt.show()

def visualize_all_results(backtester1, backtester2=None, period1_name="In-Sample", period2_name="Out-of-Sample", output_dir="./results"):
    """모든 결과 시각화 (단일 백테스트 또는 비교)"""
    import os
    
    # 결과 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 첫 번째 백테스트 시각화
    visualize_equity_curve(
        backtester1, 
        title=f"{period1_name} Equity Curve",
        save_path=f"{output_dir}/{period1_name.lower().replace('-', '_')}_equity_curve.png"
    )
    
    visualize_trade_results(
        backtester1,
        title=f"{period1_name} Trade Results", 
        save_path=f"{output_dir}/{period1_name.lower().replace('-', '_')}_trade_results.png"
    )
    
    visualize_trade_patterns(
        backtester1, 
        title=f"{period1_name} Pattern Analysis",
        save_path=f"{output_dir}/{period1_name.lower().replace('-', '_')}_patterns.png"
    )
    
    # 두 번째 백테스트가 있으면 시각화 및 비교
    if backtester2:
        visualize_equity_curve(
            backtester2, 
            title=f"{period2_name} Equity Curve",
            save_path=f"{output_dir}/{period2_name.lower().replace('-', '_')}_equity_curve.png"
        )
        
        visualize_trade_results(
            backtester2,
            title=f"{period2_name} Trade Results", 
            save_path=f"{output_dir}/{period2_name.lower().replace('-', '_')}_trade_results.png"
        )
        
        visualize_trade_patterns(
            backtester2, 
            title=f"{period2_name} Pattern Analysis",
            save_path=f"{output_dir}/{period2_name.lower().replace('-', '_')}_patterns.png"
        )
        
        # 결과 비교
        stats1 = calculate_backtest_stats(backtester1)
        stats2 = calculate_backtest_stats(backtester2)
        
        compare_backtest_results(
            stats1, 
            stats2,
            title=f"{period1_name} vs {period2_name} Comparison",
            save_path=f"{output_dir}/backtest_comparison.png"
        )

def calculate_backtest_stats(backtester):
    """백테스트 결과 통계 계산"""
    # 이미 계산된 통계가 있으면 반환
    if hasattr(backtester, 'last_stats'):
        return backtester.last_stats
    
    # 아니면 calculate_statistics 메서드 호출
    return backtester.calculate_statistics()