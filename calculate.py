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
    def calculate_bollinger_bands(df, window=20, num_of_std=2):
        rolling_mean = df['close'].rolling(window=window).mean()
        rolling_std = df['close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return upper_band, lower_band
    
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