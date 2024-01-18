import os
import ccxt
import pandas as pd
from tqdm import tqdm

class MarketData:
    @staticmethod
    def fetch_coins_data(exchange, symbols, timeframe, limit):
        coins_data = {}
        # 모든 시장 데이터 로드
        markets = exchange.load_markets()
        
        # USDT 마켓에서 거래되는 심볼만 필터링
        usdt_pairs = [symbol for symbol in symbols if symbol.endswith('/USDT:USDT') and symbol in markets]
        
        for symbol in tqdm(usdt_pairs, leave=False):
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                coins_data[symbol] = df
            except Exception as e:
                print(f"Error fetching data for {symbol}: {str(e)}")  # 오류 로깅
        return coins_data

    @staticmethod
    def save_data(df, symbol, timeframe):
        formatted_symbol = symbol.replace(':USDT', '').replace('/', '_')
        directory = f"data/{timeframe}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_name = f"{directory}/{formatted_symbol}.csv"
        df.to_csv(file_name, index=False)

    @staticmethod
    def fetch_and_save_all_timeframes(exchange, limit):
        symbols = exchange.get_symbols()
        timeframes = ['5m', '15m', '30m', '1h']
        for timeframe in timeframes:
            print(f"Fetching and saving data for timeframe: {timeframe}")
            data = MarketData.fetch_coins_data(exchange.exchange, symbols, timeframe, limit)
            for symbol, df in data.items():
                MarketData.save_data(df, symbol, timeframe)
            print(f"{timeframe} ohlcv data is saved!")