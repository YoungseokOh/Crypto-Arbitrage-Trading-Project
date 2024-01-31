import pandas as pd
from calculate import TechnicalIndicators  # 필요한 경우 import 경로를 조정하세요.

class TradingCore:
    @staticmethod
    def find_bollinger_extremes(coins_data, num_of_std=2):
        extreme_bb_signals = []

        for symbol, df in coins_data.items():
            if not df.empty:  # 데이터프레임이 비어 있지 않은지 확인
                upper_band, lower_band = TechnicalIndicators.calculate_bollinger_bands(df, num_of_std=num_of_std)
                df['upper_band'] = upper_band
                df['lower_band'] = lower_band
                if df['close'].iloc[-1] > df['upper_band'].iloc[-1]:
                    extreme_bb_signals.append((symbol, 'Above Upper Band'))
                elif df['close'].iloc[-1] < df['lower_band'].iloc[-1]:
                    extreme_bb_signals.append((symbol, 'Below Lower Band'))

        return extreme_bb_signals

    
    @staticmethod
    def find_extreme_rsi(coins_data, rsi_window=14, overbought_threshold=70, oversold_threshold=30):
        extreme_rsi_signals = []
        
        for symbol, df in coins_data.items():
            if not df.empty:  # 데이터프레임이 비어 있지 않은지 확인
            # RSI 계산
                df['RSI'] = TechnicalIndicators.calculate_rsi(df, window=rsi_window)
                
                # 극단 RSI 조건 검사
                if df['RSI'].iloc[-1] > overbought_threshold:
                    extreme_rsi_signals.append((symbol, 'Overbought', df['RSI'].iloc[-1]))
                elif df['RSI'].iloc[-1] < oversold_threshold:
                    extreme_rsi_signals.append((symbol, 'Oversold', df['RSI'].iloc[-1]))

        return extreme_rsi_signals