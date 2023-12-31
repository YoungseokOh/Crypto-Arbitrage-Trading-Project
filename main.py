from tqdm import tqdm
from util import ChartUtils
from calculate import TechnicalIndicators
from data import MarketData
from core import TradingCore
from dotenv import load_dotenv
from exchange import Exchange
import ccxt
import matplotlib.pyplot as plt
import os
import shutil
import pandas as pd

timeframe_options = ['1h', '2h', '4h', '6h', '8h', '12h']

def analyze_all_timeframes(exchange):
    # 전체 시간봉을 탐색하는 로직
    print("Analyzing all timeframes...")
    symbols = exchange.get_symbols()
    extreme_signals_per_timeframe = {
    timeframe: {'bb': set(), 'rsi': set()} for timeframe in timeframe_options
    }
    for timeframe in tqdm(timeframe_options):
    # 이 시점에서 'timeframe' 변수는 유효한 값을 가짐
        print(f"\nAnalyzing timeframe: {timeframe}")
        limit = ChartUtils.calculate_limit(timeframe)  # 입력된 시간봉에 따른 limit 계산
        coins_data = MarketData.fetch_coins_data(exchange.exchange, symbols, timeframe, limit)
        extreme_bb_signals = TradingCore.find_bollinger_extremes(coins_data)
        extreme_rsi_signals = TradingCore.find_extreme_rsi(coins_data)

        # 각 시간대별 신호 저장
        for symbol, _ in extreme_bb_signals:
            extreme_signals_per_timeframe[timeframe]['bb'].add(symbol)
        for symbol, _, _ in extreme_rsi_signals:
            extreme_signals_per_timeframe[timeframe]['rsi'].add(symbol)
    # 공통 신호 찾기
    common_bb_symbols = set.intersection(*[signals['bb'] for signals in extreme_signals_per_timeframe.values()])
    common_rsi_symbols = set.intersection(*[signals['rsi'] for signals in extreme_signals_per_timeframe.values()])

    # 공통 볼린저 밴드 신호 코인에 대한 차트 저장
    if common_bb_symbols:
        for symbol in common_bb_symbols:
            data = coins_data[symbol]
            data = TechnicalIndicators.add_technical_indicators(data)
            data['upper_band'], data['lower_band'] = TechnicalIndicators.calculate_bollinger_bands(data)
            ChartUtils.save_chart(data, symbol, "common")
    else:
        print("No common Bollinger Band signals found across timeframes.")

def analyze_specific_timeframe(exchange):
    print("Available timeframes: " + ', '.join(timeframe_options))
    while True:
        user_input = input("Enter the timeframe (e.g., '1' for '1h', '6' for '6h'): ")
        if user_input.isdigit() and f"{user_input}h" in timeframe_options:
            timeframe = f"{user_input}h"
            print(f"You have selected the timeframe: {timeframe}")
            # 여기에 특정 시간봉을 탐색하는 코드 추가
            symbols = exchange.get_symbols()
            limit = ChartUtils.calculate_limit(timeframe)  # 입력된 시간봉에 따른 limit 계산
            coins_data = MarketData.fetch_coins_data(exchange.exchange, symbols, timeframe, limit)
            extreme_bb_signals = TradingCore.find_bollinger_extremes(coins_data)
            extreme_rsi_signals = TradingCore.find_extreme_rsi(coins_data)

            if extreme_bb_signals:
                print("\nCoins with extreme Bollinger Band values:")
                for symbol, position in extreme_bb_signals:
                    print(f"{symbol} is {position}")
                    # 데이터 프레임을 가져오고, 볼린저 밴드를 계산합니다.
                    data = coins_data[symbol]
                    # 기술적 지표 (SMA와 RSI)를 계산하고 데이터프레임에 추가합니다.
                    data = TechnicalIndicators.add_technical_indicators(data)
                    # 볼린저 밴드를 계산합니다.
                    data['upper_band'], data['lower_band'] = TechnicalIndicators.calculate_bollinger_bands(data)
                    # 차트를 저장합니다.
                    ChartUtils.save_chart(data, symbol, timeframe)
                    
            if extreme_rsi_signals:
                print("\nCoins with extreme RSI values:")
                for symbol, status, rsi_value in extreme_rsi_signals:
                    print(f"{symbol} is {status} (RSI: {rsi_value:.2f})")

            else:
                print("\nNo coins with extreme Bollinger Band values at this time.")
            break
        else:
            print("Invalid input. Please enter a valid number for the timeframe.")


def main():
    ChartUtils.initialize_chart_folder()
    exchange = Exchange()
    # 선물 계좌 잔고 조회
    exchange.print_balance()

    print("Select the analysis mode:")
    print("1: Analyze all timeframes")
    print("2: Analyze a specific timeframe")
    
    while True:
        mode = input("Enter your choice (1 or 2): ")
        if mode == '1':
            analyze_all_timeframes(exchange)
            break
        elif mode == '2':
            analyze_specific_timeframe(exchange)
            break
        else:
            print("Invalid input. Please enter 1 or 2.")
    

if __name__ == "__main__":
    main()