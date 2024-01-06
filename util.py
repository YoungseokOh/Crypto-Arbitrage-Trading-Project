import os
import shutil
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd


class ChartUtils:
    @staticmethod
    def initialize_chart_folder(folder_path='charts'):
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)  # 폴더와 폴더 내 모든 파일을 삭제
        os.mkdir(folder_path)  # 새로운 폴더 생성
    
    @staticmethod
    def calculate_limit(timeframe):
        timeframe_limits = {
            '1h': 100,  # 1시간봉의 경우 최근 100개 데이터
            '2h': 200,
            '3h': 300,
            '4h': 400,
            '6h': 600,
            '8h': 800,
            '12h': 1200  # 12시간봉의 경우 최근 1200개 데이터
        }
        return timeframe_limits.get(timeframe, 100)  # 기본값은 100

    @staticmethod
    def save_chart(data, symbol, timeframe):
        # 데이터를 mplfinance 형식으로 변환
        data.index = pd.to_datetime(data['timestamp'], unit='ms')
        ohlcv = data[['open', 'high', 'low', 'close', 'volume']]

        # EMA 계산 (이미 계산되어 있다고 가정)
        ema7 = data['EMA_7']
        ema25 = data['EMA_25']
        ema99 = data['EMA_99']

        # 볼린저 밴드 계산 (이미 계산되어 있다고 가정)
        upper_band = data['upper_band']
        lower_band = data['lower_band']

        # RSI 계산 (이미 계산되어 있다고 가정)
        rsi = data['RSI']

        # EMA, 볼린저 밴드, RSI를 추가 플롯으로 설정
        apds = [mpf.make_addplot(ema7, color='fuchsia', width=0.7, label='EMA 7'),
                mpf.make_addplot(ema25, color='purple', width=0.7, label='EMA 25'),
                mpf.make_addplot(ema99, color='black', width=0.7, label='EMA 99'),
                mpf.make_addplot(upper_band, color='cyan', label='Upper Band'),
                mpf.make_addplot(lower_band, color='cyan', label='Lower Band'),
                mpf.make_addplot(rsi, panel=1, color='purple', ylabel='RSI', label='RSI')]

        # 캔들스틱 차트와 추가 플롯 그리기
        mpf.plot(ohlcv, type='line', style='yahoo', addplot=apds, title=f'{symbol} {timeframe}', 
                figratio=(10, 8), volume=True, panel_ratios=(6,3))

        # 폴더 확인 및 생성
        if not os.path.isdir('charts'):
            os.mkdir('charts')

        # 차트 저장
        chart_filename = f'charts/{symbol.replace("/", "_")}_{timeframe}.png'
        plt.savefig(chart_filename)
        plt.close()

    @staticmethod
    def save_ichimoku_chart(data, symbol, timeframe):
        # Ichimoku Cloud 구성 요소를 사용하여 추가 플롯 설정
        apds = [mpf.make_addplot(data['tenkan_sen'], color='blue', width=0.7, label='Tenkan Sen'),
                mpf.make_addplot(data['kijun_sen'], color='red', width=0.7, label='Kijun Sen'),
                mpf.make_addplot(data['senkou_span_a'], color='green', width=0.7, label='Senkou Span A', alpha=0.3),
                mpf.make_addplot(data['senkou_span_b'], color='orange', width=0.7, label='Senkou Span B', alpha=0.3),
                mpf.make_addplot(data['chikou_span'], color='purple', width=0.7, label='Chikou Span')]

        # 캔들스틱 차트와 Ichimoku Cloud 그리기
        mpf.plot(data, type='candle', style='yahoo', addplot=apds, title=f'{symbol} Ichimoku Chart {timeframe}', 
                figratio=(10, 8), volume=True)

        # 차트 저장 폴더 확인 및 생성
        if not os.path.isdir('charts'):
            os.mkdir('charts')

        # Ichimoku 차트 저장
        chart_filename = f'charts/{symbol.replace("/", "_")}_ichimoku_{timeframe}.png'
        plt.savefig(chart_filename)
        plt.close()

    @staticmethod
    def remove_suffix_from_symbols(symbols, suffix=':USDT'):
        """주어진 심볼 목록에서 특정 접미사를 제거합니다."""
        processed_symbols = [symbol.replace(suffix, '') for symbol in symbols]
        return processed_symbols