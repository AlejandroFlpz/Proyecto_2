from indicators import rsi, macd, bollinger_bands
import pandas as pd

def get_signals(data:pd.DataFrame, params:dict) -> pd.DataFrame:
    

    buy_rsi, sell_rsi = rsi(data, params['rsi_window'], params['rsi_lower'], params['rsi_upper'])
    buy_macd, sell_macd = macd(data, params['macd_fast'], params['macd_slow'], params['macd_signal'])
    buy_bb, sell_bb = bollinger_bands(data, params['bb_window'], params['bb_window_dev'])

    buy_signals = buy_rsi.astype(int) + buy_macd.astype(int) + buy_bb.astype(int)
    sell_signals = sell_rsi.astype(int) + sell_macd.astype(int) + sell_bb.astype(int)

    data['buy_signal'] = buy_signals >= 2
    data['sell_signal'] = sell_signals >= 2

    return data