from exchange import Exchange
from util import ChartUtils
from analysis import Analysis
from data import MarketData


def main():
    ChartUtils.initialize_chart_folder()
    exchange = Exchange()
    analysis = Analysis(exchange)
    analysis_functions = {
            'all_timeframes': analysis.analyze_all_timeframes,
            'top_coins': analysis.analyze_top_coins
            }
    # 선물 계좌 잔고 조회
    exchange.print_balance()

    while True:
        
        print("Select the analysis mode:")
        print("1: Analyze all timeframes")
        print("2: Analyze a specific timeframe")
        print("3: Run Telegram bot")
        print("4: Predict crypto coin")
        print("5: Save the ohlcv data for training")

        mode = input("Enter your choice : ")
        if mode == '1':
            analysis.analyze_all_timeframes()
            break
        elif mode == '2':
            analysis.analyze_specific_timeframe()
            break
        elif mode == '3':
            from telegram import run_telegram_bot
            run_telegram_bot(analysis_functions)
            break
        elif mode == '4':
            print('Not surpported!')
        elif mode == '5':
            limit = int(input("Enter the number of data points to fetch: "))
            MarketData.fetch_and_save_all_timeframes(exchange, limit)
        else:
            print("Invalid input. Please enter the number.")
    

if __name__ == "__main__":
    main()