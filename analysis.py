# analysis.py

from tqdm import tqdm
from util import ChartUtils
from calculate import TechnicalIndicators
from data import MarketData
from core import TradingCore
import os
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


class Analysis:
    def __init__(self, exchange):
        self.exchange = exchange
        self.timeframe_options = ['1h', '2h', '4h', '6h', '8h', '12h']

    def fetch_top_gainers_and_losers(self):
        tickers = self.exchange.exchange.fetch_tickers()
        futures_tickers = {symbol: ticker for symbol, ticker in tickers.items() if symbol.endswith('USDT')}

        sorted_tickers = sorted(futures_tickers.items(), key=lambda x: x[1]['percentage'], reverse=True)
        top_5_gainers = sorted_tickers[:5]
        top_5_losers = sorted_tickers[-5:]

        # 상위 및 하위 5개 코인의 funding fee 가져오기
        gainers_with_fee = []
        for symbol, ticker in top_5_gainers:
            funding_rate = self.exchange.fetch_funding_rate(symbol)
            gainers_with_fee.append({
                'symbol': symbol.replace(':USDT', ''),
                'change': ticker['percentage'],
                'funding_rate': funding_rate
            })

        losers_with_fee = []
        for symbol, ticker in top_5_losers:
            funding_rate = self.exchange.fetch_funding_rate(symbol)
            losers_with_fee.append({
                'symbol': symbol.replace(':USDT', ''),
                'change': ticker['percentage'],
                'funding_rate': funding_rate
            })

        return {
            'gainers': gainers_with_fee,
            'losers': losers_with_fee
        }

    def analyze_top_coins(self):
        top_gainers = self.fetch_top_gainers_and_losers()
        return top_gainers

    def process_timeframe(self, timeframe, symbols):
        limit = ChartUtils.calculate_limit(timeframe)
        coins_data = MarketData.fetch_coins_data(self.exchange.exchange, symbols, timeframe, limit)
        extreme_bb_signals = TradingCore.find_bollinger_extremes(coins_data)
        extreme_rsi_signals = TradingCore.find_extreme_rsi(coins_data)

        # 각 시간대별 신호 추출
        bb_symbols = {symbol for symbol, _ in extreme_bb_signals}
        rsi_symbols = {symbol for symbol, _, _ in extreme_rsi_signals}
        # 데이터와 신호들 반환
        return (coins_data, bb_symbols, rsi_symbols)

    def analyze_all_timeframes(self):
        # 전체 시간봉을 탐색하는 로직
        print("Analyzing all timeframes...")
        result = {
            'common_bb_symbols': [], 
            'common_rsi_symbols': [], 
            'intersected_symbols': [], # 공통된 코인을 저장할 리스트
            'funding_rates': {}  # 코인별 funding fee 정보를 저장할 딕셔너리
        }
        symbols = self.exchange.get_symbols()
        extreme_signals_per_timeframe = {
        timeframe: {'bb': set(), 'rsi': set()} for timeframe in self.timeframe_options
        }
        all_coins_data = {}
        start_time = time.time()  # 시작 시간 기록
        with ThreadPoolExecutor(max_workers=2) as executor:
            # 각 timeframe에 대한 작업을 병렬로 수행
            futures = {executor.submit(self.process_timeframe, timeframe, symbols): 
                       timeframe for timeframe in self.timeframe_options}
            for future in as_completed(futures):
                result_list = future.result()
                # 리스트에서 데이터 추출
                timeframe_data = result_list[0]
                bb_signals = result_list[1]
                rsi_signals = result_list[2]
                timeframe = futures[future]
                all_coins_data[timeframe] = timeframe_data

                # 각 시간대별 신호 저장
                extreme_signals_per_timeframe[timeframe]['bb'].update(bb_signals)
                extreme_signals_per_timeframe[timeframe]['rsi'].update(rsi_signals)
        end_time = time.time()  # 종료 시간 기록
        total_time = end_time - start_time  # 전체 실행 시간 계산
        print(f"Total execution time: {total_time:.2f} seconds")  # 전체 실행 시간 출력

            # for timeframe in tqdm(self.timeframe_options):
            # # 이 시점에서 'timeframe' 변수는 유효한 값을 가짐
            #     limit = ChartUtils.calculate_limit(timeframe)  # 입력된 시간봉에 따른 limit 계산
            #     coins_data = MarketData.fetch_coins_data(self.exchange.exchange, symbols, timeframe, limit)
            #     extreme_bb_signals = TradingCore.find_bollinger_extremes(coins_data)
            #     extreme_rsi_signals = TradingCore.find_extreme_rsi(coins_data)

            #     # 각 시간대별 신호 저장
            #     for symbol, _ in extreme_bb_signals:
            #         extreme_signals_per_timeframe[timeframe]['bb'].add(symbol)
            #     for symbol, _, _ in extreme_rsi_signals:
            #         extreme_signals_per_timeframe[timeframe]['rsi'].add(symbol)

        common_bb_symbols = set.intersection(*[signals['bb'] for signals in extreme_signals_per_timeframe.values()])
        common_rsi_symbols = set.intersection(*[signals['rsi'] for signals in extreme_signals_per_timeframe.values()])
        intersected_symbols = common_bb_symbols.intersection(common_rsi_symbols)

        if common_bb_symbols:
            processed_bb_symbols = ChartUtils.remove_suffix_from_symbols(common_bb_symbols)
            processed_rsi_symbols = ChartUtils.remove_suffix_from_symbols(common_rsi_symbols)
            processed_intersected_symbols = ChartUtils.remove_suffix_from_symbols(intersected_symbols)

            for symbol in common_bb_symbols:
                # data = futures.coins_data[symbol]
                data = [all_coins_data[tf][symbol] for tf in self.timeframe_options if symbol in all_coins_data[tf]]
                # 단일로 처리해야함..
                # 몇시간 봉을 보여줄 것인가?
                # 이미지를 한번에 합쳐서 보여주는건...?
                data = TechnicalIndicators.add_technical_indicators(data[0])
                data['upper_band'], data['lower_band'] = TechnicalIndicators.calculate_bollinger_bands(data)
                ChartUtils.save_chart(data, symbol, "common")
                funding_rate = self.exchange.fetch_funding_rate(symbol)
                result['funding_rates'][symbol] = funding_rate
            
            result.update({
            'common_bb_symbols': list(processed_bb_symbols),
            'common_rsi_symbols': list(processed_rsi_symbols),
            'intersected_symbols': list(processed_intersected_symbols),
            'funding_rate': funding_rate})            
        else:
            print("No common Bollinger Band signals found across timeframes.")
        return result
    
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
                