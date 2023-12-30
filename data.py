import ccxt
import pandas as pd
from tqdm import tqdm

class MarketData:
    @staticmethod
    def fetch_coins_data(exchange, symbols, timeframe, limit):
        coins_data = {}
        # 모든 시장 데이터 로드
        markets = exchange.load_markets()
        for symbol in tqdm(symbols):
            if symbol.endswith('/USDT') and symbol in markets:  # USDT 마켓이며 사용 가능한 심볼만 고려
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    coins_data[symbol] = df
                except Exception as e:
                    pass  # 여기서 오류 처리나 로깅을 할 수 있습니다.
        return coins_data