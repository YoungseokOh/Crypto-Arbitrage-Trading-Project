import ccxt
from dotenv import load_dotenv
import os
import pandas as pd
from tqdm import tqdm


def calculate_bollinger_bands(df, window=20, num_of_std=2):
    rolling_mean = df['close'].rolling(window=window).mean()
    rolling_std = df['close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)
    return upper_band, lower_band


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
                pass
                # print(f"Error fetching data for {symbol}: {str(e)}")
    return coins_data


def find_bollinger_extremes(exchange, symbols, timeframe='1h', limit=100, window=20, num_of_std=3):
    coins_data = fetch_coins_data(exchange, symbols, timeframe, limit)
    extreme_signals = []

    for symbol, df in coins_data.items():
        upper_band, lower_band = calculate_bollinger_bands(df, window, num_of_std)
        df['upper_band'] = upper_band
        df['lower_band'] = lower_band

        if df['close'].iloc[-1] > df['upper_band'].iloc[-1]:
            extreme_signals.append((symbol, 'Above Upper Band'))
        elif df['close'].iloc[-1] < df['lower_band'].iloc[-1]:
            extreme_signals.append((symbol, 'Below Lower Band'))

    return extreme_signals

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
    exchange.load_markets()
    symbols = exchange.symbols
    extreme_signals = find_bollinger_extremes(exchange, symbols, timeframe)
    
    if extreme_signals:
        print("\nCoins with extreme Bollinger Band values:")
        for symbol, position in extreme_signals:
            print(f"{symbol} is {position}")
    else:
        print("\nNo coins with extreme Bollinger Band values at this time.")

if __name__ == "__main__":
    main()