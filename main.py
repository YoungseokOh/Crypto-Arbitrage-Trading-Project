import ccxt
import json
import time

class RiskFreeArbitrageBot:
    def __init__(self, exchange1, exchange2, symbols, amount, api_key1, secret_key1, api_key2, secret_key2):
        self.exchange1 = ccxt.binance({
            'apiKey': api_key1,
            'secret': secret_key1,
            'enableRateLimit': True,
        })

        self.exchange2 = ccxt.binance({
            'apiKey': api_key2,
            'secret': secret_key2,
            'enableRateLimit': True,
        })

        self.symbols = symbols
        self.amount = amount

        self.fee1 = self.get_exchange_fee(self.exchange1)
        self.fee2 = self.get_exchange_fee(self.exchange2)

    def get_exchange_fee(self, exchange):
        fees = exchange.load_account()['info']['makerCommission']
        return fees / 100.0

    def get_ticker_info(self, exchange, symbol):
        return exchange.fetch_ticker(symbol)

    def calculate_profit_margin(self, symbol):
        info1 = self.get_ticker_info(self.exchange1, symbol)
        info2 = self.get_ticker_info(self.exchange2, symbol)

        bid_price_1 = info1['bid']
        ask_price_2 = info2['ask']

        return ask_price_2 - bid_price_1

    def execute_arbitrage_trade(self):
        for symbol in self.symbols:
            profit_margin = self.calculate_profit_margin(symbol)

            if profit_margin > 0:
                print(f"무위험 차익거래 발생! 이윤: {profit_margin} - {symbol}")

                order1 = self.exchange1.create_market_buy_order(symbol, self.amount)
                order2 = self.exchange2.create_market_sell_order(symbol, self.amount)

                print("거래 성공!")
            else:
                print(f"무위험 차익거래 기회가 없습니다 - {symbol}")

def load_api_keys_from_json(file_path):
    try:
        with open(file_path, 'r') as file:
            api_keys = json.load(file)
        return api_keys.get('api_key1'), api_keys.get('secret_key1'), api_keys.get('api_key2'), api_keys.get('secret_key2')
    except FileNotFoundError:
        return None, None, None, None
    except json.JSONDecodeError:
        return None, None, None, None

if __name__ == "__main__":
    file_path = input("API Key 파일 경로를 입력하세요: ")
    api_key1, secret_key1, api_key2, secret_key2 = load_api_keys_from_json(file_path)

    if None in (api_key1, secret_key1, api_key2, secret_key2):
        print("API Key 파일을 올바르게 선택하세요.")
    else:
        symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT"]  # 여기에 원하는 암호화폐 쌍을 추가하십시오.

        bot = RiskFreeArbitrageBot(
            exchange1=None, exchange2=None, symbols=symbols, amount=0.001,
            api_key1=api_key1, secret_key1=secret_key1, api_key2=api_key2, secret_key2=secret_key2
        )

        while True:
            bot.execute_arbitrage_trade()
            time.sleep(60)  # 60초마다 거래 실행 (조정 가능)
