from exchange import Exchange
from util import ChartUtils
from analysis import Analysis


def main():
    ChartUtils.initialize_chart_folder()
    exchange = Exchange()
    analysis = Analysis(exchange)
    # 선물 계좌 잔고 조회
    exchange.print_balance()

    print("Select the analysis mode:")
    print("1: Analyze all timeframes")
    print("2: Analyze a specific timeframe")
    
    while True:
        mode = input("Enter your choice (1 or 2): ")
        if mode == '1':
            analysis.analyze_all_timeframes()
            break
        elif mode == '2':
            analysis.analyze_specific_timeframe()
            break
        else:
            print("Invalid input. Please enter 1 or 2.")
    

if __name__ == "__main__":
    main()