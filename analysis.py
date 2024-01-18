# analysis.py

from tqdm import tqdm
from util import ChartUtils
from calculate import TechnicalIndicators
from data import MarketData
from core import TradingCore
import os
import pandas as pd


class Analysis:
    def __init__(self, exchange):
        self.exchange = exchange
        self.timeframe_options = ['1h', '2h', '4h', '6h', '8h', '12h']

    def fetch_top_gainers_and_losers(self):
    # Binance 선물 시장의 모든 코인에 대한 티커 정보를 가져옵니다.
        tickers = self.exchange.exchange.fetch_tickers()
        futures_tickers = {symbol: ticker for symbol, ticker in tickers.items() if symbol.endswith('USDT')}

        # 가격 변동률을 기준으로 정렬하여 상위 5개와 하위 5개 코인을 추출합니다.
        sorted_tickers = sorted(futures_tickers.items(), key=lambda x: x[1]['percentage'], reverse=True)
        top_5_gainers = sorted_tickers[:5]
        top_5_losers = sorted_tickers[-5:]

        # 결과를 딕셔너리로 반환합니다.
        return {
                'gainers': [{'symbol': symbol.replace(':USDT', ''), 'change': ticker['percentage']} for symbol, ticker in top_5_gainers],
                'losers': [{'symbol': symbol.replace(':USDT', ''), 'change': ticker['percentage']} for symbol, ticker in top_5_losers]
                }   

    def analyze_top_coins(self):
        top_gainers = self.fetch_top_gainers_and_losers()
        return top_gainers

    def analyze_all_timeframes(self):
        # 전체 시간봉을 탐색하는 로직
        print("Analyzing all timeframes...")
        result = {
            'common_bb_symbols': [], 
            'common_rsi_symbols': [], 
            'intersected_symbols': []  # 공통된 코인을 저장할 리스트
        }
        symbols = self.exchange.get_symbols()
        extreme_signals_per_timeframe = {
        timeframe: {'bb': set(), 'rsi': set()} for timeframe in self.timeframe_options
        }
        for timeframe in tqdm(self.timeframe_options):
        # 이 시점에서 'timeframe' 변수는 유효한 값을 가짐
            limit = ChartUtils.calculate_limit(timeframe)  # 입력된 시간봉에 따른 limit 계산
            coins_data = MarketData.fetch_coins_data(self.exchange.exchange, symbols, timeframe, limit)
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
        # 공통된 요소 찾기
        intersected_symbols = common_bb_symbols.intersection(common_rsi_symbols)

        # 공통 볼린저 밴드 신호 코인에 대한 차트 저장
        if common_bb_symbols:
            processed_bb_symbols = ChartUtils.remove_suffix_from_symbols(common_bb_symbols)
            processed_rsi_symbols = ChartUtils.remove_suffix_from_symbols(common_rsi_symbols)
            processed_intersected_symbols = ChartUtils.remove_suffix_from_symbols(intersected_symbols)

            for symbol in common_bb_symbols:
                data = coins_data[symbol]
                data = TechnicalIndicators.add_technical_indicators(data)
                data['upper_band'], data['lower_band'] = TechnicalIndicators.calculate_bollinger_bands(data)
                ChartUtils.save_chart(data, symbol, "common")
                result.update({
                'common_bb_symbols': list(processed_bb_symbols),
                'common_rsi_symbols': list(processed_rsi_symbols),
                'intersected_symbols': list(processed_intersected_symbols)  # 공통된 코인 리스트 추가
            })
                return result
        else:
            print("No common Bollinger Band signals found across timeframes.")

    def analyze_specific_timeframe(self):
        print("Available timeframes: " + ', '.join(self.timeframe_options))
        while True:
            user_input = input("Enter the timeframe (e.g., '1' for '1h', '6' for '6h'): ")
            if user_input.isdigit() and f"{user_input}h" in self.timeframe_options:
                timeframe = f"{user_input}h"
                print(f"You have selected the timeframe: {timeframe}")
                # 여기에 특정 시간봉을 탐색하는 코드 추가
                symbols = self.exchange.get_symbols()
                limit = ChartUtils.calculate_limit(timeframe)  # 입력된 시간봉에 따른 limit 계산
                coins_data = MarketData.fetch_coins_data(self.exchange.exchange, symbols, timeframe, limit)
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
                