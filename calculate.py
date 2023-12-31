import pandas as pd

class TechnicalIndicators:
    @staticmethod
    def calculate_sma(df, window=20):
        return df['close'].rolling(window=window).mean()
    
    @staticmethod
    def calculate_ema(df, window=20):
        return df['close'].ewm(span=window, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df, window=14):
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_bollinger_bands(df, window=20, num_of_std=3):
        rolling_mean = df['close'].rolling(window=window).mean()
        rolling_std = df['close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return upper_band, lower_band
    
    @staticmethod
    def calculate_ichimoku(data):
        high = data['high']
        low = data['low']
        close = data['close']

        # 전환선 (Tenkan-sen)
        tenkan_sen = (high.rolling(window=9).max() + low.rolling(window=9).min()) / 2
        # 기준선 (Kijun-sen)
        kijun_sen = (high.rolling(window=26).max() + low.rolling(window=26).min()) / 2
        # 선행스팬 A (Senkou Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        # 선행스팬 B (Senkou Span B)
        senkou_span_b = ((high.rolling(window=52).max() + low.rolling(window=52).min()) / 2).shift(26)
        # 후행스팬 (Chikou Span)
        chikou_span = close.shift(-26)

        return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span

    @staticmethod
    def add_technical_indicators(df):
        df['SMA_20'] = TechnicalIndicators.calculate_sma(df, window=20)
        df['SMA_50'] = TechnicalIndicators.calculate_sma(df, window=50)
        df['RSI'] = TechnicalIndicators.calculate_rsi(df)
        df['EMA_7'] = TechnicalIndicators.calculate_ema(df, window=7)
        df['EMA_25'] = TechnicalIndicators.calculate_ema(df, window=25)
        df['EMA_99'] = TechnicalIndicators.calculate_ema(df, window=99)
        df['upper_band'], df['lower_band'] = TechnicalIndicators.calculate_bollinger_bands(df)
        return df