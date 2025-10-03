import pandas as pd
import ta

def rsi(data: pd.DataFrame, rsi_window: int, rsi_lower: int, rsi_upper: int) -> tuple:
    rsi_indicator = ta.momentum.RSIIndicator(data.Close, window=rsi_window)
    rsi_ind = rsi_indicator.rsi()

    buy_signal_rsi = rsi_ind < rsi_lower
    sell_signal_rsi = rsi_ind > rsi_upper

    #buy_signal_rsi = (rsi_ind < rsi_lower) & (rsi_ind.shift(1) >= rsi_lower)
    #sell_signal_rsi = (rsi_ind > rsi_upper) & (rsi_ind.shift(1) <= rsi_upper)

    return buy_signal_rsi, sell_signal_rsi


def macd(data: pd.DataFrame, fast: int, slow: int, signal: int) -> tuple:
    macd_indicator = ta.trend.MACD(data.Close, window_slow=slow, window_fast=fast, window_sign=signal)
    Macd = macd_indicator.macd()
    macd_signal = macd_indicator.macd_signal()

    buy_signal_macd = Macd > macd_signal
    sell_signal_macd = Macd < macd_signal

    #buy_signal_macd = (Macd > macd_signal) & (Macd.shift(1) <= macd_signal.shift(1))
    #sell_signal_macd = (Macd < macd_signal) & (Macd.shift(1) >= macd_signal.shift(1))

    return buy_signal_macd, sell_signal_macd


def bollinger_bands(data: pd.DataFrame, window: int, window_dev: float) -> tuple:
    bb_indicator = ta.volatility.BollingerBands(data.Close, window=window, window_dev=window_dev)
    bb_high = bb_indicator.bollinger_hband()
    bb_low = bb_indicator.bollinger_lband()
    

    buy_signal_bb = data.Close < bb_low
    sell_signal_bb = data.Close > bb_high

    #buy_signal_bb = (data.Close < bb_low) & (data.Close.shift(1) >= bb_low.shift(1))
    #sell_signal_bb = (data.Close > bb_high) & (data.Close.shift(1) <= bb_high.shift(1))

    return buy_signal_bb, sell_signal_bb

