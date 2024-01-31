# Exchange.py
import ccxt
from dotenv import load_dotenv
import os

class Exchange:
    def __init__(self):
        load_dotenv(verbose=True)
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.exchange = self.connect()
        
    def connect(self):
        exchange = ccxt.binance({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        return exchange
    
    def fetch_funding_rate(self, symbol):
        market = self.exchange.market(symbol)
        funding_rate = self.exchange.fetch_funding_rate(symbol)['fundingRate']
        percentage_rate = funding_rate * 100
        funding_rate = "{:.3f}%".format(percentage_rate)
        return funding_rate

    def fetch_balance(self):
        return self.exchange.fetch_balance()
    
    def load_markets(self):
        return self.exchange.load_markets()
    
    def get_symbols(self):
        return self.exchange.symbols
    
    def print_balance(self):
        balance = self.exchange.fetch_balance()
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
