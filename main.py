from tqdm import tqdm
from util import ChartUtils
from calculate import TechnicalIndicators
from data import MarketData
from core import TradingCore
from dotenv import load_dotenv

import ccxt
import matplotlib.pyplot as plt
import os
import shutil
import pandas as pd


def main():
    # 사용자가 원하는 시간봉 입력
    timeframe_options = ['1h', '2h', '3h', '4h', '6h', '8h', '12h']
    print("Available timeframes: " + ', '.join(timeframe_options))
    # Binance 마진 계좌에 연결

    while True:
        user_input = input("Enter the timeframe (e.g., '1' for '1h', '6' for '6h'): ")
        # 사용자 입력이 숫자만 포함하고, 옵션에 해당하는지 확인
        if user_input.isdigit() and f"{user_input}h" in timeframe_options:
            timeframe = f"{user_input}h"
            break  # 올바른 입력을 받았으므로 루프를 종료
        else:
            print("Invalid input. Please enter a valid number for the timeframe.")

    load_dotenv(verbose=True)
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
        # Binance 선물(futures) 계좌에 연결
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}  # 선물 계좌로 설정
    })

    # 선물 계좌 잔고 조회
    balance = exchange.fetch_balance()
    print("Futures Account Balances:")
    for asset, amount in balance['total'].items():
        if amount > 0:
            print(f"{asset}: {amount}")

    # 현재 포지션 정보 조회
    print("\nCurrent Positions:")
    positions = balance['info']['positions']
    for position in positions:
        if float(position['positionAmt']) != 0:  # 열려 있는 포지션만 출력
            print(f"Symbol: {position['symbol']}")
            print(f"  Position Amount: {position['positionAmt']}")
            print(f"  Entry Price: {position['entryPrice']}")
            print(f"  Unrealized Profit: {position['unrealizedProfit']}")
            print(f"  leverage: {position['leverage']}")
            print("")

    # 이 시점에서 'timeframe' 변수는 유효한 값을 가짐
    print(f"You have selected the timeframe: {timeframe}")
    limit = ChartUtils.calculate_limit(timeframe)  # 입력된 시간봉에 따른 limit 계산
    ChartUtils.initialize_chart_folder()
    exchange.load_markets()
    symbols = exchange.symbols
    coins_data = MarketData.fetch_coins_data(exchange, symbols, timeframe, limit)
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

if __name__ == "__main__":
    main()