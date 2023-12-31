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
        
        for symbol in usdt_pairs:
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                coins_data[symbol] = df
            except Exception as e:
                print(f"Error fetching data for {symbol}: {str(e)}")  # 오류 로깅
                
        return coins_data