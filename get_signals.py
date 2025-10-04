from indicators import rsi_signals, ema_signals, macd_signals
import pandas as pd

def get_signal(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    # RSI
    buy_rsi, sell_rsi = rsi_signals(
        data, 
        params['rsi_window'], 
        params['rsi_lower'], 
        params['rsi_upper']
    )

    # EMA
    buy_ema, sell_ema = ema_signals(
        data, 
        params['ema_short'], 
        params['ema_long']
    )

    # MACD
    buy_macd, sell_macd = macd_signals(
        data, 
        params['macd_fast'], 
        params['macd_slow'], 
        params['macd_signal']
    )

    # Votación (al menos 2 de 3)
    buy_signals = buy_rsi.astype(int) + buy_ema.astype(int) + buy_macd.astype(int)
    sell_signals = sell_rsi.astype(int) + sell_ema.astype(int) + sell_macd.astype(int)

    data['buy_signal'] = buy_signals >= 2
    data['sell_signal'] = sell_signals >= 2

    return data
