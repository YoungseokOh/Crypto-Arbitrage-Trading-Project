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
        # For debugging
        # self.timeframe_options = ['1h']

    def fetch_top_gainers_and_losers(self):
        tickers = self.exchange.exchange.fetch_tickers()
        futures_tickers = {symbol: ticker for symbol, ticker in tickers.items() if symbol.endswith('USDT')}

        sorted_tickers = sorted(futures_tickers.items(), key=lambda x: x[1]['percentage'], reverse=True)
        top_5_gainers = sorted_tickers[:5]
        top_5_losers = sorted_tickers[-5:]

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

        bb_symbols = {symbol for symbol, _ in extreme_bb_signals}
        rsi_symbols = {symbol for symbol, _, _ in extreme_rsi_signals}
        return (coins_data, bb_symbols, rsi_symbols)

    def analyze_all_timeframes(self):
        print("Analyzing all timeframes...")
        result = {
            'common_bb_symbols': [], 
            'common_rsi_symbols': [], 
            'intersected_symbols': [],
            'funding_rates': {}
        }
        symbols = self.exchange.get_symbols()
        extreme_signals_per_timeframe = {
        timeframe: {'bb': set(), 'rsi': set()} for timeframe in self.timeframe_options
        }
        all_coins_data = {}
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(self.process_timeframe, timeframe, symbols): 
                       timeframe for timeframe in self.timeframe_options}
            for future in as_completed(futures):
                result_list = future.result()
                timeframe_data = result_list[0]
                bb_signals = result_list[1]
                rsi_signals = result_list[2]
                timeframe = futures[future]
                all_coins_data[timeframe] = timeframe_data

                extreme_signals_per_timeframe[timeframe]['bb'].update(bb_signals)
                extreme_signals_per_timeframe[timeframe]['rsi'].update(rsi_signals)
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total execution time: {total_time:.2f} seconds")

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
                symbols = self.exchange.get_symbols()
                limit = ChartUtils.calculate_limit(timeframe)
                coins_data = MarketData.fetch_coins_data(self.exchange.exchange, symbols, timeframe, limit)
                extreme_bb_signals = TradingCore.find_bollinger_extremes(coins_data)
                extreme_rsi_signals = TradingCore.find_extreme_rsi(coins_data)

                if extreme_bb_signals:
                    print("\nCoins with extreme Bollinger Band values:")
                    for symbol, position in extreme_bb_signals:
                        print(f"{symbol} is {position}")
                        data = coins_data[symbol]
                        data = TechnicalIndicators.add_technical_indicators(data)
                        data['upper_band'], data['lower_band'] = TechnicalIndicators.calculate_bollinger_bands(data)
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
                