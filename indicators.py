import pandas as pd
import ta

def rsi_signals(data: pd.DataFrame, rsi_window: int, rsi_lower: int, rsi_upper: int):
    rsi_indicator = ta.momentum.RSIIndicator(data.Close, window=rsi_window)
    rsi = rsi_indicator.rsi()

    # Fijo
    buy_signal = rsi < rsi_lower
    sell_signal = rsi > rsi_upper

    # Cruce
    #buy_signal = (rsi < rsi_lower) & (rsi.shift(1) >= rsi_lower)
    #sell_signal = (rsi > rsi_upper) & (rsi.shift(1) <= rsi_upper)

    return buy_signal, sell_signal

def macd_signals(data: pd.DataFrame, fast_window: int, slow_window: int, signal_window: int):
    macd = ta.trend.MACD(data.Close, window_slow=slow_window, window_fast=fast_window, window_sign=signal_window)
    macd_l= macd.macd()
    signal_line = macd.macd_signal()

    # Fijo
    buy_signal = macd_l > signal_line
    sell_signal = macd_l < signal_line

    # Cruce
    #buy_signal = (macd_l > signal_line) & (macd_l.shift(1) <= signal_line.shift(1))
    #sell_signal = (macd_l < signal_line) & (macd_l.shift(1) >= signal_line.shift(1))

    return buy_signal, sell_signal

def ema_signals(data: pd.DataFrame, short_window: int, long_window: int):
    short_ema = ta.trend.EMAIndicator(data.Close, window=short_window).ema_indicator()
    long_ema = ta.trend.EMAIndicator(data.Close, window=long_window).ema_indicator()

    # Fijo
    buy_signal = short_ema > long_ema
    sell_signal = short_ema < long_ema

    # Cruce
    #buy_signal = (short_ema > long_ema) & (short_ema.shift(1) <= long_ema.shift(1))
    #sell_signal = (short_ema < long_ema) & (short_ema.shift(1) >= long_ema.shift(1))

    return buy_signal, sell_signal

def bollinger_signals(data: pd.DataFrame, window: int, n_std: float):
    bb = ta.volatility.BollingerBands(close=data.Close, window=window, window_dev=n_std)
    lower = bb.bollinger_lband()
    upper = bb.bollinger_hband()

    # Fijo: 
    buy_signal  = data.Close < lower
    sell_signal = data.Close > upper

    # Cruce (comentado): cruce de precio con bandas
    # buy_signal  = (data.Close < lower) & (data.Close.shift(1) >= lower.shift(1))
    # sell_signal = (data.Close > upper) & (data.Close.shift(1) <= upper.shift(1))

    return buy_signal, sell_signal

def stochastic_signals(data: pd.DataFrame, k_window: int , d_window: int, lower: int, upper: int):
    stoch = ta.momentum.StochasticOscillator(high=data.High, low=data.Low, close=data.Close,window=k_window, smooth_window=d_window)
    k = stoch.stoch()       
    d = stoch.stoch_signal()

    
    buy_signal  = k < lower
    sell_signal = k > upper

    # Cruce (comentado): %K cruza %D
    # buy_signal  = (k > d) & (k.shift(1) <= d.shift(1))
    # sell_signal = (k < d) & (k.shift(1) >= d.shift(1))

    return buy_signal, sell_signal

